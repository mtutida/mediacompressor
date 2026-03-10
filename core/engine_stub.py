from .job import JobStatus
from .engine_contract import ICompressionEngine
import time


class StubCompressionEngine(ICompressionEngine):

    def process(self, job):
        try:
            if job.is_cancel_requested():
                job.status = JobStatus.CANCELLED
                print(f"[ENGINE] Job cancelled before start: {job.name}")
                return

            job.status = JobStatus.RUNNING
            job.set_progress(0)
            print(f"[ENGINE] Running job: {job.name}")

            # Simulated progressive work
            for step in range(1, 5):
                if job.is_cancel_requested():
                    job.status = JobStatus.CANCELLED
                    print(f"[ENGINE] Job cancelled during execution: {job.name}")
                    return

                time.sleep(0.5)
                job.set_progress(step * 25)
                print(f"[ENGINE] Progress: {job.get_progress()}%")

            job.task()

            job.set_progress(100)
            job.status = JobStatus.COMPLETED
            print(f"[ENGINE] Completed job: {job.name}")

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            print(f"[ENGINE] Job failed: {job.name} -> {job.error}")
