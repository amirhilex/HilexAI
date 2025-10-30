import asyncio
import pandas as pd
from hex_twitter.adapters.twikit_scraper import TwikitScraper

async def main():
    scraper = TwikitScraper()
    tweets = await scraper.search_tweets("btc", limit=1000)

    df = pd.DataFrame([
        {**t.__dict__, "images": ", ".join(t.images) if t.images else ""}
        for t in tweets
    ])
    df.to_csv("tweets.csv", index=False, encoding="utf-8-sig")
    print("Saved tweets.csv")
    print("Images saved in images/ folder")

if __name__ == "__main__":
    asyncio.run(main())