import subprocess

def check_ffmpeg():
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    if result.returncode == 0:
        return
    raise Exception("FFmpeg is not installed.")