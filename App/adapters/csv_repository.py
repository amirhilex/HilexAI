import pandas as pd
from typing import List
from ..domain.entities import Tweet

class CSVRepository:
    def __init__(self, out_file: str = "tweets.csv"):
        self.out_file = out_file

    def save_many(self, tweets: List[Tweet]):
        rows = []
        for t in tweets:
            rows.append({
                "tweet_id": t.tweet_id,
                "username": t.username,
                "name": t.name,
                "text": t.text,
                "likes": t.likes,
                "retweets": t.retweets,
                "replies": t.replies,
                "created_at": t.created_at,
                "images": ", ".join(t.images) if t.images else ""
            })
        df = pd.DataFrame(rows)
        df.to_csv(self.out_file, index=False, encoding="utf-8-sig")
        print(f"Saved {len(rows)} rows to {self.out_file}")
