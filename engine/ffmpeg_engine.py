
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable


class EngineStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    CANCELLED = "CANCELLED"


@dataclass
class EngineResult:
    status: EngineStatus
    exit_code: int
    error_message: Optional[str] = None


class FFmpegEngine:

    def _get_duration_us(self, input_path: str) -> Optional[float]:
        try:
            probe_cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                input_path
            ]

            result = subprocess.run(
                probe_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )

            if result.returncode != 0:
                return None

            duration_seconds = float(result.stdout.strip())
            return duration_seconds * 1_000_000.0  # convert to microseconds

        except Exception:
            return None

    def execute(self, job, cancel_token=None, progress_callback: Optional[Callable[[float], None]] = None) -> EngineResult:

        duration_us = self._get_duration_us(job.input_path)

        cmd = [
            "ffmpeg",
            "-y",
            "-progress", "pipe:1",
            "-nostats",
            "-i", job.input_path,
            job.output_path
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )

            
            last_percent = -1.0

            while True:
                # Cooperative cancellation check
                if cancel_token and hasattr(cancel_token, "is_cancelled") and cancel_token.is_cancelled():
                    process.terminate()
                    process.wait()
                    return EngineResult(
                        status=EngineStatus.CANCELLED,
                        exit_code=-3,
                        error_message="Cancelled by request."
                    )

                line = process.stdout.readline()
                if not line:
                    break

                line = line.strip()

                if duration_us and line.startswith("out_time_ms="):
                    try:
                        current_us = float(line.split("=")[1])
                        percent = min(max(current_us / duration_us, 0.0), 1.0)

                        if percent > last_percent:
                            last_percent = percent
                            if progress_callback:
                                progress_callback(percent)
                    except Exception:
                        pass

                if line.startswith("progress=end"):
                    break

            process.wait()
            returncode = process.returncode

            if returncode > 2**31 - 1:
                returncode -= 2**32

            if returncode == 0:
                if progress_callback and last_percent < 1.0:
                    progress_callback(1.0)

                return EngineResult(
                    status=EngineStatus.SUCCESS,
                    exit_code=0,
                    error_message=None
                )
            else:
                return EngineResult(
                    status=EngineStatus.FAILURE,
                    exit_code=returncode,
                    error_message="FFmpeg execution failed."
                )

        except FileNotFoundError:
            return EngineResult(
                status=EngineStatus.FAILURE,
                exit_code=-1,
                error_message="FFmpeg or FFprobe not found."
            )
        except Exception as e:
            return EngineResult(
                status=EngineStatus.FAILURE,
                exit_code=-2,
                error_message=str(e)
            )
