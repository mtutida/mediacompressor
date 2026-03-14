from app.interaction_model.event_bridge import event_bridge

import threading
import queue

from app.engine.cancel_token import CancelToken


class Scheduler:
    """Scheduler v2 with cancel token and progress support"""

    def __init__(self, pipeline, max_workers=1):
        self._queue = queue.Queue()
        self._pipeline = pipeline
        self._max_workers = max_workers

        self._workers = []
        self._running = False

        self._active_jobs = {}
        self._lock = threading.Lock()
        # using global event_bridge

    def start(self):
        if self._running:
            return

        self._running = True

        for _ in range(self._max_workers):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()
            self._workers.append(t)

    def stop(self):
        self._running = False

        for _ in self._workers:
            self._queue.put(None)

        for t in self._workers:
            t.join()

    def enqueue(self, job):
        self._queue.put(job)
        event_bridge.emit('job_enqueued', {'job': job})

    def cancel(self, job_id):
        with self._lock:
            token = self._active_jobs.get(job_id)

        if token:
            token.cancel()

    def _on_progress(self, job, percent):
        if hasattr(job, "set_progress"):
            job.set_progress(percent * 100)

    def _worker_loop(self):

        while True:

            job = self._queue.get()

            if job is None:
                break

            cancel_token = CancelToken()

            job_id = getattr(job, "id", id(job))

            with self._lock:
                self._active_jobs[job_id] = cancel_token

            try:

                result = self._pipeline.execute(
                    job,
                    cancel_token=cancel_token,
                    progress_callback=lambda p: self._on_progress(job, p)
                )

                if hasattr(job, "set_result"):
                    job.set_result(result)
                event_bridge.emit('job_finished', {'job': job, 'result': result})

            except Exception as e:

                if hasattr(job, "set_error"):
                    job.set_error(str(e))
                event_bridge.emit('job_failed', {'job': job, 'error': str(e)})

            finally:

                with self._lock:
                    self._active_jobs.pop(job_id, None)

                self._queue.task_done()
