from typing import Sequence
from ..domain.ports import ScraperPort, PostRepositoryPort
from ..domain.entities import ScrapedPost

class ScrapeAndStorePostsUseCase:
    def __init__(self, scraper: ScraperPort, repo: PostRepositoryPort):
        self._scraper = scraper
        self._repo = repo

    async def execute(self, query: str, limit: int = 20) -> dict:
        posts: Sequence[ScrapedPost] = await self._scraper.search(query=query, limit=limit)
        saved = await self._repo.save_many(list(posts))
        return {"found": len(posts), "saved": saved}

