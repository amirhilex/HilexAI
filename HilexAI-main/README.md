# Twitter Scraper Service

This service scrapes tweets, stores them in PostgreSQL, and provides a dashboard-ready API to manage search queries and run scheduled extractions.

## Key features
- Define and manage saved queries (keywords, hashtags, filters, schedule)
- ELT pipeline: extract from Twitter (via twikit), load into PostgreSQL, transform/normalize
- Store users and their last 3 tweets
- Store media file references in the database

## API overview

- POST /scrape
	- Legacy scrape for ad-hoc query: body { query, limit }

- GET /scrape/recent
	- Legacy list of recent posts (legacy model)

- POST /scrape/execute
	- Execute a saved query: { query_id, limit, include_media, update_user_profiles }

- GET /scrape/tweets/recent
	- List recent tweets (new Tweet model)

- POST /queries
	- Create a query definition

- GET /queries/{id}
	- Get a query by id

- GET /queries
	- List active queries

- PATCH /queries/{id}
	- Update a query

- DELETE /queries/{id}
	- Delete a query

## Database
Tables are auto-created on startup using SQLAlchemy metadata.

## Twitter Authentication
Set the following environment variables:
- TWIKIT_EMAIL
- TWIKIT_USERNAME
- TWIKIT_PASSWORD

## Running with Docker

```bash
docker-compose up
```

The API will be available at http://localhost:8000

## Running locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Running in Google Colab

برای اجرا در Google Colab، راهنمای کامل فارسی را ببینید:

📖 **[QUICK_START_COLAB.md](QUICK_START_COLAB.md)** - شروع سریع  
📚 **[COLAB_GUIDE_FA.md](COLAB_GUIDE_FA.md)** - راهنمای کامل فارسی

