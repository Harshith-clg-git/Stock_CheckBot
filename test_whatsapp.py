import os
import sys

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from notifier.whatsapp import send_alert

try:
    print("Testing WhatsApp alert...")
    send_alert(
        title="Test Hot Wheels 59 Chevy Impala",
        price="₹179",
        link="https://www.bigbasket.com/test",
        platform="bigbasket",
        category="MUSCLE"
    )
    print("WhatsApp alert sent successfully!")
except Exception as e:
    print(f"Failed to send WhatsApp alert: {e}")
