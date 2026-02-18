from pathlib import Path
import json
from typing import List
from datetime import datetime

from ..models import JobResult

class ManifestWriter:
    def __init__(self, manifest_path: Path):
        self.manifest_path = manifest_path
        self._ensure_file()
    
    def _ensure_file(self):
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.manifest_path.exists():
            self.manifest_path.touch()

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
            
    def print_all(self) -> List[JobResult]:
        res = []
        
        if not self.manifest_path.exists():
            return []
        
        with open(self.manifest_path, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                data = json.loads(line)
                data['ts_utc'] = datetime.fromisoformat(data['ts_utc'])
                res.append(JobResult(**data))

        return res