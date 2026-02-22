# ASR Dataset Builder

## To run the project via the main function 
```
uv sync --no-dev
```
* update the channels.txt
```
uv run python -m main
```
* for platforms other than youtube, the name of platform should be specified while calling the function 
```
uv run python -m main x
```

## CLI commands
```
uv sync --no-dev
```

### Discover 
#### Flags:
```
--platform/-p (optional for now - default: youtube)
--channel/-c (required)
``` 
```
uv run audio-scraper discover -c https://www.youtube.com/@turkeiran/videos
```

### Build
#### Flags:
```
--platform/-p (optional for now - default: youtube)
--channel/-c (required)
--output/-o (optional - default: the output_dir specified in the config file)
--sr (optional - default: the sample_rate specified in the config file)
--mono/--stereo (optional - default: the mono specified in the config file)
--codec (pcm_bit_depth) (optional - default: the pcm_bit_depth specified in the config file)
--jobs/-j (optional - default: the concurrency specified in the config file)
--max/-m (optional - default: the max_videos_per_channel specified in the config file)
--since_date (optional - default: the since_date specified in the config file)
--skip/--no-skip (optional - default: the skip_existing specified in the config file)
--manifest (optional - default: the write_manifest specified in the config file)
```
```
uv run audio-scraper build -c https://www.youtube.com/@turkeiran/videos 
```

## Config file
* configs/config.yaml
```
output_dir: ./data
channels_file: /home/cavad/Projects/asr-scraper/channels.txt
sample_rate: 16000
mono: true
pcm_bit_depth: 16
concurrency: 3
max_videos_per_channel: null 
# format: YYYYMMDD (20260219)
since_date: null
skip_existing: true
write_manifest: ./manifest.jsonl
```

## To run with docker 
```
docker build -t asr-scraper .
```
```
docker run -i asr-scraper
```

## Install FFmpeg
* Linux (Debian/Ubuntu)
```
sudo apt update  
```
```
sudo apt install ffmpeg
```

* macOS
```
brew install ffmpeg
```

* Windows
```
https://www.ffmpeg.org/download.html
```
* install the zip file
* create a new environment variable