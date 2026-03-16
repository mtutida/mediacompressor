
from app.interaction_model.event_bridge import event_bridge
from app.core.ffmpeg_engine import FFmpegCompressionEngine
from app.core.output_naming import generate_output_path

import threading
from collections import deque
from app.engine.cancel_token import CancelToken


class RunController:

    def __init__(self):
        self.engine = FFmpegCompressionEngine()

        # active jobs
        self.jobs = {}

        # cancel tokens
        self.tokens = {}

        # queue
        self._queue = deque()
        self._queue_lock = threading.Lock()
        self._queue_event = threading.Event()

        # worker thread
        self._worker = threading.Thread(
            target=self._worker_loop,
            daemon=True
        )
        self._worker.start()

        event_bridge.subscribe(self._on_event)

    # ------------------------------------------------

    def _on_event(self, event_type, payload):

        if event_type == "job_run_requested":
            job = payload if not isinstance(payload, dict) else payload.get("job")
            if job:

                if getattr(job, "status", None) in ("PROCESSING", "RUNNING"):
                    return

                self._prepare_job(job)
                self._enqueue_job(job)

        elif event_type == "cancel_all_requested":

            # cancel running job
            for t in list(self.tokens.values()):
                t.cancel()

            # cancel queued jobs
            with self._queue_lock:
                while self._queue:
                    job = self._queue.popleft()
                    job.status = "CANCELLED"
                    job.progress = 0
                    event_bridge.emit("job_updated", {"job": job})

        elif event_type == "job_cancel_requested":

            job = payload if not isinstance(payload, dict) else payload.get("job")
            token = self.tokens.get(id(job))

            if token:
                token.cancel()
                return

            # if job is queued remove from queue
            with self._queue_lock:
                try:
                    self._queue.remove(job)
                    job.status = "CANCELLED"
                    job.progress = 0
                    event_bridge.emit("job_updated", {"job": job})
                except ValueError:
                    pass

        elif event_type == "configuration_changed":
            self._refresh_output_paths()

    # ------------------------------------------------

    def _refresh_output_paths(self):
        for job in list(self.jobs.values()):
            if hasattr(job, "source_path"):
                job.output_path = generate_output_path(job.source_path)
                event_bridge.emit("job_updated", {"job": job})

    # ------------------------------------------------

    def _prepare_job(self, job):

        if not hasattr(job, "name"):
            job.name = getattr(job, "file_name", getattr(job, "source_path", "job"))

        # reset state for retry
        job.error = None
        job.progress = 0

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

    # ------------------------------------------------

    def _enqueue_job(self, job):

        job.status = "QUEUED"
        event_bridge.emit("job_updated", {"job": job})

        with self._queue_lock:
            self._queue.append(job)
            self._queue_event.set()

    # ------------------------------------------------

    def _worker_loop(self):

        while True:

            self._queue_event.wait()

            while True:

                with self._queue_lock:
                    if not self._queue:
                        self._queue_event.clear()
                        break

                    job = self._queue.popleft()

                self._start_job(job)

    # ------------------------------------------------

    def _start_job(self, job):

        job.output_path = generate_output_path(job.source_path)
        event_bridge.emit("job_updated", {"job": job})

        token = CancelToken()
        self.tokens[id(job)] = token
        self.jobs[id(job)] = job

        self._execute_job(job, token)

    # ------------------------------------------------

    def _cleanup_job(self, job):
        self.tokens.pop(id(job), None)
        self.jobs.pop(id(job), None)

    # ------------------------------------------------

    def _execute_job(self, job, token):

        try:

            job.status = "PROCESSING"
            event_bridge.emit("job_updated", {"job": job})

            self.engine.process(job, cancel_token=token)

            job.progress = 100
            job.status = "DONE"

            event_bridge.emit("job_updated", {"job": job})
            event_bridge.emit("job_finished", {"job": job})

        except Exception as e:

            job.status = "CANCELLED" if "cancelled" in str(e).lower() else "FAILED"
            job.error = str(e)

            if "cancelled" in str(e).lower():
                job.progress = 0
                event_bridge.emit("job_updated", {"job": job})
            else:
                event_bridge.emit("job_failed", {
                    "job": job,
                    "error": str(e)
                })

        finally:
            self._cleanup_job(job)
