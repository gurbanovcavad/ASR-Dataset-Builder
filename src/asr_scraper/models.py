from typing import Optional
from dataclasses import dataclass
from datetime import datetime, date

@dataclass(Frozen=True)
class VideoItem:
    platform: str
    channel_ref: str
    video_id: str
    title: str
    url: str
    upload_date: Optional[date] = None
    duration_s: Optional[int] = None
    
@dataclass(Frozen=True)
class JobResult:
    ts_utc: datetime
    platform: str
    channel_ref: str
    video_id: str
    url: str
    title: str
    wav_path: Optional[str]
    # ok, skipped, failed
    status: str
    error: Optional[str]
    sha256: Optional[str]
    audio_sr: Optional[int]
    audio_channels: Optional[int]
    audio_duration_s: Optional[float]