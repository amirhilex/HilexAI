import os
from datetime import datetime, timezone
from typing import Sequence, Optional
from ...domain.ports import ScraperPort
from ...domain.entities import ScrapedPost, Query, Tweet, TwitterUser, UserRecentTweet

# twikit is installed; import here to keep adapter boundary
from twikit import Client  # adjust if your twikit exposes different entry points

class TwikitScraper(ScraperPort):
    def __init__(self) -> None:
        self._client = Client("en-US")  # locale example; tweak as needed
        self._email = os.getenv("TWIKIT_EMAIL")
        self._username = os.getenv("TWIKIT_USERNAME")
        self._password = os.getenv("TWIKIT_PASSWORD")
        self._logged_in = False

    async def _ensure_login(self):
        if not self._logged_in:
            # twikit login may be sync; if so, run in thread or adapt.
            # For many twikit versions, login is synchronous. We'll call it directly here.
            self._client.login(
                auth_info_1=self._email,
                auth_info_2=self._username,
                password=self._password
            )
            self._logged_in = True

    async def search(self, query: str, limit: int = 20) -> Sequence[ScrapedPost]:
        await self._ensure_login()
        # NOTE: Adjust to your twikit version's API. Many provide .search_tweet or similar.
        # We'll demonstrate a generic approach:
        results = self._client.search_tweet(query=query, count=limit)

        posts: list[ScrapedPost] = []
        for t in results:
            # These attributes may differ by version — tweak field names accordingly.
            post_id = str(getattr(t, "id", getattr(t, "tweet_id", "")))
            author = getattr(t, "user", getattr(t, "username", "unknown"))
            text = getattr(t, "text", "")
            created = getattr(t, "created_at", None)
            if isinstance(created, str):
                # fallback parse if needed
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            elif isinstance(created, datetime):
                created_dt = created
            else:
                created_dt = datetime.now(timezone.utc)

            url = f"https://x.com/{author}/status/{post_id}" if post_id and author else None
            posts.append(ScrapedPost(
                id=post_id, author=str(author), text=text,
                created_at=created_dt, source="x", url=url
            ))
        return posts

    async def search_tweets(self, query: Query, limit: int = 20) -> Sequence[Tweet]:
        await self._ensure_login()
        # Attempt to use an advanced search if available; fallback to simple
        results = self._client.search_tweet(query=query.search_text, count=limit)
        tweets: list[Tweet] = []
        for t in results:
            tweet_id = str(getattr(t, "id", getattr(t, "tweet_id", "")))
            user = getattr(t, "user", None)
            username = getattr(user, "screen_name", getattr(t, "username", None))
            author_id = str(getattr(user, "id", getattr(t, "user_id", "")))
            text = getattr(t, "text", "")
            created = getattr(t, "created_at", None)
            if isinstance(created, str):
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            elif isinstance(created, datetime):
                created_dt = created
            else:
                created_dt = datetime.now(timezone.utc)

            metrics = getattr(t, "public_metrics", None) or {}
            retweet_count = int(getattr(t, "retweet_count", metrics.get("retweet_count", 0)) or 0)
            like_count = int(getattr(t, "favorite_count", metrics.get("like_count", 0)) or 0)
            reply_count = int(metrics.get("reply_count", getattr(t, "reply_count", 0)) or 0)
            quote_count = int(metrics.get("quote_count", getattr(t, "quote_count", 0)) or 0)

            entities = getattr(t, "entities", {}) or {}
            hashtags = [h["text"] if isinstance(h, dict) else str(h) for h in entities.get("hashtags", [])]
            mentions = [m["screen_name"] if isinstance(m, dict) else str(m) for m in entities.get("user_mentions", [])]

            tweet_type = "original"
            if getattr(t, "is_retweet", False):
                tweet_type = "retweet"
            elif getattr(t, "in_reply_to_status_id", None):
                tweet_type = "reply"
            elif getattr(t, "is_quote_status", False):
                tweet_type = "quote"

            original_url = None
            if username and tweet_id:
                original_url = f"https://x.com/{username}/status/{tweet_id}"

            tweets.append(Tweet(
                tweet_id=tweet_id,
                text=text,
                author_id=author_id,
                created_at=created_dt,
                retweet_count=retweet_count,
                like_count=like_count,
                reply_count=reply_count,
                quote_count=quote_count,
                tweet_type=tweet_type,
                hashtags=hashtags or None,
                mentions=mentions or None,
                media_urls=None,  # media URLs resolving can be added if available
                query_id=query.id,
                source="x",
                original_url=original_url,
                scraped_at=datetime.now(timezone.utc),
            ))
        return tweets

    async def get_user_profile(self, user_id: str) -> Optional[TwitterUser]:
        await self._ensure_login()
        try:
            u = self._client.get_user_by_user_id(user_id)
        except Exception:
            return None
        if not u:
            return None
        return TwitterUser(
            user_id=str(getattr(u, "id", user_id)),
            username=getattr(u, "screen_name", getattr(u, "username", "")),
            display_name=getattr(u, "name", getattr(u, "display_name", "")),
            bio=getattr(u, "description", None),
            followers_count=int(getattr(u, "followers_count", 0) or 0),
            following_count=int(getattr(u, "friends_count", 0) or 0),
            profile_image_url=getattr(u, "profile_image_url_https", None),
            header_image_url=getattr(u, "profile_banner_url", None),
            location=getattr(u, "location", None),
            auto_update=False,
        )

    async def get_user_recent_tweets(self, user_id: str, count: int = 3) -> Sequence[Tweet]:
        await self._ensure_login()
        try:
            results = self._client.get_user_tweets(user_id=user_id, count=count)
        except Exception:
            results = []
        tweets: list[Tweet] = []
        for t in results:
            tweet_id = str(getattr(t, "id", getattr(t, "tweet_id", "")))
            text = getattr(t, "text", "")
            created = getattr(t, "created_at", None)
            if isinstance(created, str):
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            elif isinstance(created, datetime):
                created_dt = created
            else:
                created_dt = datetime.now(timezone.utc)
            tweets.append(Tweet(
                tweet_id=tweet_id,
                text=text,
                author_id=user_id,
                created_at=created_dt,
                source="x",
                scraped_at=datetime.now(timezone.utc),
            ))
        return tweets

