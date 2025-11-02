"""
نسخه ساده برای تست سریع در Colab بدون FastAPI
این فایل فقط scraping رو تست می‌کنه
"""

# ===== نصب پکیج‌ها (سلول 1) =====
# !pip install -q twikit python-dotenv

# ===== تنظیم Credentials (سلول 2) =====
import os
os.environ['TWIKIT_EMAIL'] = 'your_email@gmail.com'
os.environ['TWIKIT_USERNAME'] = 'your_username'
os.environ['TWIKIT_PASSWORD'] = 'your_password'

# ===== تست ساده Scraper (سلول 3) =====
from twikit import Client
import asyncio

async def test_scraper():
    client = Client('en-US')
    
    # Login
    await client.login(
        auth_info_1=os.environ['TWIKIT_EMAIL'],
        auth_info_2=os.environ['TWIKIT_USERNAME'],
        password=os.environ['TWIKIT_PASSWORD']
    )
    
    # Search
    tweets = client.search_tweet('#python', count=10)
    
    # نمایش نتایج
    for i, tweet in enumerate(tweets, 1):
        print(f"\n{i}. @{tweet.user.screen_name}")
        print(f"   {tweet.text[:100]}")
        print(f"   Likes: {tweet.favorite_count} | RTs: {tweet.retweet_count}")
    
    return tweets

# اجرا
results = asyncio.run(test_scraper())
print(f"\n✅ {len(results)} توییت پیدا شد!")


