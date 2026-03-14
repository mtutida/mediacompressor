from dataclasses import dataclass, field
from uuid import UUID, uuid4
from enum import Enum, auto
from typing import Callable, Optional
import threading


class JobStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class Job:
    name: str
    task: Callable[[], None]
    job_id: UUID = field(default_factory=uuid4)
    status: JobStatus = field(default=JobStatus.PENDING)
    error: Optional[str] = field(default=None)

    _cancel_requested: bool = field(default=False, init=False, repr=False)
    _cancel_lock: threading.Lock = field(
        default_factory=threading.Lock, init=False, repr=False
    )

    _progress: float = field(default=0.0, init=False, repr=False)
    _progress_lock: threading.Lock = field(
        default_factory=threading.Lock, init=False, repr=False
    )

    def request_cancel(self) -> None:
        with self._cancel_lock:
            self._cancel_requested = True

    def is_cancel_requested(self) -> bool:
        with self._cancel_lock:
            return self._cancel_requested

    def set_progress(self, value: float) -> None:
        if value < 0:
            value = 0.0
        if value > 100:
            value = 100.0
        with self._progress_lock:
            self._progress = value

    def get_progress(self) -> float:
        with self._progress_lock:
            return self._progress


    def create_snapshot(self):
        from .job_snapshot import JobSnapshot
        with self._progress_lock:
            progress = self._progress
        return JobSnapshot(
            job_id=self.job_id,
            name=self.name,
            status=self.status,
            progress=progress,
            error=self.error
        )


    def persist_snapshot(self, repository):
        snapshot = self.create_snapshot()
        repository.save(snapshot)
