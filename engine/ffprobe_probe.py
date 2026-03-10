
import subprocess, json

def probe(path):
    try:
        cmd = [
            "ffprobe",
            "-v","quiet",
            "-print_format","json",
            "-show_streams",
            "-show_format",
            path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)

        streams = data.get("streams", [])
        if not streams:
            return None

        codec="?" 
        width="?" 
        height="?" 
        fps="?" 
        duration="?" 
        container="?"

        for s in data.get("streams",[]):
            if s.get("codec_type") == "video":
                codec = s.get("codec_name","?")
                width = s.get("width","?")
                height = s.get("height","?")
                r = s.get("r_frame_rate","0/1")
                try:
                    num,den = r.split("/")
                    fps = str(round(float(num)/float(den),2))
                except:
                    fps="?"

        fmt=data.get("format",{})
        if "duration" in fmt:
            try:
                d=float(fmt["duration"])
                m=int(d//60)
                s=int(d%60)
                duration=f"{m:02d}:{s:02d}"
            except:
                duration="?"

        if "format_name" in fmt:
            container=fmt["format_name"].split(",")[0]

        resolution=f"{width}x{height}"

        return codec,resolution,fps,duration,container

    except Exception:
        return None
