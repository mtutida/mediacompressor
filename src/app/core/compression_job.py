
from typing import Optional
from uuid import UUID
from .job import Job


class CompressionJob(Job):

    def __init__(
        self,
        name: str,
        input_path: str,
        output_path: str,
        video_codec: str = "libx264",
        audio_codec: str = "aac",
        video_bitrate: Optional[str] = None,
        audio_bitrate: Optional[str] = None,
        preset: Optional[str] = None,
        job_id: Optional[UUID] = None,
    ):
        # task exigida por Job (contrato preservado)
        def _task():
            return input_path, output_path

        if job_id is not None:
            super().__init__(name=name, task=_task, job_id=job_id)
        else:
            super().__init__(name=name, task=_task)

        self.input_path = input_path
        self.output_path = output_path
        self.video_codec = video_codec
        self.audio_codec = audio_codec
        self.video_bitrate = video_bitrate
        self.audio_bitrate = audio_bitrate
        self.preset = preset
