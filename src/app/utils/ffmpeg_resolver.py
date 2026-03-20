import os, sys, shutil

def get_base():
    return getattr(sys, '_MEIPASS', os.getcwd())

def find_ffmpeg():
    paths = [
        os.path.join(get_base(), "ffmpeg.exe"),
        os.path.join(get_base(), "bin", "ffmpeg.exe"),
        os.path.join(os.getcwd(), "ffmpeg.exe")
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return shutil.which("ffmpeg")

def require_ffmpeg():
    path = find_ffmpeg()
    if not path:
        raise RuntimeError("FFmpeg não encontrado")
    return path
