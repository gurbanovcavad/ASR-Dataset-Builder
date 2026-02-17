import ffmpeg
from pathlib import Path

class Converter:
    def __init__(self, sample_rate: int = 16000, mono: bool = True, bit_depth: int = 16):
        self.sample_rate = sample_rate
        self.mono = mono
        self.bit_depth = bit_depth
        self.codec = {
            8: "pcm_s8",
            16: "pcm_s16le",
            24: "pcm_s24le",
            32: "pcm_s32le"
        }.get(bit_depth, "pcm_s16le")
     
    def convert_to_wav(self, input_path: Path, output_path: Path):
        try:
            channels = 1 if self.mono else 2
            
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                ac=channels,
                ar=self.sample_rate,
                acodec=self.codec,
                **{'y': None}
            )
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            return output_path.exists() and output_path.stat().st_size > 0
        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            return False