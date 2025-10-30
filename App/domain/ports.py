from abc import ABC, abstractmethod
from typing import List
from .entities import Tweet

class ScraperPort(ABC):
    @abstractmethod
    async def search_tweets(self, keyword: str, limit: int) -> List[Tweet]:
        pass