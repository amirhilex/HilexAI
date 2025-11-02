from fastapi import APIRouter, Depends
from ....schemas import ScrapeRequest, ScrapeResult, PostResponse, EnhancedScrapeRequest, TweetResponse
from ....application.use_cases import ScrapeAndStorePostsUseCase, ExecuteQueryUseCase
from ....domain.ports import PostRepositoryPort, TweetRepositoryPort
from ....config import (
    get_use_case as get_legacy_use_case,
    get_execute_query_use_case,
    get_tweet_repo,
    get_repo,
)

router = APIRouter(prefix="/scrape", tags=["scrape"])

@router.post("", response_model=ScrapeResult)
async def scrape(
    payload: ScrapeRequest,
    use_case: ScrapeAndStorePostsUseCase = Depends(get_legacy_use_case),
):
    return await use_case.execute(query=payload.query, limit=payload.limit)

@router.get("/recent", response_model=list[PostResponse])
async def list_recent(repo: PostRepositoryPort = Depends(get_repo)):
    posts = await repo.list_recent(limit=50)
    return [PostResponse(**p.__dict__) for p in posts]


@router.post("/execute", response_model=ScrapeResult)
async def execute_query(
    payload: EnhancedScrapeRequest,
    use_case: ExecuteQueryUseCase = Depends(get_execute_query_use_case),
):
    return await use_case.execute(
        query_id=payload.query_id,
        limit=payload.limit,
        include_media=payload.include_media,
        update_user_profiles=payload.update_user_profiles,
    )

@router.get("/tweets/recent", response_model=list[TweetResponse])
async def list_recent_tweets(repo: TweetRepositoryPort = Depends(get_tweet_repo)):
    tweets = await repo.list_recent(limit=50)
    return [TweetResponse(**t.__dict__) for t in tweets]

