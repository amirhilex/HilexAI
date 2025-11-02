import os
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .infrastructure.db import get_session, Base, engine
from .adapters.db.repository import (
    SqlAlchemyPostRepository,
    SqlAlchemyQueryRepository,
    SqlAlchemyTwitterUserRepository,
    SqlAlchemyTweetRepository,
    SqlAlchemyMediaFileRepository,
    SqlAlchemyUserRecentTweetRepository,
)
from .adapters.scrapers.twikit_scraper import TwikitScraper
from .application.use_cases import ScrapeAndStorePostsUseCase, ExecuteQueryUseCase
from .domain.ports import (
    PostRepositoryPort, ScraperPort,
    QueryRepositoryPort, TwitterUserRepositoryPort, TweetRepositoryPort,
    MediaFileRepositoryPort, UserRecentTweetRepositoryPort,
)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# DI providers
async def get_repo(session: AsyncSession = Depends(get_session)) -> PostRepositoryPort:
    return SqlAlchemyPostRepository(session)

async def get_tweet_repo(session: AsyncSession = Depends(get_session)) -> TweetRepositoryPort:
    return SqlAlchemyTweetRepository(session)

async def get_query_repo(session: AsyncSession = Depends(get_session)) -> QueryRepositoryPort:
    return SqlAlchemyQueryRepository(session)

async def get_user_repo(session: AsyncSession = Depends(get_session)) -> TwitterUserRepositoryPort:
    return SqlAlchemyTwitterUserRepository(session)

async def get_media_repo(session: AsyncSession = Depends(get_session)) -> MediaFileRepositoryPort:
    return SqlAlchemyMediaFileRepository(session)

async def get_user_recent_repo(session: AsyncSession = Depends(get_session)) -> UserRecentTweetRepositoryPort:
    return SqlAlchemyUserRecentTweetRepository(session)

async def get_scraper() -> ScraperPort:
    return TwikitScraper()

def get_use_case(
    scraper: ScraperPort = Depends(get_scraper),
    repo: PostRepositoryPort = Depends(get_repo)
) -> ScrapeAndStorePostsUseCase:
    return ScrapeAndStorePostsUseCase(scraper, repo)

def get_execute_query_use_case(
    scraper: ScraperPort = Depends(get_scraper),
    query_repo: QueryRepositoryPort = Depends(get_query_repo),
    tweet_repo: TweetRepositoryPort = Depends(get_tweet_repo),
    user_repo: TwitterUserRepositoryPort = Depends(get_user_repo),
    media_repo: MediaFileRepositoryPort = Depends(get_media_repo),
    user_recent_repo: UserRecentTweetRepositoryPort = Depends(get_user_recent_repo),
) -> ExecuteQueryUseCase:
    return ExecuteQueryUseCase(
        scraper, query_repo, tweet_repo, user_repo, media_repo, user_recent_repo
    )

