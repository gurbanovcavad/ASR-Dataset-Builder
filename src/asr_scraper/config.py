from typing import Optional, List
from datetime import date
from pathlib import Path

class Config:
    def __init__(self, 
                channels: List[str] = [], 
                output_dir: Path = Path("./data"), 
                sample_rate: int = 16000, 
                mono: bool = True, 
                pcm_bit_depth: int = 16, 
                concurrency: int = 2, 
                max_videos_per_channel: Optional[int] = None, 
                since_date: Optional[str] = None, 
                skip_existing: bool = True, 
                write_manifest: Path = Path("./manifest.jsonl"),
                proxy: str = "",
        ):
        self.channels = channels
        self.output_dir = output_dir
        self.sample_rate = sample_rate
        self.mono = mono
        self.pcm_bit_depth = pcm_bit_depth
        self.concurrency = concurrency
        self.max_videos_per_channel = max_videos_per_channel
        self.since_date = since_date 
        self.skip_existing = skip_existing
        self.write_manifest = write_manifest
        self.proxy = proxy
        # platform_overrides: 
        
config = Config()