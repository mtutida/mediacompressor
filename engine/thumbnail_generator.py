import subprocess, os
def generate_thumbnail(video_path,out_path):
    try:
        cmd=[
            "ffmpeg","-y","-i",video_path,
            "-vf","thumbnail=200,eq=brightness=0.05:saturation=1.15,scale=320:-1",
            "-frames:v","1",out_path
        ]
        subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return out_path if os.path.exists(out_path) else None
    except Exception:
        return None
