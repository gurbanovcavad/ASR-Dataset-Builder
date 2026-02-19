from asr_scraper.adapters.youtube import YouTubeAdapter
from asr_scraper.services.downloader import Downloader
from asr_scraper.services.converter import Converter
from asr_scraper.services.manifest import ManifestWriter
from asr_scraper.services.validator import Validator
from asr_scraper.config import Config
from asr_scraper.adapters.base import ChannelAdapter
from asr_scraper.models import VideoItem

from typing import List

class Orchestrator:
    def __init__(self, config: Config, platform: ChannelAdapter):
        self.downloader = Downloader()
        self.converter = Converter()
        self.manifest_writer = ManifestWriter(config.write_manifest)
        self.validator = Validator()
        self.config = config
        self.platform = platform
    
    def discover(self, channel_ref: str):
        return self.platform.list_videos(channel_ref)
      
    def build(self, videos: List[VideoItem]):
        for video in videos:
            
            input_path = self.downloader.download_video(video.url, video.video_id)
            
            # convert to wav the downloaded videos, the input_path and the output_path will be the same
            output_path = input_path
            self.converter.convert_to_wav(input_path, output_path)
            
            # validate audio after downloading and converting to wav
            self.validator.validate(output_path)