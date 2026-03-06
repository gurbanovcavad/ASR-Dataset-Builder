import yaml
from pathlib import Path

from asr_scraper.config import config

def create_config():
    with open("./configs/config.yaml") as file:
        try:
            data = yaml.safe_load(file)
            
            with open(data["channels_file"]) as f:
                temp = [line.rstrip() for line in f]
            setattr(config, "channels", temp)
            
            setattr(config, "output_dir", Path(data["output_dir"]))
            setattr(config, "sample_rate", data["sample_rate"])
            setattr(config, "mono", data["mono"])
            setattr(config, "pcm_bit_depth", data["pcm_bit_depth"])
            setattr(config, "concurrency", data["concurrency"])
            setattr(config, "max_videos_per_channel", data["max_videos_per_channel"])
            setattr(config, "since_date", data["since_date"])
            setattr(config, "skip_existing", data["skip_existing"])
            setattr(config, "write_manifest", Path(data["write_manifest"]))
            proxy = data["proxy"]
            setattr(config, "proxy", "" if proxy is None else proxy)
            setattr(config, "transcripts_dir", Path(data["transcripts_dir"]))
        except yaml.YAMLError as e:
            print(e)
        except Exception as e:
            print(e)