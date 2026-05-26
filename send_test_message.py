import sys
sys.stdout.reconfigure(encoding="utf-8")

from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, YOUR_WHATSAPP_NUMBER

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

try:
    message = client.messages.create(
        body="🚗 Hot Wheels Bot Test Message\nIf you see this, Twilio is working correctly!",
        from_=TWILIO_WHATSAPP_NUMBER,
        to=YOUR_WHATSAPP_NUMBER,
    )
    print(f"Message sent! SID: {message.sid}")
    print(f"Status: {message.status}")
except Exception as e:
    print(f"Failed to send: {e}")
