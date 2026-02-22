from asr_scraper.adapters.youtube import YouTubeAdapter
from asr_scraper.services.downloader import Downloader
from asr_scraper.services.converter import Converter
from asr_scraper.services.manifest import ManifestWriter
from asr_scraper.services.validator import Validator
from asr_scraper.adapters.base import ChannelAdapter
from asr_scraper.utils.slugify import slugify
from asr_scraper.utils.hashing import hash
from asr_scraper.models import JobResult
from asr_scraper.config import config

import logging
from rich.console import Console 
from pathlib import Path
from typing import List
from datetime import datetime, timezone

class Orchestrator:
    def __init__(self, console: Console, platform: ChannelAdapter, plaform_name: str):
        self.downloader = Downloader(Path(f"./temp/{plaform_name}/"))
        self.converter = Converter(config.sample_rate, config.mono, config.pcm_bit_depth)
        self.manifest_writer = ManifestWriter(config.write_manifest)
        self.validator = Validator(config.sample_rate, config.channels)
        self.platform = platform
        self.platform_name = plaform_name
        self.console = console
        self.logger = logging.getLogger(__name__)
    
    def discover(self, channels: List[str]):
        for channel in channels: 
            videos = self.platform.list_videos(channel, config.since_date)

            for video in videos: 
                self.console.print(f"[blue]{video}[/blue]")    
        
    def build(self, channels: List[str]):
        for channel in channels:
            c = 0
            # apply since_date 
            videos = self.platform.list_videos(channel, config.since_date)

            for video in videos:
                # skipped
                if config.skip_existing:
                    if self.manifest_writer.is_downloaded(self.platform_name, video.video_id):
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
                        self.manifest_writer.append(result)
                        self.console.print(f"[yellow]{self.platform_name}, {video.channel_ref}, {video.video_id}, {video.url} - skipped[/yellow]")
                        self.logger.info(
                            "skipped",
                            extra={
                                "platform": self.platform_name,
                                "channel_ref": video.channel_ref,
                                "video_id": video.video_id,
                                "url": video.url,
                            },
                        )
                        continue

                # ok
                try: 
                    # apply max_videos filter 
                    if config.max_videos_per_channel is not None and config.max_videos_per_channel == c:
                        break 
                    
                    # convert to wav the downloaded videos, the input path is {channel_id}/{video_id}
                    input_path = self.downloader.download_video(video.url, video.video_id)

                    # create output path according to the channel_ref and slugify(video.title)
                    output_dir = config.output_dir / video.channel_ref
                    output_dir.mkdir(exist_ok=True, parents=True)
                    output_path = slugify(video.title, output_dir, video.video_id)
                    
                    self.converter.convert_to_wav(input_path, output_path)

                    # validate the downloaded audio
                    validation_result = self.validator.validate(output_path)
                    if not validation_result.ok:
                        # delete the downloaded file
                        output_path.unlink(missing_ok=True)
                        
                        result = JobResult(
                            ts_utc=datetime.now(timezone.utc).strftime("%m/%d/%Y, %H:%M:%S"),
                            platform=self.platform_name,
                            channel_ref=video.channel_ref,
                            video_id=video.video_id,
                            url=video.url,
                            title=video.title,
                            wav_path=None,
                            status="failed",
                            error=validation_result.error,
                            sha256=None,
                            audio_sr=None, 
                            audio_channels=None,
                            audio_duration_s=None,
                        )
                        self.manifest_writer.append(result)
                        self.console.print(f"[red]{self.platform_name}, {video.channel_ref}, {video.video_id}, {video.url} - failed[/red]")
                        self.logger.error(
                            "failed",
                            extra={
                                "platform": self.platform_name,
                                "channel_ref": video.channel_ref,
                                "video_id": video.video_id,
                                "url": video.url,
                            },
                        )
                    
                    result = JobResult(
                        ts_utc=datetime.now(timezone.utc).strftime("%m/%d/%Y, %H:%M:%S"),
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
                    self.manifest_writer.append(result)
                    self.console.print(f"[green]{self.platform_name}, {video.channel_ref}, {video.video_id}, {video.url} - ok[/green]")
                    self.logger.info(
                        "ok",
                        extra={
                            "platform": self.platform_name,
                            "channel_ref": video.channel_ref,
                            "video_id": video.video_id,
                            "url": video.url,
                        },
                    )
                    c += 1
                # failed
                except Exception as e:
                    self.logger.error(
                        "failed",
                        extra={
                            "platform": self.platform_name,
                            "channel_ref": video.channel_ref,
                            "video_id": video.video_id,
                            "url": video.url,
                        },
                    )
                    result = JobResult(
                        ts_utc=datetime.now(timezone.utc).strftime("%m/%d/%Y, %H:%M:%S"),
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
                    self.manifest_writer.append(result)
                    self.console.print(f"[red]{self.platform_name}, {video.channel_ref}, {video.video_id}, {video.url} - failed[/red]")
            