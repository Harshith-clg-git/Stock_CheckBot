# 🚗 Hot Wheels Multi-Platform Stock Checker Bot

A modern, high-performance Hot Wheels stock checker bot built for quick-commerce and toy platforms (**Blinkit**, **Zepto**, **Swiggy Instamart**, **FirstCry**, **BigBasket**).

Powered by **GitHub Actions** (serverless 5-minute cron schedule) and **Telegram Bot API** (100% free instant push alerts with direct "🛒 Buy Now" links).

---

## 🌟 Key Features

- ⚡ **Zero-Cost 24/7 Execution**: Runs on **GitHub Actions** every 5 minutes without sleeping servers or hosting fees.
- 📱 **Instant Telegram Push Alerts**: Direct markdown alert cards with title, price, platform badge, priority tag, and buy link.
- 🏎️ **Smart Category Engine**: Prioritizes **Super Treasure Hunts (STH)**, **Treasure Hunts (TH)**, **JDM** (Skyline GT-R, Supra, Civic, RX-7), **Exotics** (Porsche, Lambo, Ferrari), and **Premium** (Boulevard, Car Culture).
- 🔄 **Deduplication & Restock DB**: Stores stock state in SQLite (`database.db`) so you only get alerts for **new items** or **restocked items**.

---

## 🚀 Quick Setup Guide

### Step 1: Create your Free Telegram Bot (30 Seconds)
1. Open Telegram and search for `@BotFather`.
2. Send `/newbot`, name your bot (e.g. `MyHotWheelsBot`), and save the **Bot Token** (`7123456789:AAFxxx...`).
3. Search for `@userinfobot` or `@raw_data_bot` to get your **Chat ID** (`123456789`).

### Step 2: Configure GitHub Repository Secrets
Push this repository to GitHub, then go to:
**Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions** $\rightarrow$ **New repository secret**:

| Secret Name | Required | Value |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | **Yes** | Your Telegram Bot Token from `@BotFather` |
| `TELEGRAM_CHAT_ID` | **Yes** | Your Telegram Chat ID from `@userinfobot` |
| `PROXY_SERVER` | *Optional (for Blinkit/Zepto/BigBasket on GitHub Actions)* | Indian Proxy URL (e.g. `http://103.x.x.x:8080` or `http://p.webshare.io:80`) |
| `PROXY_USERNAME` | *Optional* | Proxy username if authenticated |
| `PROXY_PASSWORD` | *Optional* | Proxy password if authenticated |

> [!NOTE]
> **Why is an Indian Proxy needed for Blinkit/Zepto/BigBasket on GitHub Actions?**
> Quick-commerce apps in India (Blinkit, Zepto, BigBasket) geo-fence their catalog to local dark stores and block overseas/datacenter cloud IPs (like GitHub Actions' US/EU servers).
> Adding an Indian proxy routes the scraper through India, allowing full access to Hyderabad inventory 24/7 on GitHub Actions with zero hosting costs.

---

## 💻 Local Testing & Manual Run

### Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### Run Dry-Run Tests
```bash
python test_bot.py
```

### Run Single Scan (Same mode as GitHub Actions)
```bash
python main.py --once
```

### Run Continuous Daemon Mode (Local / VPS)
```bash
python main.py --interval 300
```
