# راهنمای اجرای پروژه در Google Colab

این پروژه یک FastAPI application است که نیاز به PostgreSQL دارد. در Google Colab باید تنظیمات خاصی انجام بدید.

## مراحل نصب و راه‌اندازی

### مرحله 1: نصب PostgreSQL در Colab

در ابتدای notebook خود این سلول‌ها رو اضافه کنید:

```python
# نصب PostgreSQL برای Colab
!apt-get update
!apt-get -y install postgresql postgresql-contrib > /dev/null
!service postgresql start

# تنظیم محیط PostgreSQL
!sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres123';"
!sudo -u postgres psql -c "CREATE DATABASE twitter_scraper;"

print("✅ PostgreSQL installed and configured!")
```

### مرحله 2: نصب وابستگی‌های پایتون

```python
# نصب پکیج‌های مورد نیاز
!pip install -q fastapi uvicorn[standard] pydantic SQLAlchemy asyncpg python-dotenv twikit aiohttp requests greenlet

print("✅ All packages installed!")
```

### مرحله 3: آپلود فایل‌های پروژه

```python
# اتصال به Google Drive (اختیاری)
from google.colab import drive
drive.mount('/content/drive')

# یا استفاده از file manager خود Colab
import os
os.chdir('/content')
```

بعد فایل‌های پروژه رو به Colab آپلود کنید:
- app/
- requirements.txt (البته قبلاً نصب کردیم)

### مرحله 4: تنظیم متغیرهای محیطی

```python
import os

# تنظیمات دیتابیس
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://postgres:postgres123@localhost:5432/twitter_scraper'

# تنظیمات Twikit (مهم: باید credentials خودتون رو بذارید!)
os.environ['TWIKIT_EMAIL'] = 'your_email@example.com'
os.environ['TWIKIT_USERNAME'] = 'your_twitter_username'
os.environ['TWIKIT_PASSWORD'] = 'your_password'

print("✅ Environment variables set!")
```

### مرحله 5: اجرای FastAPI با ngrok

Colab port forwarding مستقیم نداره، پس از ngrok استفاده می‌کنیم:

```python
# نصب ngrok
!pip install pyngrok

from pyngrok import ngrok
import uvicorn
import threading

# ایجاد tunnel
public_url = ngrok.connect(8000)
print(f"🌐 Your API is available at: {public_url}")

# اجرای FastAPI در background
def run_api():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

thread = threading.Thread(target=run_api, daemon=True)
thread.start()

print("✅ FastAPI is running!")
print(f"📖 API Docs: {public_url}/docs")
```

## تست API

```python
import requests

# تست health endpoint
response = requests.get(f"{public_url}/healthz")
print(response.json())

# تست ساخت query
query_data = {
    "name": "Test Query",
    "search_text": "#python",
    "is_active": True
}

response = requests.post(f"{public_url}/queries", json=query_data)
print("Created Query:", response.json())
```

## توجهات مهم

⚠️ **محدودیت‌های Colab:**
- Session بعد از ۹۰ دقیقه expire میشه
- هر بار باید دوباره setup کنید
- برای production مناسب نیست

🔒 **امنیت:**
- هرگز credentials رو public نکنید
- از notebooks عمومی استفاده نکنید

💡 **بهترین روش:**
اگر فقط میخواید scraping کنید، شاید بهتر باشه نسخه ساده‌تر بدون FastAPI استفاده کنید!

