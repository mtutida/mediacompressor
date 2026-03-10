from dataclasses import dataclass
from uuid import UUID
from typing import Optional
from .job import JobStatus


@dataclass(frozen=True)
class JobSnapshot:
    job_id: UUID
    name: str
    status: JobStatus
    progress: float
    error: Optional[str]
