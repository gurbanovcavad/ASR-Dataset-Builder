import subprocess
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from typing import Optional
from pathlib import Path

class DownloadError(Exception):
    pass

class TransientDownloadError(Exception):
    pass

class Downloader:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=2, max=10),
        retry=retry_if_exception_type(TransientDownloadError)
    )
    def download_video(self, url: str, video_id: str) -> Optional[Path]:
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        output_template = self.temp_dir / f"{video_id}_%(ext)s"
        cmd = [
            "yt-dlp",
            "-f", "bestaudio/best",
            "--extract-audio",
            "--audio-format", "best",
            "--no-playlist",
            "--no-warnings",
            "-o", str(output_template),
            url
        ]
        
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300
            )
            files = list(self.temp_dir.glob(f"{video_id}_*"))
            if files:
                return files[0]
            return None
        
        except subprocess.TimeoutExpired:
            raise TransientDownloadError(f"Download timeout for {url}")
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.lower()
            if "http error 429" in stderr or "timeout" in stderr or "http error 5" in stderr or "network" in stderr:
                raise TransientDownloadError(f"Transient error: {e.stderr}")
            else:
                raise DownloadError(f"Permanent error: {e.stderr}")