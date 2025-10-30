import os
import json
import asyncio
from datetime import datetime
from typing import List
from twikit import Client
from App.domain.entities import Tweet
from App.domain.ports import ScraperPort

COOKIE_FILE = "cookies.json"

class TwikitScraper(ScraperPort):
    def __init__(self, language: str = "en-US"):
        self.client = Client(language=language)
        cookies = self._get_cookies()
        self.client.set_cookies(cookies)

    def _get_cookies(self):
        if os.path.exists(COOKIE_FILE):
            with open(COOKIE_FILE, 'r') as f:
                cookies = json.load(f)
                print(" Loaded cookies from file.")
        else:
            auth_token = input("Enter your auth_token: ").strip()
            ct0 = input("Enter your ct0: ").strip()
            cookies = {"auth_token": auth_token, "ct0": ct0}
            with open(COOKIE_FILE, 'w') as f:
                json.dump(cookies, f)
                print(" Saved cookies to file.")
        return cookies

    async def search_tweets(self, keyword: str, limit: int = 100, count: int = 20) -> List[Tweet]:
        tweets_data = []
        cursor = None

        while len(tweets_data) < limit:
            try:
                tweets = await self.client.search_tweet(keyword, product='Top', count=count, cursor=cursor)
            except Exception as e:
                if "429" in str(e):
                    print("⚠️ Rate limit reached. Waiting 60 seconds...")
                    await asyncio.sleep(60)
                    continue
                else:
                    raise e

            if not tweets:
                break

            for t in tweets:
                images_urls = []
                if hasattr(t, "media") and t.media:
                    images_urls = [getattr(m, "media_url_https", getattr(m, "url", None))
                                   for m in t.media if getattr(m, "type", None) == "photo"]
                    images_urls = [u for u in images_urls if u]

                tweets_data.append(Tweet(
                    tweet_id=str(t.id),
                    username=getattr(t.user, "screen_name", ""),
                    name=getattr(t.user, "name", ""),
                    text=getattr(t, "text", ""),
                    likes=int(getattr(t, "favorite_count", 0) or 0),
                    retweets=int(getattr(t, "retweet_count", 0) or 0),
                    replies=int(getattr(t, "reply_count", 0) or 0),
                    created_at=getattr(t, "created_at", datetime.utcnow()),
                    images=images_urls if images_urls else None
                ))

                if len(tweets_data) >= limit:
                    break

            cursor = getattr(tweets, "next_cursor", None)
            if not cursor:
                break

        print(f" Collected {len(tweets_data)} tweets.")
        return tweets_data

