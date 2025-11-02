from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Integer, Boolean, Text, ForeignKey, JSON
from ...infrastructure.db import Base

class QueryORM(Base):
    """Query definitions created in dashboard"""
    __tablename__ = "queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    search_text: Mapped[str] = mapped_column(Text, nullable=False)  # keywords, hashtags, mentions
    filters: Mapped[dict] = mapped_column(JSON, nullable=True)  # date, language, tweet type filters
    schedule_interval: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g., "6h", "daily"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationship to tweets
    tweets: Mapped[list["TweetORM"]] = relationship("TweetORM", back_populates="query")

class UserORM(Base):
    """Twitter user profiles"""
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)  # Twitter user_id
    username: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    following_count: Mapped[int] = mapped_column(Integer, default=0)
    profile_image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    header_image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    auto_update: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tweets: Mapped[list["TweetORM"]] = relationship("TweetORM", back_populates="author")
    recent_tweets: Mapped[list["UserRecentTweetORM"]] = relationship("UserRecentTweetORM", back_populates="user")

class TweetORM(Base):
    """Tweet data with enhanced fields"""
    __tablename__ = "tweets"

    tweet_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.user_id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    # Metrics
    retweet_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    quote_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Tweet type and content
    tweet_type: Mapped[str] = mapped_column(String(20), default="original")  # original, reply, retweet, quote
    hashtags: Mapped[list] = mapped_column(JSON, nullable=True)  # List of hashtags
    mentions: Mapped[list] = mapped_column(JSON, nullable=True)  # List of mentioned users
    media_urls: Mapped[list] = mapped_column(JSON, nullable=True)  # List of media URLs
    
    # Source tracking
    query_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("queries.id"), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(32), default="x")
    original_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    
    # Timestamps
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    author: Mapped["UserORM"] = relationship("UserORM", back_populates="tweets")
    query: Mapped["QueryORM"] = relationship("QueryORM", back_populates="tweets")
    media_files: Mapped[list["MediaFileORM"]] = relationship("MediaFileORM", back_populates="tweet")

class MediaFileORM(Base):
    """Media files"""
    __tablename__ = "media_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tweet_id: Mapped[str] = mapped_column(String(64), ForeignKey("tweets.tweet_id"), nullable=False, index=True)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)  # photo, video
    original_url: Mapped[str] = mapped_column(String(512), nullable=False)  # Original Twitter URL
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)  # File size in bytes
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationship
    tweet: Mapped["TweetORM"] = relationship("TweetORM", back_populates="media_files")

class UserRecentTweetORM(Base):
    """Last 3 tweets for each user"""
    __tablename__ = "user_recent_tweets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.user_id"), nullable=False, index=True)
    tweet_id: Mapped[str] = mapped_column(String(64), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationship
    user: Mapped["UserORM"] = relationship("UserORM", back_populates="recent_tweets")

# Legacy model for backward compatibility (can be removed later)
class PostORM(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    author: Mapped[str] = mapped_column(String(255), index=True)
    text: Mapped[str] = mapped_column(String(10240))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source: Mapped[str] = mapped_column(String(32))
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)

