#!/usr/bin/env bash
# ==============================================================================
# Raspberry Pi 5 Automated Setup Script for Hot Wheels Stock Checker Bot
# ==============================================================================
set -e

echo "🚗 Starting Raspberry Pi 5 setup for Hot Wheels Stock Checker Bot..."

# 1. Update and install system dependencies
echo "📦 Installing system packages & dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git curl

# 2. Setup Python virtual environment
echo "🐍 Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo "📦 Installing Python requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Install Playwright browser and OS dependencies
echo "🌐 Installing Playwright Chromium & Firefox + ARM64 system libraries..."
python -m playwright install --with-deps chromium firefox

# 4. Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found! Creating template..."
    cat <<EOF > .env
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
BLINKIT_LAT=17.4297
BLINKIT_LON=78.4406
ZEPTO_LAT=17.4297
ZEPTO_LON=78.4406
PINCODE=500073
SCAN_INTERVAL=300
EOF
    echo "👉 Please edit .env with your TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID."
fi

# 5. Configure systemd service
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)

echo "⚙️  Configuring systemd service for user '$CURRENT_USER' at '$CURRENT_DIR'..."

SERVICE_FILE="/etc/systemd/system/hotwheels.service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Hot Wheels Multi-Platform Stock Checker Bot
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
EnvironmentFile=$CURRENT_DIR/.env
ExecStart=$CURRENT_DIR/venv/bin/python main.py
Restart=always
RestartSec=15
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

echo ""
echo "======================================================================"
echo "✅ Setup Complete!"
echo "======================================================================"
echo "To start the bot 24/7 now:"
echo "  sudo systemctl enable --now hotwheels.service"
echo ""
echo "To check live logs:"
echo "  sudo journalctl -u hotwheels.service -f"
echo ""
echo "To test run manually once:"
echo "  source venv/bin/activate && python main.py --once"
echo "======================================================================"
