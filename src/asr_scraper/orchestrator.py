from asr_scraper.adapters.youtube import YoutubeAdapter
from asr_scraper.services.downloader import Downloader
from asr_scraper.services.converter import Converter
from asr_scraper.services.manifest import ManifestWriter
from asr_scraper.services.validator import Validator
from asr_scraper.adapters.base import ChannelAdapter
from asr_scraper.utils.slugify import slugify
from asr_scraper.utils.hashing import hash
from asr_scraper.models import JobResult
from asr_scraper.config import config
from asr_scraper.models import VideoItem

import logging
from rich.console import Console 
from pathlib import Path
from typing import List
from datetime import datetime, timezone
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import subprocess

class Orchestrator:
    def __init__(self, console: Console, platform: ChannelAdapter, platform_name: str):
        self.temp_dir = Path(f"temp/{platform_name}/")
        self.downloader = Downloader(self.temp_dir, config.proxy)
        self.converter = Converter(config.sample_rate, config.mono, config.pcm_bit_depth)
        self.manifest_writer = ManifestWriter(config.write_manifest)
        self.validator = Validator(config.sample_rate, config.channels)
        self.platform = platform
        self.platform_name = platform_name
        self.console = console
        self.logger = logging.getLogger(__name__)
        self.max_workers = config.concurrency
        self.min_delay = 1.0
        self.max_delay = 4.0
        self._lock = threading.Lock() 
    
    def discover(self, channels: List[str]):
        for channel in channels: 
            videos = self.platform.list_videos(channel, config.since_date)

            for video in videos: 
                self.console.print(f"[blue]{video}[/blue]")    
        
    def download(self, url: str):
        try:
            # extract video_id from the url
            parts = url.split("=")
            if len(parts) != 2:
                raise Exception("Invalid url")

            # extract title from the url
            title = self.platform.get_video_title(url)
            channel_ref = self.platform.normalize_channel_ref(url)
            
            video = VideoItem(self.platform_name, channel_ref, parts[1], title, url)
            self._process_video(video, 1)
        except Exception as e:
            self.logger.error(
                    "failed",
                    extra={
                        "order": 1,
                        "platform": self.platform_name,
                        "channel_ref": None,
                        "video_id": None,
                        "url": url,
                    },
                )
            raise(e)
            
                
    def build(self, channels: List[str]):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            for channel in channels:
                videos = self.platform.list_videos(channel, config.since_date)

                c = 0
                for video in videos:
                    if config.max_videos_per_channel is not None and c >= config.max_videos_per_channel:
                        break

                    futures.append(executor.submit(self._process_video, video, c + 1))
                    c += 1

            for f in as_completed(futures):
                f.result()
            
    def _process_video(self, video, order):
        try:
            time.sleep(random.uniform(self.min_delay, self.max_delay))

            if config.skip_existing and self.manifest_writer.is_downloaded(self.platform_name, video.video_id):
                self._write_skipped(video, order)
                return
            
            input_path = self.downloader.download_video(video.url, video.video_id)

            output_dir = config.output_dir / video.channel_ref
            output_dir.mkdir(exist_ok=True, parents=True)
            output_path = slugify(video.title, output_dir, video.video_id, "wav")

            self.converter.convert_to_wav(input_path, output_path)

            validation_result = self.validator.validate(output_path)

            # delete the temp file audio file
            input_path.unlink(missing_ok=True)

            if not validation_result.ok:
                output_path.unlink(missing_ok=True)
                raise RuntimeError(validation_result.error)

            result = JobResult(
                ts_utc=datetime.now(timezone.utc).isoformat(),
                platform=self.platform_name,
                channel_ref=video.channel_ref,
                video_id=video.video_id,
                url=video.url,
                title=video.title,
                wav_path=str(output_path),
                status="ok",
                error=None,
                sha256=hash(str(output_path)),
                audio_sr=validation_result.sample_rate,
                audio_channels=validation_result.channels,
                audio_duration_s=validation_result.duration_s,
            )
            
            with self._lock:
                self.manifest_writer.append(result)

                self.console.print(f"[green]{order} - {self.platform_name}, {video.channel_ref}, {video.video_id}, {video.url} - ok[/green]")
                
                self.logger.info(
                    "ok",
                    extra={
                        "order": order,
                        "platform": self.platform_name,
                        "channel_ref": video.channel_ref,
                        "video_id": video.video_id,
                        "url": video.url,
                    },
                )

            time.sleep(random.uniform(self.min_delay, self.max_delay))
            try:
                temp_path = self.downloader.download_subtitles(video.url, video.video_id)
                transcript_dir = config.transcripts_dir / video.channel_ref
                transcript_dir.mkdir(parents=True, exist_ok=True)
                transcript_path = slugify(video.title, transcript_dir, video.video_id, "txt")
                
                # delete timestamps and etc. 
                self._create_transcript(temp_path, transcript_path)

                # delete the temporary file
                temp_path.unlink()
            except Exception as e:
                pass

        except Exception as e:
            result = JobResult(
                ts_utc=datetime.now(timezone.utc).isoformat(),
                platform=self.platform_name,
                channel_ref=video.channel_ref,
                video_id=video.video_id,
                url=video.url,
                title=video.title,
                wav_path=None,
                status="failed",
                error=str(e),
                sha256=None,
                audio_sr=None,
                audio_channels=None,
                audio_duration_s=None,
            )

            with self._lock:
                self.manifest_writer.append(result)

                self.console.print(f"[red]{order} - {self.platform_name}, {video.channel_ref}, {video.video_id}, {video.url} - failed[/red]")

                self.logger.error(
                    "failed",
                    extra={
                        "order": order,
                        "platform": self.platform_name,
                        "channel_ref": video.channel_ref,
                        "video_id": video.video_id,
                        "url": video.url,
                    },
                )
            
    def _write_skipped(self, video, order):
        result = JobResult(
            ts_utc=datetime.now(timezone.utc).strftime("%m/%d/%Y, %H:%M:%S"),
            platform=self.platform_name,
            channel_ref=video.channel_ref,
            video_id=video.video_id,
            url=video.url,
            title=video.title,
            wav_path=None,
            status="skipped",
            error=None,
            sha256=None,
            audio_sr=None, 
            audio_channels=None,
            audio_duration_s=None,
        )
        with self._lock:
            self.manifest_writer.append(result)
        
            self.console.print(f"[yellow]{order} - {self.platform_name}, {video.channel_ref}, {video.video_id}, {video.url} - skipped[/yellow]")

            self.logger.info(
                "skipped",
                extra={
                    "order": order,
                    "platform": self.platform_name,
                    "channel_ref": video.channel_ref,
                    "video_id": video.video_id,
                    "url": video.url,
                },
            )
            
    def _create_transcript(self, input, output):
        cmd = [
            "sed",
            "-e", r"/^[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9] --> [0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]$/d",
            "-e", r"/^[[:digit:]]\{1,4\}$/d",
            "-e", r"s/>> //g",
            "-e", r"s/<[^>]*>//g",
            "-e", r"/^[[:space:]]*$/d",
            str(input)
        ]

        with open(output, "w") as f:
            subprocess.run(cmd, stdout=f, check=True)