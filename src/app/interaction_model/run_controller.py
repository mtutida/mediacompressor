
from app.interaction_model.event_bridge import event_bridge
from app.core.ffmpeg_engine import FFmpegCompressionEngine
import threading


class RunController:

    def __init__(self):
        self.engine = FFmpegCompressionEngine()
        event_bridge.subscribe(self._on_event)

    def _on_event(self, event_type, payload):

        if event_type == "job_run_requested":
            job = payload if not isinstance(payload, dict) else payload.get("job")
            if job:
                self._prepare_job(job)
                self._start_job(job)

    # ---------------------------------------------------------
    # Compatibility layer for UI job objects
    # ---------------------------------------------------------

    def _prepare_job(self, job):

        if not hasattr(job, "name"):
            job.name = getattr(job, "file_name", getattr(job, "source_path", "job"))

        if not hasattr(job, "error"):
            job.error = None

        if not hasattr(job, "progress"):
            job.progress = 0

        # REAL progress bridge
        def set_progress(v):
            job.progress = int(v)

            event_bridge.emit("job_progress", {
                "job": job,
                "progress": job.progress
            })

        job.set_progress = set_progress

        if not hasattr(job, "get_progress"):
            job.get_progress = lambda: getattr(job, "progress", 0)

        if not hasattr(job, "is_cancel_requested"):
            job.is_cancel_requested = lambda: False

    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------

    def _start_job(self, job):

        t = threading.Thread(
            target=self._execute_job,
            args=(job,),
            daemon=True
        )
        t.start()

    def _execute_job(self, job):

        try:

            job.status = "PROCESSING"
            event_bridge.emit("job_updated", {"job": job})

            self.engine.process(job)

            job.progress = 100
            job.status = "DONE"

            event_bridge.emit("job_finished", {"job": job})

        except Exception as e:

            job.status = "FALHA"
            job.error = str(e)

            event_bridge.emit("job_failed", {
                "job": job,
                "error": str(e)
            })
