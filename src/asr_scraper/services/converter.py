import ffmpeg
from pathlib import Path

class Converter:
    def __init__(self, sample_rate: int = 16000, mono: bool = True, bit_depth: int = 16):
        self.sample_rate = sample_rate
        self.mono = mono
        self.bit_depth = bit_depth
     
    def convert_to_wav(self, input_path: Path, output_path: Path):
        try:
            # TODO - implement conversion
            pass
        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            return False