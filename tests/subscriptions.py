from locust import TaskSet, task


class SubscriptionTasks(TaskSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_client = args[0]

    def on_start(self):
        pass

    @task
    def subscribeNewBlock(self):
        self.custom_client.send(
            "subscribeNewBlock",

        )

    @task
    def subscribeNewEvent(self):
        self.custom_client.send(
            "subscribeNewEvent",

        )

    @task
    def subscribeNewExtrinsic(self):
        self.custom_client.send(
            "subscribeNewExtrinsic",

        )
        
    @task
    def subscribeNewTransfer(self):
        self.custom_client.send(
            "subscribeNewTransfer",

        )
        
    @task
    def subscribeNewLog(self):
        self.custom_client.send(
            "subscribeNewLog",

        )