
import subprocess
import os
import re
import shlex


class FFmpegCompressionEngine:
    """FFmpeg compression engine with real-time progress parsing.

    Architectural rules respected:
    - Engine NEVER mutates job.source_path or job.output_path
    - Engine only reads job data and reports progress
    - Progress parsed from FFmpeg stderr stream
    """

    TIME_REGEX = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

    def _get_duration_seconds(self, input_path):
        """Get media duration using ffprobe."""

        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_path
        ]

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            return float(result.stdout.strip())
        except Exception:
            return None

    def _parse_time_to_seconds(self, line):
        match = self.TIME_REGEX.search(line)
        if not match:
            return None

        h = int(match.group(1))
        m = int(match.group(2))
        s = float(match.group(3))

        return h * 3600 + m * 60 + s

    def process(self, job):

        input_path = job.source_path
        output_path = job.output_path

        if not input_path:
            raise Exception("Job sem source_path")

        if not output_path:
            raise Exception("Job sem output_path")

        duration = self._get_duration_seconds(input_path)

        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-vcodec", "libx264",
            "-crf", "28",
            output_path
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        last_progress = 0

        for line in process.stderr:

            seconds = self._parse_time_to_seconds(line)

            if seconds is not None and duration:

                progress = int((seconds / duration) * 100)

                progress = max(0, min(progress, 100))

                if progress != last_progress:

                    if hasattr(job, "set_progress"):
                        job.set_progress(progress)

                    last_progress = progress

        process.wait()

        if process.returncode != 0:
            raise Exception("FFmpeg terminou com erro")

        if hasattr(job, "set_progress"):
            job.set_progress(100)
