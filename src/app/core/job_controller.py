class JobController:

    def __init__(self, model, scheduler):
        self.model = model
        self.scheduler = scheduler

    def enqueue(self, job):

        # adiciona na UI
        if hasattr(self.model, "add_job"):
            self.model.add_job(job)

        # envia para execução
        if self.scheduler:
            self.scheduler.enqueue(job)
