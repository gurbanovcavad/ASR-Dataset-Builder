import subprocess
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional
from pathlib import Path
import tempfile

class DownloadError(Exception):
    pass

class Downloader:
    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = temp_dir or Path(tempfile.gettempdir()) / "asr_scraper"
        self.temp_dir.mkdir(exist_ok=True)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(DownloadError)
    )
    def download_video(self, url: str, video_id: str) -> Optional[Path]:
        # check if the video is downloaded before, if it is, then skip it based on the config
        output_template = self.temp_dir / f"{video_id}_%(ext)s"
        cmd = [
            "yt-dlp",
            "-f", "bestaudio/best",
            "--extract-audio",
            "--audio-format", "best",
            "--no-playlist",
            "--ignore-errors",
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
            
            files = list(self.temp_dir.glob(f"{video_id}.*"))
            if files:
                return files[0]
            return None
            
        except subprocess.TimeoutExpired:
            raise DownloadError(f"Download timeout for {url}")
        except subprocess.CalledProcessError as e:
            raise DownloadError(f"Download failed: {e.stderr}")