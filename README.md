# 🚗 Hot Wheels Multi-Platform Stock Checker Bot

A high-performance Hot Wheels stock checker bot built for quick-commerce and retail platforms (**Blinkit**, **Zepto**, **FirstCry**, **BigBasket**).

Optimized for **24/7 local execution on Raspberry Pi 5** using native network routing, continuous daemon scheduling, and instant **Telegram Bot API** alerts.

---

## 🌟 Key Features

- 🍓 **Native 24/7 Raspberry Pi 5 Execution**: Runs locally without timeouts, serverless limits, or cloud IP geo-blocks.
- 📍 **No Proxies Required**: Direct Indian ISP connection allows seamless dark-store inventory access for quick commerce.
- 📱 **Instant Telegram Push Alerts**: Rich markdown cards with product title, price, platform badge, priority tags, and direct buy links.
- 🏎️ **Smart Category Engine**: Prioritizes **Super Treasure Hunts (STH)**, **Treasure Hunts (TH)**, **JDM** (Skyline GT-R, Supra, Civic, RX-7), **Exotics** (Porsche, Lambo, Ferrari), and **Premium** (Boulevard, Car Culture).
- 🔄 **Local SQLite Persistence**: Tracks stock status in `database.db` so you only get alerts for **brand new drops** or **restocked items**.
- ⚙️ **Auto-Restart & Resilience**: Pre-configured `systemd` service and `docker-compose` ensure 100% uptime through power cycles and network drops.

---

## 🚀 Raspberry Pi 5 Quick Start (Recommended)

### Option A: 1-Command Automated Setup (Systemd Service)

1. **Clone the repository on your Raspberry Pi:**
   ```bash
   git clone <your-repo-url> Hotwheels_bot
   cd Hotwheels_bot
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup_pi.sh
   ./setup_pi.sh
   ```
   This will:
   - Install Python, pip, and system libraries
   - Create a virtual environment and install all dependencies
   - Install Playwright Chromium & Firefox binaries
   - Register and configure the `hotwheels.service` background service

3. **Configure your `.env`:**
   Ensure your `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, and coordinates in `.env` are filled.

4. **Start the Bot 24/7:**
   ```bash
   sudo systemctl enable --now hotwheels.service
   ```

5. **Monitor Live Logs:**
   ```bash
   sudo journalctl -u hotwheels.service -f
   ```

---

### Option B: Docker Compose Setup

If you prefer running via Docker on your Pi:

```bash
docker compose up -d --build
```

View live container logs:
```bash
docker compose logs -f
```

---

## 🛠️ Configuration & Sessions

### Environment Variables (`.env`)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token from `@BotFather` | *(Required)* |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID from `@userinfobot` | *(Required)* |
| `SCAN_INTERVAL` | Seconds between scan cycles in daemon mode | `300` (5 mins) |
| `PINCODE` | Target delivery pincode | `500073` |
| `BLINKIT_LAT` / `BLINKIT_LON` | Dark store GPS coordinates | Hyderabad |
| `ZEPTO_LAT` / `ZEPTO_LON` | Dark store GPS coordinates | Hyderabad |

### Session Setup (Pincode & Dark Store Lock)

To calibrate your exact local store sessions:
```bash
source venv/bin/activate
python setup_session.py
```
Select the platform, set your delivery location in the opened browser window, and press `ENTER` in the terminal to save the session state.

---

## 💻 Manual Commands

- **Run single test scan:**
  ```bash
  source venv/bin/activate
  python main.py --once
  ```

- **Run matcher unit tests:**
  ```bash
  source venv/bin/activate
  python test_bot.py
  ```

- **Manage Background Service:**
  ```bash
  sudo systemctl restart hotwheels.service   # Restart bot
  sudo systemctl stop hotwheels.service      # Stop bot
  sudo systemctl status hotwheels.service    # Check status
  ```

