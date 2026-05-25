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
    store = PLATFORM_EMOJI.get(platform, platform.title())
    priority_tag = "⚡ HIGH PRIORITY\n" if _is_priority(title) else ""
    cat_line = f"📦 Category: {category}\n" if category else ""

    body = (
        f"{priority_tag}"
        f"🚨 HOT WHEELS FOUND on {store}\n"
        f"\n"
        f"🏷  {title}\n"
        f"💰  {price}\n"
        f"{cat_line}"
        f"🔗  {link}\n"
    )

    client.messages.create(
        body=body,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=YOUR_WHATSAPP_NUMBER,
    )
