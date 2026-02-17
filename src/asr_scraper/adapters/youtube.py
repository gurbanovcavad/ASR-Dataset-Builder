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

    def list_videos(self, channel_ref: str):
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--dump-single-json",
            "--ignore-errors",
            "--no-warnings",
            channel_ref
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # remove all the spaces before and after the string
            for line in result.stdout.strip().split('\n'):
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
                        channel_ref=self.normalize_channel_ref(channel_ref),
                        video_id=data.get('id', ''),
                        title=data.get('title', 'Untitled'),
                        url=f"https://youtube.com/watch?v={data.get('id', '')}",
                        upload_date=upload_date,
                        duration_s=data.get('duration')
                    )
                    
                except json.JSONDecodeError:
                    continue
                    
        except subprocess.CalledProcessError as e:
            print(f"Error listing videos: {e.stderr}")
            return
        
registry.register(YouTubeAdapter())