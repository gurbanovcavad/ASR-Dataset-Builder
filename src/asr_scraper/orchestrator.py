from asr_scraper.adapters.youtube import YouTubeAdapter
from asr_scraper.services.downloader import Downloader
from asr_scraper.services.converter import Converter
from asr_scraper.services.manifest import ManifestWriter

class Orchestrator:
    def __init__(self):
        self.downloader = Downloader()
        self.converter = Converter()
        self.manifest_writer = ManifestWriter()
    
    def discover(self):
        pass

    def download(self):
        pass
    
    def convert(self):
        pass
    
    def store(self):
        pass