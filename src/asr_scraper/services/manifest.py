from pathlib import Path
import json
from typing import List
from datetime import datetime

from ..models import JobResult

class ManifestWriter:
    def __init__(self, manifest_path: Path):
        self.manifest_path = manifest_path
        self.videos: set[tuple[str, str]] = set()
        self._ensure_file()
        self._load()
    
    def _ensure_file(self):
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.manifest_path.exists():
            self.manifest_path.touch()

    def _load(self):
        with self.manifest_path.open() as f:
            for line in f:
                data = json.loads(line)
                if data["status"] == "ok":
                    self.videos.add((data["platform"], data["video_id"]))

    def is_downloaded(self, platform: str, video_id: str) -> bool:
        return (platform, video_id) in self.videos

    def append(self, result: JobResult):
        data = {
            "platform": result.platform,
            "ts_utc": result.ts_utc,
            "channel_ref": result.channel_ref,
            "video_id": result.video_id,
            "url": result.url,
            "title": result.title,
            "wav_path": result.wav_path,
            "status": result.status,
            "error": result.error,
            "sha256": result.sha256,
            "audio_sr": result.audio_sr,
            "audio_channels": result.audio_channels,
            "audio_duration_s": result.audio_duration_s
        }
        
        with open(self.manifest_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data) + '\n')
            