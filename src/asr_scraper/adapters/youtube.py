import json
import subprocess
from datetime import datetime
from ..models import VideoItem
from .base import ChannelAdapter, registry
from typing import Optional

class YouTubeAdapter(ChannelAdapter):
    name = "youtube"

    def can_handle(self, channel_ref: str) -> bool:
        handleable_domains = [
            "youtube.com/",
            "youtu.be/",
            "youtube.com/@",
            "youtube.com/channel/",
            "youtube.com/c/",
            "youtube.com/user/"
        ]
        
        for d in handleable_domains:
            if d in channel_ref:
                return True
        
        return False

    def normalize_channel_ref(self, channel_ref: str):
        cmd = [
            'yt-dlp', '--quiet', '--max-downloads', '1', '--skip-download',
            '--no-warnings', '--print', '%(channel_id)s', channel_ref
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            channel_id = res.stdout.strip()
            
            if channel_id:
                return channel_id
            else:
                raise Exception("Empty channel_id")

        except subprocess.CalledProcessError as e:
            if e.returncode == 101:
                channel_id = e.output.strip() if e.output else None
                if channel_id:
                    return channel_id
                else:
                    print("Empty channel_id")
                    return None
            else:
                print(f"Failed to fetch channel_id: {e}")
                return None
    
    def list_videos(self, channel_ref: str, since: Optional[str] = None):
        if not self.can_handle(channel_ref):
            return None
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--dump-json",
            "--ignore-errors",
            "--no-warnings",
            channel_ref
        ]
        
        if since is not None: 
            cmd = [
                "yt-dlp",
                "--dateafter", since,
                "--dump-json",
                "--ignore-errors",
                "--no-warnings",
                channel_ref
            ]
        
        try:
            # get normalized channel reference
            channel = self.normalize_channel_ref(channel_ref)

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # remove all the spaces before and after the string
            for line in iter(process.stdout.readline, ""):
                if not line:
                    continue
                    
                try:
                    data = json.loads(line)
                    upload_date = None
                    if data.get('upload_date'):
                        try:
                            upload_date = datetime.strptime(
                                data['upload_date'], 
                                '%Y%m%d'
                            ).date()
                        except ValueError:
                            pass
                    
                    yield VideoItem(
                        platform="youtube",
                        channel_ref=channel,
                        video_id=data.get('id', ''),
                        title=data.get('title', 'Untitled'),
                        url=f"https://youtube.com/watch?v={data.get('id', '')}",
                        upload_date=upload_date,
                        duration_s=data.get('duration')
                    )
                    
                except json.JSONDecodeError:
                    continue
                    
        except subprocess.CalledProcessError as e:
            print(f"Failed to list videos: {e.stderr}")
            return
            
registry.register("youtube", YouTubeAdapter())