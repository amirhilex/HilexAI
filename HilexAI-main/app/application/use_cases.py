from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Sequence

from fastapi import Depends

from ..domain.entities import ScrapedPost, Query, Tweet, TwitterUser, MediaFile, UserRecentTweet
from ..domain.ports import (
    ScraperPort,
    PostRepositoryPort,
    QueryRepositoryPort,
    TweetRepositoryPort,
    TwitterUserRepositoryPort,
    MediaFileRepositoryPort,
    UserRecentTweetRepositoryPort,
)


class ScrapeAndStorePostsUseCase:
    """Legacy use case used by /scrape endpoint"""
    def __init__(self, scraper: ScraperPort, repo: PostRepositoryPort):
        self._scraper = scraper
        self._repo = repo

    async def execute(self, query: str, limit: int = 20) -> dict:
        posts: Sequence[ScrapedPost] = await self._scraper.search(query=query, limit=limit)
        saved = await self._repo.save_many(list(posts))
        return {"found": len(posts), "saved": saved}


class ExecuteQueryUseCase:
    def __init__(
        self,
        scraper: ScraperPort,
        query_repo: QueryRepositoryPort,
        tweet_repo: TweetRepositoryPort,
        user_repo: TwitterUserRepositoryPort,
        media_repo: MediaFileRepositoryPort,
        user_recent_repo: UserRecentTweetRepositoryPort,
    ):
        self._scraper = scraper
        self._query_repo = query_repo
        self._tweet_repo = tweet_repo
        self._user_repo = user_repo
        self._media_repo = media_repo
        self._user_recent_repo = user_recent_repo

    async def execute(
        self,
        query_id: int,
        limit: int = 50,
        include_media: bool = True,
        update_user_profiles: bool = True,
    ) -> dict:
        q = await self._query_repo.get_by_id(query_id)
        if not q or not q.is_active:
            return {"found": 0, "saved": 0, "media_files_saved": 0, "users_updated": 0, "query_id": query_id}

        tweets: Sequence[Tweet] = await self._scraper.search_tweets(q, limit=limit)
        # Save tweets
        saved_tweets = await self._tweet_repo.save_many(list(tweets))

        users_updated = 0
        media_saved = 0

        if update_user_profiles:
            # Upsert users referenced in tweets
            user_ids = {t.author_id for t in tweets}
            for uid in user_ids:
                profile = await self._scraper.get_user_profile(uid)
                if profile:
                    await self._user_repo.save(profile)
                    # Update user's recent tweets table
                    recent = await self._scraper.get_user_recent_tweets(uid, count=3)
                    recent_user_tweets = [
                        UserRecentTweet(id=None, user_id=uid, tweet_id=t.tweet_id, text=t.text, created_at=t.created_at)
                        for t in recent
                    ]
                    await self._user_recent_repo.save_user_tweets(uid, recent_user_tweets)
                    users_updated += 1

        if include_media:
            # For each tweet, if there are media URLs, persist references
            media_files: list[MediaFile] = []
            for t in tweets:
                if not t.media_urls:
                    continue
                for media_url in t.media_urls:
                    media_files.append(MediaFile(
                        id=None,
                        tweet_id=t.tweet_id,
                        media_type="photo" if any(media_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]) else "video",
                        original_url=media_url,
                    ))
            if media_files:
                media_saved = await self._media_repo.save_many(media_files)

        await self._query_repo.update_last_run(query_id, datetime.now(timezone.utc))

        return {
            "found": len(tweets),
            "saved": saved_tweets,
            "media_files_saved": media_saved,
            "users_updated": users_updated,
            "query_id": query_id,
        }

