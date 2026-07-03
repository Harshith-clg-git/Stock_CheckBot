from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER,
    YOUR_WHATSAPP_NUMBER,
    TOP_PRIORITY,
)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

PLATFORM_EMOJI = {
    "blinkit":          "🟡 Blinkit",
    "swiggy_instamart": "🟠 Swiggy Instamart",
    "zepto":            "🟣 Zepto",
    "firstcry":         "🔵 FirstCry",
    "bigbasket":        "🟢 BigBasket",
}


def _is_priority(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in TOP_PRIORITY)


def send_alert(title: str, price: str, link: str,
               platform: str = "blinkit", category: str = ""):
    # Send only name and link to save bandwidth/costs as requested
    body_text = f"{title}\n{link}"
    
    client.messages.create(
        body=body_text,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=YOUR_WHATSAPP_NUMBER,
    )
