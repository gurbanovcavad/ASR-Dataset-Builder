import subprocess
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class Downloader:
    def download_video(self, video_url: str):
        pass