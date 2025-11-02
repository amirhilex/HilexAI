"""
این فایل برای اجرای پروژه در Google Colab ساخته شده
"""

# ==================== سلول 1: نصب PostgreSQL ====================
# این سلول رو اول اجرا کنید

# !apt-get update
# !apt-get -y install postgresql postgresql-contrib
# !service postgresql start
# !sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres123';"
# !sudo -u postgres psql -c "CREATE DATABASE twitter_scraper;"
# print("✅ PostgreSQL installed!")

# ==================== سلول 2: نصب پکیج‌ها ====================
# !pip install -q fastapi uvicorn[standard] pydantic SQLAlchemy asyncpg python-dotenv twikit aiohttp requests greenlet
# print("✅ Packages installed!")

# ==================== سلول 3: تنظیم متغیرها ====================
import os
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://postgres:postgres123@localhost:5432/twitter_scraper'
os.environ['TWIKIT_EMAIL'] = 'your_email@example.com'  # تغییر بدید!
os.environ['TWIKIT_USERNAME'] = 'your_username'  # تغییر بدید!
os.environ['TWIKIT_PASSWORD'] = 'your_password'  # تغییر بدید!
print("✅ Environment variables set!")

# ==================== سلول 4: اجرای API با ngrok ====================
# !pip install -q pyngrok

# from pyngrok import ngrok
# import uvicorn
# import threading

# public_url = ngrok.connect(8000)
# print(f"🌐 API URL: {public_url}")

# def run_api():
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000)

# thread = threading.Thread(target=run_api, daemon=True)
# thread.start()
# print("✅ FastAPI running!")
# print(f"📖 Docs: {public_url}/docs")

