
import subprocess
import re
from .engine_contract import ICompressionEngine
from .job import JobStatus


class FFmpegCompressionEngine(ICompressionEngine):

    _time_regex = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

    def _get_duration_seconds(self, input_path: str) -> float:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())

    def process(self, job):
        try:
            if job.is_cancel_requested():
                job.status = JobStatus.CANCELLED
                return

            job.status = JobStatus.RUNNING
            job.set_progress(0)

            input_path, output_path = job.task()

            duration = self._get_duration_seconds(input_path)

            cmd = [
                "ffmpeg",
                "-y",
                "-i", input_path,
                "-progress", "pipe:1",
                "-nostats",
                output_path
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                if job.is_cancel_requested():
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    job.status = JobStatus.CANCELLED
                    return

                match = self._time_regex.search(line)
                if match and duration > 0:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = float(match.group(3))
                    current_time = hours * 3600 + minutes * 60 + seconds
                    percent = (current_time / duration) * 100
                    job.set_progress(percent)

            process.wait()

            if process.returncode == 0:
                job.set_progress(100)
                job.status = JobStatus.COMPLETED
            else:
                job.status = JobStatus.FAILED

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
