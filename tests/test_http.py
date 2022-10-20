import os
import time

from locust.contrib.fasthttp import FastHttpUser

from tests.settings import settings
from tests.queries import QueryTasks


class HttpClient(FastHttpUser):
    tasks = [QueryTasks]

    def __init__(self, *args, **kwargs):
        self.host = f"http://{settings.SERVER_ADDR}:{settings.SERVER_PORT}{settings.HTTP_MOUNT}"
        super().__init__(*args, **kwargs)

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        pass

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        pass

    def send(self, name, payload):
        start_at = time.time()
        with self.client.post(
                self.host,
                name=name,
                json={"query": payload},
                catch_response=True) as response:

            if response.status_code != 200:
                response.failure("Incorrect Response Code for Latest Query")
            if (time.time() - start_at) > 1:
               response.failure("Response Time was more than 1 second")
