from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Tweet:
    tweet_id: str
    username: str
    name: str
    text: str
    likes: int
    retweets: int
    replies: int
    created_at: datetime
    images: Optional[List[str]] = None

@dataclass
class TwitterUser:
    user_id: str
    username: str
    display_name: str
    followers_count: int
    following_count: int