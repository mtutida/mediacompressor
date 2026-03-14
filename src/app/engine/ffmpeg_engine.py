
import subprocess
import os


class FFmpegCompressionEngine:
    """Stable FFmpeg engine implementation."""

    def process(self, job):

        input_path = getattr(job, "source_path", None)

        if not input_path or not os.path.exists(input_path):
            raise Exception("Arquivo de entrada inválido")

        base_dir = os.path.dirname(input_path)
        name, ext = os.path.splitext(os.path.basename(input_path))

        output_path = os.path.join(base_dir, f"{name}_compressed{ext}")
        job.output_path = output_path

        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-c:v", "libx264",
            "-crf", "28",
            "-preset", "medium",
            "-c:a", "copy",
            output_path
        ]

        # Run ffmpeg without pipes to avoid deadlocks
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if result.returncode != 0:
            raise Exception("FFmpeg falhou durante a compressão")

        if hasattr(job, "set_progress"):
            job.set_progress(100)
