from abc import ABC, abstractmethod
from typing import Iterable

class ChannelAdapter(ABC):
    name: str

    @abstractmethod
    def can_handle(self, channel_ref: str) -> bool:
        pass
        
    @abstractmethod
    def list_videos(self, channel_ref: str) -> Iterable[VideoItem]:
        pass
    
    def normalize_channel_ref(self, channel_ref: str) -> str:
        return channel_ref.strip('/').split('/')[-1]
    
class AdapterRegistry:
    def __init__(self):
        self._adapters: List[ChannelAdapter] = []
        
    def register(self, new: ChannelAdapter):
        self._adapters.append(new)
    
registry = AdapterRegistry()