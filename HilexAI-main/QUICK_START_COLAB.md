# ⚡ راهنمای سریع اجرا در Colab

## 🎯 نسخه کامل (با FastAPI + PostgreSQL)

**برای استفاده کامل از API و ذخیره در دیتابیس:**

📄 فایل: `COLAB_GUIDE_FA.md` رو بخونید

**خلاصه:**
1. نصب PostgreSQL
2. نصب پکیج‌ها  
3. آپلود پروژه
4. تنظیم credentials
5. اجرا با ngrok

⏱️ زمان: 5-7 دقیقه

---

## 🧪 نسخه تست (بدون دیتابیس)

**فقط برای تست scraping:**

📄 فایل: `simple_colab_test.py` رو اجرا کنید

**کد ساده:**
```python
!pip install -q twikit

from twikit import Client

client = Client('en-US')
client.login(
    auth_info_1='your_email',
    auth_info_2='username',
    password='password'
)

tweets = client.search_tweet('#python', count=10)
for t in tweets:
    print(t.text)
```

⏱️ زمان: 1 دقیقه

---

## 📋 چیزهای ضروری

### باید پیکربندی کنید:

| مورد | توضیح | از کجا |
|------|-------|--------|
| **TWIKIT_EMAIL** | ایمیل توییتر | اکانت توییتر |
| **TWIKIT_USERNAME** | یوزرنیم | اکانت توییتر |
| **TWIKIT_PASSWORD** | پسورد | اکانت توییتر |
| **DATABASE_URL** | ادرس دیتابیس | PostgreSQL |
| **ngrok token** | Token ngrok | ngrok.com |

### اختیاری:

- Google Drive برای ذخیره نتایج
- ngrok Pro برای tunnel پایدارتر
- GPU runtime برای سرعت بیشتر

---

## 🚀 شروع سریع (Copy-Paste Ready)

```python
# سلول 1: Setup
!apt-get -qq update && apt-get -qq install postgresql
!service postgresql start
!sudo -u postgres psql -c "CREATE DATABASE twitter_scraper;"

# سلول 2: Install
!pip install -q fastapi uvicorn SQLAlchemy asyncpg twikit pyngrok

# سلول 3: Config
import os
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://postgres:@localhost:5432/twitter_scraper'
os.environ['TWIKIT_EMAIL'] = 'YOUR_EMAIL'
os.environ['TWIKIT_USERNAME'] = 'YOUR_USERNAME'
os.environ['TWIKIT_PASSWORD'] = 'YOUR_PASSWORD'

# سلول 4: Run
from pyngrok import ngrok
import uvicorn, threading
ngrok.connect(8000)
def r(): uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
threading.Thread(target=r, daemon=True).start()
```

**حالا API در /docs در دسترس است!**

---

📖 برای راهنمای کامل: `COLAB_GUIDE_FA.md` رو ببینید

