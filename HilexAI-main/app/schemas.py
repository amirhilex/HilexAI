from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

# Query Management Schemas
class QueryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    search_text: str = Field(..., min_length=1)
    filters: Optional[dict] = None
    schedule_interval: Optional[str] = None
    is_active: bool = True

class QueryUpdateRequest(BaseModel):
    name: Optional[str] = None
    search_text: Optional[str] = None
    filters: Optional[dict] = None
    schedule_interval: Optional[str] = None
    is_active: Optional[bool] = None

class QueryResponse(BaseModel):
    id: int
    name: str
    search_text: str
    filters: Optional[dict] = None
    schedule_interval: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_run_at: Optional[datetime] = None

# Twitter User Schemas
class TwitterUserResponse(BaseModel):
    user_id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    followers_count: int
    following_count: int
    profile_image_url: Optional[str] = None
    header_image_url: Optional[str] = None
    location: Optional[str] = None
    auto_update: bool
    created_at: datetime
    updated_at: datetime

class UserUpdateRequest(BaseModel):
    auto_update: bool

# Tweet Schemas
class TweetResponse(BaseModel):
    tweet_id: str
    text: str
    author_id: str
    created_at: datetime
    retweet_count: int
    like_count: int
    reply_count: int
    quote_count: int
    tweet_type: str
    hashtags: Optional[list[str]] = None
    mentions: Optional[list[str]] = None
    media_urls: Optional[list[str]] = None
    query_id: Optional[int] = None
    source: str
    original_url: Optional[str] = None
    scraped_at: datetime

class MediaFileResponse(BaseModel):
    id: int
    tweet_id: str
    media_type: str
    original_url: str
    file_size: Optional[int] = None
    created_at: datetime

class UserRecentTweetResponse(BaseModel):
    id: int
    user_id: str
    tweet_id: str
    text: str
    created_at: datetime
    updated_at: datetime

# Enhanced Scraping Schemas
class EnhancedScrapeRequest(BaseModel):
    query_id: int = Field(..., description="ID of the query to execute")
    limit: int = Field(20, ge=1, le=1000)
    include_media: bool = Field(True, description="Whether to download and store media files")
    update_user_profiles: bool = Field(True, description="Whether to update user profile information")

class ScrapeResult(BaseModel):
    found: int
    saved: int
    media_files_saved: int = 0
    users_updated: int = 0
    query_id: Optional[int] = None

class BulkScrapeRequest(BaseModel):
    queries: list[int] = Field(..., description="List of query IDs to execute")
    limit_per_query: int = Field(50, ge=1, le=1000)
    include_media: bool = True
    update_user_profiles: bool = True

class DashboardStatsResponse(BaseModel):
    total_queries: int
    active_queries: int
    total_tweets: int
    total_users: int
    media_files_stored: int
    last_24h_tweets: int

# Legacy schemas for backward compatibility
class ScrapeRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(20, ge=1, le=100)

class PostResponse(BaseModel):
    id: str
    author: str
    text: str
    created_at: datetime
    source: str
    url: str | None = None

