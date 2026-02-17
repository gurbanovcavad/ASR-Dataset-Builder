from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    output_dir: str = './data'
    channels_file: str = 'channels.txt'
    sample_rate: int = 16000
    mono: bool = True
    pcm_bit_depth: int = 16
    concurrency: int = 2
    max_videos_per_channel: Optional[int] = None
    skip_existing: bool = True
    write_manifest: str = 'manifest.jsonl'

    class Config:
        env_file = ".env"
        case_sensitive = False