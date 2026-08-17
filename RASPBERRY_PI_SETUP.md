# 🍓 Raspberry Pi 5 Setup & Installation Guide

This guide provides step-by-step instructions for installing and running the **Hot Wheels Multi-Platform Stock Checker Bot** 24/7 on a **Raspberry Pi 5** (Raspberry Pi OS 64-bit / Debian Bookworm).

---

## 📋 Prerequisites

1. **Raspberry Pi 5** running **Raspberry Pi OS (64-bit)** (Debian Bookworm).
2. Internet connection on the Pi.
3. Your Telegram Bot details:
   - `TELEGRAM_BOT_TOKEN` (from `@BotFather`)
   - `TELEGRAM_CHAT_ID` (from `@userinfobot`)

---

## ⚡ Method 1: Automated 1-Command Setup (Recommended)

Run the following commands in the terminal on your Raspberry Pi:

```bash
# 1. Clone the repository
git clone https://github.com/Harshith-clg-git/Stock_CheckBot.git
cd Stock_CheckBot

# 2. Run the automated setup script
chmod +x setup_pi.sh
./setup_pi.sh
```

The script will automatically:
- Install required system packages (`python3-venv`, `python3-pip`, `libenchant`, `git`, `curl`).
- Create a Python virtual environment (`venv`).
- Install Python dependencies from `requirements.txt`.
- Install Playwright Chromium and Firefox binaries along with system dependencies for ARM64 Linux.
- Generate a `.env` template file.
- Register `hotwheels.service` as a systemd service under your current user account.

---

## 🛠️ Step 2: Configure Environment Variables

Edit the `.env` file on your Pi:

```bash
nano .env
```

Add your Telegram credentials and local settings:

```env
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
TELEGRAM_CHAT_ID=your_actual_chat_id_here

# Hyderabad coordinates & Pincode (Default)
BLINKIT_LAT=17.4297
BLINKIT_LON=78.4406
ZEPTO_LAT=17.4297
ZEPTO_LON=78.4406
PINCODE=500073

# Scan interval in seconds (default: 300 = 5 minutes)
SCAN_INTERVAL=300
```

Press `Ctrl + O`, then `Enter` to save, and `Ctrl + X` to exit `nano`.

---

## 🔑 Step 3: Set Up Delivery Store Sessions (Optional but Recommended)

Quick-commerce stores (Blinkit, Zepto, BigBasket) store your delivery location in browser cookies/session storage. To lock in your exact local dark store:

1. On your Pi (with GUI / desktop):
   ```bash
   source venv/bin/activate
   python setup_session.py
   ```
2. Select the platform (or option 5 for all platforms).
3. The Chromium browser window will open.
4. Click the location selector on the site, enter your exact Hyderabad pincode/address (e.g. `500073`), confirm products are displayed for your area, and return to the terminal and press `ENTER`.
5. The session will be saved in `sessions/<platform>.json`.

> *Note: If running headless Pi OS Lite, you can run `setup_session.py` on your PC and copy the generated `sessions/` folder to `/home/pi/Stock_CheckBot/sessions/` using SFTP / SCP.*

---

## 🚀 Step 4: Start the 24/7 Background Service

To start the bot and keep it running even after rebooting your Pi:

```bash
# Enable and start the background service immediately
sudo systemctl enable --now hotwheels.service
```

### Useful Service Commands:

- **Check status:**
  ```bash
  sudo systemctl status hotwheels.service
  ```
- **View live streaming logs:**
  ```bash
  sudo journalctl -u hotwheels.service -f
  ```
- **Restart the bot:**
  ```bash
  sudo systemctl restart hotwheels.service
  ```
- **Stop the bot:**
  ```bash
  sudo systemctl stop hotwheels.service
  ```

---

## 🐳 Method 2: Running via Docker Compose

If you prefer using Docker on your Raspberry Pi:

1. **Install Docker Engine:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```
   *(Log out and log back in to apply group changes)*

2. **Start container in background:**
   ```bash
   docker compose up -d --build
   ```

3. **View logs:**
   ```bash
   docker compose logs -f
   ```

---

## 🧪 Manual Single Test Scan

To test a single scan manually without starting the continuous background service:

```bash
source venv/bin/activate
python main.py --once
```
