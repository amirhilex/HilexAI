from typing import Optional, Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ...domain.entities import (
    ScrapedPost,
    Query, TwitterUser, Tweet, MediaFile, UserRecentTweet,
)
from ...domain.ports import (
    PostRepositoryPort,
    QueryRepositoryPort, TwitterUserRepositoryPort,
    TweetRepositoryPort, MediaFileRepositoryPort, UserRecentTweetRepositoryPort,
)
from .models import (
    PostORM, QueryORM, UserORM, TweetORM, MediaFileORM, UserRecentTweetORM,
)

class SqlAlchemyPostRepository(PostRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save_many(self, posts: list[ScrapedPost]) -> int:
        if not posts:
            return 0
        # Avoid duplicates: fetch existing ids
        ids = [p.id for p in posts]
        existing = set((await self._session.execute(
            select(PostORM.id).where(PostORM.id.in_(ids))
        )).scalars().all())
        to_insert = [p for p in posts if p.id not in existing]

        for p in to_insert:
            self._session.add(PostORM(
                id=p.id, author=p.author, text=p.text,
                created_at=p.created_at, source=p.source, url=p.url
            ))
        await self._session.commit()
        return len(to_insert)

    async def get_by_id(self, post_id: str) -> Optional[ScrapedPost]:
        res = await self._session.get(PostORM, post_id)
        if not res:
            return None
        return ScrapedPost(
            id=res.id, author=res.author, text=res.text,
            created_at=res.created_at, source=res.source, url=res.url
        )

    async def list_recent(self, limit: int = 50) -> list[ScrapedPost]:
        q = select(PostORM).order_by(PostORM.created_at.desc()).limit(limit)
        rows = (await self._session.execute(q)).scalars().all()
        return [
            ScrapedPost(
                id=r.id, author=r.author, text=r.text,
                created_at=r.created_at, source=r.source, url=r.url
            )
            for r in rows
        ]


class SqlAlchemyQueryRepository(QueryRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, query: Query) -> Query:
        if query.id:
            await self._session.execute(
                update(QueryORM)
                .where(QueryORM.id == query.id)
                .values(
                    name=query.name,
                    search_text=query.search_text,
                    filters=query.filters,
                    schedule_interval=query.schedule_interval,
                    is_active=query.is_active,
                )
            )
            await self._session.commit()
            db_obj = await self._session.get(QueryORM, query.id)
        else:
            db_obj = QueryORM(
                name=query.name,
                search_text=query.search_text,
                filters=query.filters,
                schedule_interval=query.schedule_interval,
                is_active=query.is_active,
            )
            self._session.add(db_obj)
            await self._session.commit()
            await self._session.refresh(db_obj)
        return Query(
            id=db_obj.id,
            name=db_obj.name,
            search_text=db_obj.search_text,
            filters=db_obj.filters,
            schedule_interval=db_obj.schedule_interval,
            is_active=db_obj.is_active,
            created_at=db_obj.created_at,
            last_run_at=db_obj.last_run_at,
        )

    async def get_by_id(self, query_id: int) -> Optional[Query]:
        db = await self._session.get(QueryORM, query_id)
        if not db:
            return None
        return Query(
            id=db.id,
            name=db.name,
            search_text=db.search_text,
            filters=db.filters,
            schedule_interval=db.schedule_interval,
            is_active=db.is_active,
            created_at=db.created_at,
            last_run_at=db.last_run_at,
        )

    async def list_active(self) -> list[Query]:
        rows = (await self._session.execute(select(QueryORM).where(QueryORM.is_active == True))).scalars().all()
        return [
            Query(
                id=r.id,
                name=r.name,
                search_text=r.search_text,
                filters=r.filters,
                schedule_interval=r.schedule_interval,
                is_active=r.is_active,
                created_at=r.created_at,
                last_run_at=r.last_run_at,
            )
            for r in rows
        ]

    async def update_last_run(self, query_id: int, timestamp) -> None:
        await self._session.execute(
            update(QueryORM).where(QueryORM.id == query_id).values(last_run_at=timestamp)
        )
        await self._session.commit()

    async def delete(self, query_id: int) -> bool:
        res = await self._session.execute(delete(QueryORM).where(QueryORM.id == query_id))
        await self._session.commit()
        return res.rowcount > 0


class SqlAlchemyTwitterUserRepository(TwitterUserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: TwitterUser) -> TwitterUser:
        existing = await self._session.get(UserORM, user.user_id)
        if existing:
            existing.username = user.username
            existing.display_name = user.display_name
            existing.bio = user.bio
            existing.followers_count = user.followers_count
            existing.following_count = user.following_count
            existing.profile_image_url = user.profile_image_url
            existing.header_image_url = user.header_image_url
            existing.location = user.location
            existing.auto_update = user.auto_update
            self._session.add(existing)
        else:
            self._session.add(UserORM(
                user_id=user.user_id,
                username=user.username,
                display_name=user.display_name,
                bio=user.bio,
                followers_count=user.followers_count,
                following_count=user.following_count,
                profile_image_url=user.profile_image_url,
                header_image_url=user.header_image_url,
                location=user.location,
                auto_update=user.auto_update,
            ))
        await self._session.commit()
        db = await self._session.get(UserORM, user.user_id)
        return TwitterUser(
            user_id=db.user_id,
            username=db.username,
            display_name=db.display_name,
            bio=db.bio,
            followers_count=db.followers_count,
            following_count=db.following_count,
            profile_image_url=db.profile_image_url,
            header_image_url=db.header_image_url,
            location=db.location,
            auto_update=db.auto_update,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )

    async def get_by_id(self, user_id: str) -> Optional[TwitterUser]:
        db = await self._session.get(UserORM, user_id)
        if not db:
            return None
        return TwitterUser(
            user_id=db.user_id,
            username=db.username,
            display_name=db.display_name,
            bio=db.bio,
            followers_count=db.followers_count,
            following_count=db.following_count,
            profile_image_url=db.profile_image_url,
            header_image_url=db.header_image_url,
            location=db.location,
            auto_update=db.auto_update,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )

    async def get_by_username(self, username: str) -> Optional[TwitterUser]:
        row = (await self._session.execute(select(UserORM).where(UserORM.username == username))).scalar_one_or_none()
        if not row:
            return None
        return TwitterUser(
            user_id=row.user_id,
            username=row.username,
            display_name=row.display_name,
            bio=row.bio,
            followers_count=row.followers_count,
            following_count=row.following_count,
            profile_image_url=row.profile_image_url,
            header_image_url=row.header_image_url,
            location=row.location,
            auto_update=row.auto_update,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def list_for_auto_update(self) -> list[TwitterUser]:
        rows = (await self._session.execute(select(UserORM).where(UserORM.auto_update == True))).scalars().all()
        return [
            TwitterUser(
                user_id=r.user_id,
                username=r.username,
                display_name=r.display_name,
                bio=r.bio,
                followers_count=r.followers_count,
                following_count=r.following_count,
                profile_image_url=r.profile_image_url,
                header_image_url=r.header_image_url,
                location=r.location,
                auto_update=r.auto_update,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in rows
        ]

    async def update_profile(self, user: TwitterUser) -> TwitterUser:
        return await self.save(user)


class SqlAlchemyTweetRepository(TweetRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save_many(self, tweets: list[Tweet]) -> int:
        if not tweets:
            return 0
        ids = [t.tweet_id for t in tweets]
        existing = set((await self._session.execute(
            select(TweetORM.tweet_id).where(TweetORM.tweet_id.in_(ids))
        )).scalars().all())
        to_insert = [t for t in tweets if t.tweet_id not in existing]
        for t in to_insert:
            self._session.add(TweetORM(
                tweet_id=t.tweet_id,
                text=t.text,
                author_id=t.author_id,
                created_at=t.created_at,
                retweet_count=t.retweet_count,
                like_count=t.like_count,
                reply_count=t.reply_count,
                quote_count=t.quote_count,
                tweet_type=t.tweet_type,
                hashtags=t.hashtags,
                mentions=t.mentions,
                media_urls=t.media_urls,
                query_id=t.query_id,
                source=t.source,
                original_url=t.original_url,
                scraped_at=t.scraped_at,
            ))
        await self._session.commit()
        return len(to_insert)

    async def get_by_id(self, tweet_id: str) -> Optional[Tweet]:
        db = await self._session.get(TweetORM, tweet_id)
        if not db:
            return None
        return Tweet(
            tweet_id=db.tweet_id,
            text=db.text,
            author_id=db.author_id,
            created_at=db.created_at,
            retweet_count=db.retweet_count,
            like_count=db.like_count,
            reply_count=db.reply_count,
            quote_count=db.quote_count,
            tweet_type=db.tweet_type,
            hashtags=db.hashtags,
            mentions=db.mentions,
            media_urls=db.media_urls,
            query_id=db.query_id,
            source=db.source,
            original_url=db.original_url,
            scraped_at=db.scraped_at,
        )

    async def list_by_query(self, query_id: int, limit: int = 100) -> list[Tweet]:
        rows = (await self._session.execute(
            select(TweetORM).where(TweetORM.query_id == query_id).order_by(TweetORM.created_at.desc()).limit(limit)
        )).scalars().all()
        return [
            Tweet(
                tweet_id=r.tweet_id,
                text=r.text,
                author_id=r.author_id,
                created_at=r.created_at,
                retweet_count=r.retweet_count,
                like_count=r.like_count,
                reply_count=r.reply_count,
                quote_count=r.quote_count,
                tweet_type=r.tweet_type,
                hashtags=r.hashtags,
                mentions=r.mentions,
                media_urls=r.media_urls,
                query_id=r.query_id,
                source=r.source,
                original_url=r.original_url,
                scraped_at=r.scraped_at,
            )
            for r in rows
        ]

    async def list_recent(self, limit: int = 50) -> list[Tweet]:
        rows = (await self._session.execute(
            select(TweetORM).order_by(TweetORM.created_at.desc()).limit(limit)
        )).scalars().all()
        return [
            Tweet(
                tweet_id=r.tweet_id,
                text=r.text,
                author_id=r.author_id,
                created_at=r.created_at,
                retweet_count=r.retweet_count,
                like_count=r.like_count,
                reply_count=r.reply_count,
                quote_count=r.quote_count,
                tweet_type=r.tweet_type,
                hashtags=r.hashtags,
                mentions=r.mentions,
                media_urls=r.media_urls,
                query_id=r.query_id,
                source=r.source,
                original_url=r.original_url,
                scraped_at=r.scraped_at,
            )
            for r in rows
        ]

    async def get_duplicates(self, tweet_ids: list[str]) -> set[str]:
        rows = (await self._session.execute(
            select(TweetORM.tweet_id).where(TweetORM.tweet_id.in_(tweet_ids))
        )).scalars().all()
        return set(rows)


class SqlAlchemyMediaFileRepository(MediaFileRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, media_file: MediaFile) -> MediaFile:
        db = MediaFileORM(
            tweet_id=media_file.tweet_id,
            media_type=media_file.media_type,
            original_url=media_file.original_url,
            file_size=media_file.file_size,
        )
        self._session.add(db)
        await self._session.commit()
        await self._session.refresh(db)
        return MediaFile(
            id=db.id,
            tweet_id=db.tweet_id,
            media_type=db.media_type,
            original_url=db.original_url,
            file_size=db.file_size,
            created_at=db.created_at,
        )

    async def get_by_tweet(self, tweet_id: str) -> list[MediaFile]:
        rows = (await self._session.execute(select(MediaFileORM).where(MediaFileORM.tweet_id == tweet_id))).scalars().all()
        return [
            MediaFile(
                id=r.id,
                tweet_id=r.tweet_id,
                media_type=r.media_type,
                original_url=r.original_url,
                file_size=r.file_size,
                created_at=r.created_at,
            )
            for r in rows
        ]

    async def save_many(self, media_files: list[MediaFile]) -> int:
        for m in media_files:
            self._session.add(MediaFileORM(
                tweet_id=m.tweet_id,
                media_type=m.media_type,
                original_url=m.original_url,
                file_size=m.file_size,
            ))
        await self._session.commit()
        return len(media_files)


class SqlAlchemyUserRecentTweetRepository(UserRecentTweetRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save_user_tweets(self, user_id: str, tweets: list[UserRecentTweet]) -> int:
        # simple approach: delete existing, insert new
        await self._session.execute(delete(UserRecentTweetORM).where(UserRecentTweetORM.user_id == user_id))
        for t in tweets[:3]:
            self._session.add(UserRecentTweetORM(
                user_id=user_id,
                tweet_id=t.tweet_id,
                text=t.text,
                created_at=t.created_at,
            ))
        await self._session.commit()
        return min(3, len(tweets))

    async def get_by_user(self, user_id: str) -> list[UserRecentTweet]:
        rows = (await self._session.execute(
            select(UserRecentTweetORM).where(UserRecentTweetORM.user_id == user_id).order_by(UserRecentTweetORM.created_at.desc()).limit(3)
        )).scalars().all()
        return [
            UserRecentTweet(
                id=r.id,
                user_id=r.user_id,
                tweet_id=r.tweet_id,
                text=r.text,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in rows
        ]

