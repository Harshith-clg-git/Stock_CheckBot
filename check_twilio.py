import os
import sys

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, YOUR_WHATSAPP_NUMBER

try:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    messages = client.messages.list(to=YOUR_WHATSAPP_NUMBER, limit=3)
    
    for record in messages:
        print(f"Message SID: {record.sid}")
        print(f"Status: {record.status}")
        print(f"Error Message: {record.error_message}")
        print(f"Error Code: {record.error_code}")
        print("-" * 20)
        
except Exception as e:
    print(f"Failed to fetch Twilio status: {e}")
