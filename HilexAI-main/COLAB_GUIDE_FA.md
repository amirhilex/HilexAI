# 🚀 راهنمای کامل اجرای پروژه در Google Colab

این پروژه یک Twitter Scraper با FastAPI و PostgreSQL است. برای اجرا در Colab به تنظیمات خاصی نیاز دارید.

---

## ⚙️ چیزهایی که باید پیکربندی کنید:

### 1️⃣ **PostgreSQL Database**
- باید PostgreSQL نصب و راه‌اندازی بشه
- یک دیتابیس بسازید

### 2️⃣ **Credentials توییتر**
- TWIKIT_EMAIL
- TWIKIT_USERNAME  
- TWIKIT_PASSWORD

### 3️⃣ **Port Forwarding**
- Colab به صورت مستقیم port forwarding نداره
- باید از ngrok استفاده کنید

---

## 📝 مراحل کامل نصب و اجرا

### **مرحله 1: ایجاد Notebook جدید**

1. برید به [Google Colab](https://colab.research.google.com)
2. New Notebook بسازید
3. Runtime Type رو **Python 3** انتخاب کنید

---

### **مرحله 2: نصب PostgreSQL**

**سلول 1 رو اجرا کنید:**
```python
# نصب و راه‌اندازی PostgreSQL
!apt-get update
!apt-get -y install postgresql postgresql-contrib > /dev/null
!service postgresql start

# تنظیم پسورد و ساخت دیتابیس
!sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres123';"
!sudo -u postgres psql -c "CREATE DATABASE twitter_scraper;"

print("✅ PostgreSQL نصب و راه‌اندازی شد!")
```

⏱️ زمان: حدود 1-2 دقیقه

---

### **مرحله 3: نصب پکیج‌های پایتون**

**سلول 2 رو اجرا کنید:**
```python
# نصب تمام وابستگی‌ها
!pip install -q fastapi uvicorn[standard] pydantic SQLAlchemy asyncpg python-dotenv twikit aiohttp requests greenlet

print("✅ تمام پکیج‌ها نصب شدند!")
```

⏱️ زمان: حدود 2-3 دقیقه

---

### **مرحله 4: آپلود فایل‌های پروژه**

**گزینه A: استفاده از Google Drive**

```python
# اتصال به Google Drive
from google.colab import drive
drive.mount('/content/drive')

# کپی فایل‌های پروژه
!cp -r '/content/drive/MyDrive/HilexAI-main' /content/
```

**گزینه B: استفاده از file manager**

1. از منوی سمت چپ **📁 Files** رو باز کنید
2. دکمه **⬆️ Upload** رو بزنید
3. پوشه `app` رو آپلود کنید
4. یا کل پروژه رو ZIP کنید و آپلود کنید

**گزینه C: دانلود از GitHub (اگه push کردید)**

```python
!git clone YOUR_GITHUB_REPO_URL
```

---

### **مرحله 5: تنظیم Credentials**

**سلول 3 رو اجرا کنید:**
```python
import os

# تنظیمات دیتابیس
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://postgres:postgres123@localhost:5432/twitter_scraper'

# 🚨 مهم: اطلاعات توییتر خودتون رو وارد کنید!
os.environ['TWIKIT_EMAIL'] = 'your_email@gmail.com'  # ایمیل خودتون
os.environ['TWIKIT_USERNAME'] = 'your_username'  # یوزرنیم توییتر
os.environ['TWIKIT_PASSWORD'] = 'your_password'  # پسورد توییتر

print("✅ متغیرهای محیطی تنظیم شدند!")
```

⚠️ **توجه:** هرگز credentials رو public نکنید!

---

### **مرحله 6: اجرای FastAPI با ngrok**

**سلول 4 رو اجرا کنید:**
```python
# نصب ngrok
!pip install -q pyngrok

from pyngrok import ngrok
import uvicorn
import threading

# ایجاد tunnel عمومی
public_url = ngrok.connect(8000)
print(f"🌐 API شما در آدرس زیر در دسترس است:")
print(f"{public_url}")

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

# منتظر می‌مونیم تا API بالا بیاد
import time
time.sleep(5)

print("\n✅ FastAPI اجرا شد!")
print(f"📖 مستندات API: {public_url}/docs")
print(f"🔍 تست سلامت: {public_url}/healthz")
```

⏱️ زمان: 10-15 ثانیه

---

### **مرحله 7: تست API**

**سلول 5 رو اجرا کنید:**
```python
import requests

# تست سلامت سرور
health_url = f"{public_url}/healthz"
response = requests.get(health_url)
print("Health Check:", response.json())

# ساخت یک query جدید
query_data = {
    "name": "Test Python Search",
    "search_text": "#python OR #coding",
    "is_active": True
}

create_url = f"{public_url}/queries"
response = requests.post(create_url, json=query_data)
print("\nCreated Query:")
print(response.json())
```

---

## 🧪 مثال‌های استفاده

### **ساخت Query**
```python
query = {
    "name": "AI News",
    "search_text": "#AI OR #MachineLearning",
    "is_active": True
}
response = requests.post(f"{public_url}/queries", json=query)
query_id = response.json()['id']
print(f"Query ID: {query_id}")
```

### **اجرای Query و اسکرپ**
```python
execute_data = {
    "query_id": query_id,
    "limit": 50,
    "include_media": True,
    "update_user_profiles": True
}
response = requests.post(f"{public_url}/scrape/execute", json=execute_data)
print(response.json())
```

### **مشاهده نتایج**
```python
# لیست آخرین توییت‌ها
response = requests.get(f"{public_url}/scrape/tweets/recent")
tweets = response.json()
print(f"تعداد توییت‌ها: {len(tweets)}")
for tweet in tweets[:5]:
    print(f"- {tweet['text'][:100]}...")
```

---

## ⚠️ محدودیت‌های Google Colab

| محدودیت | توضیح | راه‌حل |
|---------|-------|--------|
| **Session** | بعد از ۹۰ دقیقه expire میشه | دوباره اجرا کنید |
| **RAM** | محدود به سایز notebook | GPU runtime استفاده کنید |
| **Persistent** | فایل‌ها ذخیره نمیمونن | از Drive استفاده کنید |
| **ngrok Free** | 8 ساعت محدودیت داره | tunnel جدید بسازید |

---

## 🐛 رفع مشکلات

### **خطا: "Cannot connect to database"**
```python
# بررسی که PostgreSQL اجرا شده
!service postgresql status

# راه‌اندازی مجدد
!service postgresql restart
```

### **خطا: "Module not found"**
```python
# نصب مجدد پکیج‌ها
!pip install --force-reinstall fastapi SQLAlchemy asyncpg twikit
```

### **خطا: "Authentication failed"**
- Credentials توییتر رو دوباره چک کنید
- مطمئن بشید که 2FA فعال نیست
- یا از auth_token استفاده کنید

---

## 💡 نکات مهم

✅ **بهترین کارها:**
- هر سلول رو جداگانه اجرا کنید
- بعد از هر سلول منتظر completion بمانید
- ngrok URL رو کپی کنید
- از `/docs` برای تست API استفاده کنید

❌ **از این‌ها دوری کنید:**
- اجرای همزمان سلول‌ها
- اشتراک‌گذاری credentials
- اتصال به دیتابیس خارجی بدون فایروال
- استفاده از production data

---

## 🎯 خلاصه مراحل

1. ✅ نصب PostgreSQL
2. ✅ نصب پکیج‌ها
3. ✅ آپلود پروژه
4. ✅ تنظیم credentials
5. ✅ اجرای ngrok + FastAPI
6. ✅ تست API
7. ✅ استفاده!

---

**سوالی دارید؟** Issues بسازید یا مستندات FastAPI رو بخونید: https://fastapi.tiangolo.com

