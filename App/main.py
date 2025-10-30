import asyncio
from App.adapters.twikit_scraper import TwikitScraper
from App.adapters.csv_repository import CSVRepository

async def main():
    keyword = input("Enter search keyword: ").strip()
    limit = int(input("Enter the maximum number of tweets to fetch (limit): ").strip())
    count = int(input("Enter the number of tweets per request (count): ").strip())
    scraper = TwikitScraper()
    tweets = await scraper.search_tweets(keyword, limit=limit, count=count)
    repo = CSVRepository("tweets.csv")
    repo.save_many(tweets)

if __name__ == "__main__":
    asyncio.run(main())
