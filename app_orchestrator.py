from interaction_model.state_machine import StateMachine
from interaction_model.shutdown_controller import ShutdownController
from core.engine_stub import StubCompressionEngine
from core.pipeline import ExecutionPipeline
from core.contracts import CoreExecutionController, CoreSchedulerGateway
from core.job import Job
from core.compression_job import CompressionJob
from scheduler.scheduler import Scheduler
from app.viewmodels.ready_item_view_model import ReadyItemViewModel


class ApplicationOrchestrator:

    def __init__(self, max_workers=1):
        self.state_machine = StateMachine()
        self.engine = StubCompressionEngine()
        self.pipeline = ExecutionPipeline(self.engine)
        self.scheduler = Scheduler(self.pipeline, max_workers=max_workers)

        self.core_exec = CoreExecutionController(self.state_machine)
        self.scheduler_gateway = CoreSchedulerGateway(self.scheduler)
        self.shutdown_controller = ShutdownController(self.state_machine)

        self._job_registry = {}

    def bootstrap(self):
        self.state_machine.initialize_complete()
        self.scheduler.start()

    def submit_job(self, job_or_name, task_callable=None):
        if isinstance(job_or_name, Job):
            job = job_or_name
        else:
            job = Job(name=job_or_name, task=task_callable)

        self._job_registry[job.job_id] = job
        self.scheduler_gateway.submit_job(job)
        return job

    # --- Phase 12.1.D ---
    def submit_ready_item(self, view_model: ReadyItemViewModel) -> Job:
        if not isinstance(view_model, ReadyItemViewModel):
            raise TypeError("Expected ReadyItemViewModel")

        job = CompressionJob(
            name=view_model.source_path,
            input_path=view_model.source_path,
            output_path=view_model.output_path,
            preset=view_model.preset_snapshot,
            job_id=view_model.stable_id
        )

        return self.submit_job(job)

    def list_jobs(self):
        return list(self._job_registry.values())

    def get_job(self, job_id):
        return self._job_registry.get(job_id)

    def cancel_job(self, job_id):
        job = self._job_registry.get(job_id)
        if job:
            job.request_cancel()

    def get_job_snapshot(self, job_id):
        job = self._job_registry.get(job_id)
        if job:
            return job.create_snapshot()
        return None

    def shutdown(self):
        self.shutdown_controller.request_shutdown()
        self.scheduler.stop()