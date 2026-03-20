import json
import os
import shutil
import subprocess
import tempfile
from typing import Optional

# Compatibilidade com layouts diferentes da baseline.
try:
    from app.engine.ffmpeg_resolver import find_ffmpeg  # type: ignore
except Exception:
    try:
        from app.ffmpeg_resolver import find_ffmpeg  # type: ignore
    except Exception:
        try:
            from app.core.ffmpeg_resolver import find_ffmpeg  # type: ignore
        except Exception:
            def find_ffmpeg():
                candidates = [
                    os.path.join(os.getcwd(), "ffmpeg.exe"),
                    os.path.join(os.getcwd(), "bin", "ffmpeg.exe"),
                ]
                for p in candidates:
                    if os.path.exists(p):
                        return p
                return shutil.which("ffmpeg")


def _find_ffprobe(ffmpeg_path: Optional[str]) -> Optional[str]:
    if ffmpeg_path:
        base = os.path.dirname(ffmpeg_path)
        name = os.path.basename(ffmpeg_path).lower()
        probe_name = "ffprobe.exe" if name.endswith(".exe") else "ffprobe"
        candidate = os.path.join(base, probe_name)
        if os.path.exists(candidate):
            return candidate
    return shutil.which("ffprobe")


def estimate_size_crf(path: str, crf: int = 28, sample_offset: int = 30, sample_duration: int = 8) -> Optional[int]:
    """
    Estimador estável por amostra curta.
    - Mantém fallback externo se qualquer etapa falhar.
    - Não levanta exceção para a UI.
    """
    tmp_path = None
    try:
        ffmpeg = find_ffmpeg()
        ffprobe = _find_ffprobe(ffmpeg)

        if not ffmpeg or not ffprobe:
            return None

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp_path = tmp.name
        tmp.close()

        cmd = [
            ffmpeg,
            "-y",
            "-ss", str(sample_offset),
            "-t", str(sample_duration),
            "-i", path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", str(crf),
            "-c:a", "copy",
            tmp_path,
        ]
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=120,
        )

        probe_cmd = [
            ffprobe, "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            tmp_path,
        ]
        r = subprocess.run(probe_cmd, capture_output=True, text=True, check=False, timeout=30)
        data = json.loads(r.stdout or "{}")
        if "format" not in data:
            return None

        sample_size = int(float(data["format"]["size"]))
        sample_len = float(data["format"]["duration"])
        if sample_len <= 0:
            return None
        sample_bitrate = (sample_size * 8) / sample_len

        probe_src = [
            ffprobe, "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            path,
        ]
        r2 = subprocess.run(probe_src, capture_output=True, text=True, check=False, timeout=30)
        d = json.loads(r2.stdout or "{}")
        if "format" not in d:
            return None

        full_duration = float(d["format"]["duration"])
        original_size = int(float(d["format"]["size"]))
        if full_duration <= 0:
            return None
        original_bitrate = (original_size * 8) / full_duration

        final_bitrate = original_bitrate * 0.95 if sample_bitrate > original_bitrate else sample_bitrate
        return int((final_bitrate * full_duration) / 8)

    except Exception:
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
