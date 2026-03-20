
import subprocess, json, tempfile, os

def estimate_size_crf(path, crf=28, sample_offset=30, sample_duration=8):
    '''
    Stable CRF size estimator.

    Strategy
    --------
    1. Encode small representative sample
    2. Measure sample bitrate
    3. Compare with original bitrate
    4. Prevent CRF from increasing bitrate on already compressed videos
    '''

    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp.close()

        # --- encode representative sample ---
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(sample_offset),
            "-t", str(sample_duration),
            "-i", path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", str(crf),
            "-c:a", "copy",
            tmp.name
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # --- probe sample ---
        probe_cmd = [
            "ffprobe","-v","quiet",
            "-print_format","json",
            "-show_format",
            tmp.name
        ]

        r = subprocess.run(probe_cmd, capture_output=True, text=True)
        data = json.loads(r.stdout)

        sample_size = int(data["format"]["size"])
        sample_duration = float(data["format"]["duration"])

        sample_bitrate = (sample_size * 8) / sample_duration

        # --- probe original ---
        probe_src = [
            "ffprobe","-v","quiet",
            "-print_format","json",
            "-show_format",
            path
        ]

        r2 = subprocess.run(probe_src, capture_output=True, text=True)
        d = json.loads(r2.stdout)

        full_duration = float(d["format"]["duration"])
        original_size = int(d["format"]["size"])

        original_bitrate = (original_size * 8) / full_duration

        # --- bitrate decision logic ---
        if sample_bitrate > original_bitrate:
            final_bitrate = original_bitrate * 0.95
        else:
            final_bitrate = sample_bitrate

        estimated_bytes = int((final_bitrate * full_duration) / 8)

        os.remove(tmp.name)

        return estimated_bytes

    except Exception:
        return None
