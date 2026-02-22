import subprocess
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    sample_rate: Optional[int]
    channels: Optional[int]
    duration_s: Optional[float]
    error: Optional[str]

class Validator:
    def __init__(self, sample_rate: int, channels: bool):
        self.sample_rate = sample_rate
        self.channels = 1 if channels else 2
        
    def validate(self, wav_path: Path) -> ValidationResult:
        if not wav_path.exists():
            return ValidationResult(
                ok=False,
                sample_rate=None,
                channels=None,
                duration_s=None,
                error="File does not exist",
            )

        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-print_format", "json",
                "-show_streams",
                "-show_format",
                str(wav_path),
            ]
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True,
            )

            data = json.loads(res.stdout)
            if "streams" not in data or not data["streams"]:
                return ValidationResult(
                    ok=False,
                    sample_rate=None,
                    channels=None,
                    duration_s=None,
                    error="No audio stream found",
                )
            stream = data["streams"][0]

            sr = int(stream.get("sample_rate", 0))
            channels = int(stream.get("channels", 0))
            duration = float(data["format"].get("duration", 0.0))
            
            if duration <= 0:
                return ValidationResult(
                    ok=False,
                    sample_rate=sr,
                    channels=channels,
                    duration_s=duration,
                    error="Duration is zero",
                )
            if sr != self.sample_rate:
                return ValidationResult(
                    ok=False,
                    sample_rate=sr,
                    channels=channels,
                    duration_s=duration,
                    error=f"Sample rate mismatch",
                )
            if channels != self.channels:
                return ValidationResult(
                    ok=False,
                    sample_rate=sr,
                    channels=channels,
                    duration_s=duration,
                    error=f"Channel mismatch",
                )

            return ValidationResult(
                ok=True,
                sample_rate=sr,
                channels=channels,
                duration_s=duration,
                error=None,
            )
        except subprocess.CalledProcessError as e:
            return ValidationResult(
                ok=False,
                sample_rate=None,
                channels=None,
                duration_s=None,
                error=f"ffprobe error: {e.stderr}",
            )
        except Exception as e:
            return ValidationResult(
                ok=False,
                sample_rate=None,
                channels=None,
                duration_s=None,
                error=str(e),
            )