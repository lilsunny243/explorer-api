import time
import json
import gevent
import websocket

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from locust import events, User

from broadcaster import Broadcast

from app.session import engine
from app.models.explorer import Block

from tests.settings import settings
from tests.subscriptions import SubscriptionTasks


broadcast = Broadcast(settings.BROADCAST_URI)
Session = sessionmaker(engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class SocketClient(object):

    def __init__(self, host):
        self.host = host
        self.subscriptions = {
            "subscribeNewBlock": {
                "query": "subscription { subscribeNewBlock {number, hash} }",
                "connection_count": settings.SUBSCRIBE_NEW_BLOCK_CONNECTIONS,
                "connections": []
            },
            "subscribeNewEvent": {
                "query": "subscription { subscribeNewEvent {blockNumber, eventIdx, event} }",
                "connection_count": settings.SUBSCRIBE_NEW_EVENT_CONNECTIONS,
                "connections": []
            },
            "subscribeNewExtrinsic": {
                "query": "subscription { subscribeNewExtrinsic {blockNumber, extrinsicIdx, hash} }",
                "connection_count": settings.SUBSCRIBE_NEW_EXTRINSIC_CONNECTIONS,
                "connections": []
            },
            "subscribeNewTransfer": {
                "query": "subscription { subscribeNewTransfer {blockNumber, eventIdx, blockDatetime, fromMultiAddressAccountId, toMultiAddressAccountId} }",
                "connection_count": settings.SUBSCRIBE_NEW_TRANSFER_CONNECTIONS,
                "connections": []
            },
            "subscribeNewLog": {
                "query": "subscription { subscribeNewLog {blockNumber, logIdx} }",
                "connection_count": settings.SUBSCRIBE_NEW_LOG_CONNECTIONS,
                "connections": []
            },
        }

        #TODO!!!!!!!!!!!!!!!!!!!!!!!!
        #from app import app
        # BaseModel.metadata.drop_all(bind=session.engine)
        # BaseModel.metadata.create_all(bind=session.engine)
        # create_blocks(session)

        with session_scope() as db:
            blocks = db.query(Block).limit(settings.TEST_SUBSCRIPTION_NR_BLOCKS)
            import pdb;pdb.set_trace()
            self.AVAILABLE_BLOCKS = list(blocks)

        self.connect()

    def connect(self):
        for subscription_key in self.subscriptions.keys():
            for subscription_nr in self.subscriptions[subscription_key]["connection_count"]:
                ws = websocket.WebSocket()
                ws.settimeout(settings.TEST_CONNECTION_WAIT_TIME)
                ws.connect(self.host)

                ws_req = json.dumps({
                    "type": settings.GQL_START,
                    "id": subscription_key,
                    "payload": {
                        "query": self.subscriptions[subscription_key]["query"],
                        "operationName": None,
                    },
                })
                ws.send(ws_req)
                self.subscriptions[subscription_key]["connections"].append(ws)

    def on_start(self):
        #self.send('GQL_CONNECTION_INIT', '{"type": "' + settings.GQL_CONNECTION_INIT + '" }', False)
        pass

    def on_stop(self):
        for subscription_key in self.subscriptions.keys():
            for subscription_nr in self.subscriptions[subscription_key]["connection_count"]:
                self.subscriptions[subscription_key]["connections"][subscription_nr].close()

    def trigger_new_block(self):
        block_id = self.AVAILABLE_BLOCKS.pop()
        broadcast.publish(channel=f"{settings.CHAIN_ID}-last-block", message=f"{block_id}")

    def send(self, name, payload, parse=True):
        start_at = time.time()

        if parse:
            ws_req = json.dumps({
                "type": settings.GQL_START,
                "id": name,
                "payload": {
                    "query": payload,
                    "operationName": None,
                },
            })
        else:
            ws_req = payload

        self.ws.send(ws_req)
        g = gevent.spawn(self.ws.recv)
        result = g.get(block=True, timeout=30)

        if not result:
            events.request_failure.fire(
                request_type='WEBSOCKET',
                exception='Empty response',
                name=name,
                response_time=int((time.time() - start_at)),
                response_length=len(result),
            )

        res = json.loads(result)

        if (time.time() - start_at) > 1:
            events.request_failure.fire(
                request_type='WEBSOCKET',
                exception='Response Time was more than 1 second',
                name=name,
                response_time=int((time.time() - start_at)),
                response_length=len(result),
            )

        if res["type"] == "error":
            events.request_failure.fire(
                request_type='WEBSOCKET',
                exception=result,
                name=name,
                response_time=int((time.time() - start_at)),
                response_length=len(result),
            )
        else:
            events.request_success.fire(
                request_type='WEBSOCKET',
                name=name,
                response_time=int((time.time() - start_at)),
                response_length=len(result),
            )
        return res


class WSUser(User):
    tasks = [SubscriptionTasks]

    def __init__(self, *args, **kwargs):
        super(WSUser, self).__init__(*args, **kwargs)
        self.client = SocketClient(f"ws://{settings.SERVER_ADDR}:{settings.SERVER_PORT}{settings.WS_MOUNT}")

    def send(self, *args, **kwargs):
        self.client.send(*args, **kwargs)

    def on_start(self):
        self.client.on_start()

    def on_stop(self):
        self.client.on_stop()
