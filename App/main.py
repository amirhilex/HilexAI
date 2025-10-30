import asyncio
from adapters.twikit_scraper import TwikitScraper
from adapters.csv_repository import CSVRepository

async def main():
    scraper = TwikitScraper()
    tweets = await scraper.search_tweets("btc", limit=100)
    repo = CSVRepository("tweets.csv")
    repo.save_many(tweets)

if __name__ == "__main__":
    asyncio.run(main())
