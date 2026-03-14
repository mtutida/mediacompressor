class JobController:

    def __init__(self, model):
        self.model = model

    def enqueue(self, job):
        if hasattr(self.model, "add_job"):
            self.model.add_job(job)
