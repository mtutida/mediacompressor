from interaction_model.contracts import IExecutionController, ISchedulerGateway

class CoreExecutionController(IExecutionController):

    def __init__(self, state_machine):
        self._state_machine = state_machine

    def start(self):
        self._state_machine.start_execution()

    def stop(self):
        self._state_machine.execution_finished()


class CoreSchedulerGateway(ISchedulerGateway):

    def __init__(self, scheduler):
        self._scheduler = scheduler

    def submit_job(self, job):
        self._scheduler.enqueue(job)
