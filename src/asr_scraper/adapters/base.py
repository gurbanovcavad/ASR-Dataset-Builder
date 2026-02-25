from abc import ABC, abstractmethod
from typing import Iterable, List
from ..models import VideoItem

class ChannelAdapter(ABC):
    name: str

    @abstractmethod
    def can_handle(self, channel_ref: str) -> bool:
        pass
        
    @abstractmethod
    def list_videos(self, channel_ref: str) -> Iterable[VideoItem]:
        pass
    
    @abstractmethod
    def normalize_channel_ref(self, channel_ref: str) -> str:
        pass
    
    @abstractmethod 
    def get_video_title(self, url: str) -> str:
        pass
    
class AdapterRegistry:
    def __init__(self):
        self._adapters: dict[str, 'ChannelAdapter'] = {}
        
    def register(self, name: str, adapter: ChannelAdapter):
        if name in self._adapters:
            print(f"Warning: Overwriting existing adapter '{name}'")
        self._adapters[name] = adapter
        
    def get(self, name: str):
        return self._adapters.get(name)
    
registry = AdapterRegistry()