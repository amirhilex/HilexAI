from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(slots=True, frozen=True)
class Query:
    id: Optional[int]
    name: str
    search_text: str
    filters: Optional[dict] = None
    schedule_interval: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None

@dataclass(slots=True, frozen=True)
class TwitterUser:
    user_id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    profile_image_url: Optional[str] = None
    header_image_url: Optional[str] = None
    location: Optional[str] = None
    auto_update: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass(slots=True, frozen=True)
class Tweet:
    tweet_id: str
    text: str
    author_id: str
    created_at: datetime
    
    # Metrics
    retweet_count: int = 0
    like_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    
    # Tweet metadata
    tweet_type: str = "original"  # original, reply, retweet, quote
    hashtags: Optional[list[str]] = None
    mentions: Optional[list[str]] = None
    media_urls: Optional[list[str]] = None
    
    # Source tracking
    query_id: Optional[int] = None
    source: str = "x"
    original_url: Optional[str] = None
    scraped_at: Optional[datetime] = None

@dataclass(slots=True, frozen=True)
class MediaFile:
    id: Optional[int]
    tweet_id: str
    media_type: str  # photo, video
    original_url: str
    file_size: Optional[int] = None
    created_at: Optional[datetime] = None

@dataclass(slots=True, frozen=True)
class UserRecentTweet:
    id: Optional[int]
    user_id: str
    tweet_id: str
    text: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# Legacy entity for backward compatibility
@dataclass(slots=True, frozen=True)
class ScrapedPost:
    id: str                 # e.g., tweet id
    author: str
    text: str
    created_at: datetime
    source: str = "x"       # which platform/source
    url: Optional[str] = None

