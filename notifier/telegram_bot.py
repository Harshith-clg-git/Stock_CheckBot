import httpx
from loguru import logger
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from matcher.engine import is_priority

PLATFORM_BADGES = {
    "blinkit":          "🟡 Blinkit",
    "zepto":            "🟣 Zepto",
    "firstcry":         "🔵 FirstCry",
    "bigbasket":        "🟢 BigBasket",
}

CATEGORY_EMOJIS = {
    "TREASURE_HUNT": "💎 TREASURE HUNT",
    "PREMIUM":       "⭐ PREMIUM",
    "JDM":           "🏎️ JDM SPEC",
    "EXOTIC":        "🔥 EXOTIC",
    "MUSCLE":        "💪 MUSCLE",
    "EURO":          "🇪🇺 EURO",
    "POPULAR":       "🚗 MAINLINE",
    "MAINLINE":      "🚗 MAINLINE",
}

async def send_telegram_alert(
    title: str,
    price: str,
    link: str,
    platform: str = "blinkit",
    category: str = "MAINLINE",
    alert_type: str = "NEW"
) -> bool:
    """
    Sends a formatted stock alert card to Telegram via Bot API.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram Bot Token or Chat ID not configured. Skipping Telegram alert.")
        return False

    platform_badge = PLATFORM_BADGES.get(platform.lower(), f"🌐 {platform.capitalize()}")
    cat_badge = CATEGORY_EMOJIS.get(category, "🚗 MAINLINE")
    
    header = "🚨 **RESTOCK ALERT**" if alert_type == "RESTOCK" else "⚡ **NEW HOT WHEELS IN STOCK**"
    priority_flag = "\n🔥 **HIGH PRIORITY ITEM** 🔥" if is_priority(title) else ""

    message_text = (
        f"{header}\n\n"
        f"**{title}**\n"
        f"🏷️ **Price:** {price}\n"
        f"📍 **Platform:** {platform_badge}\n"
        f"🏎️ **Category:** {cat_badge}"
        f"{priority_flag}\n\n"
        f"🔗 [Click Here to Buy Now]({link})"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
        "reply_markup": {
            "inline_keyboard": [
                [{"text": f"🛒 Buy on {platform.capitalize()}", "url": link}]
            ]
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                logger.success(f"[Telegram] Sent alert for: {title}")
                return True
            else:
                logger.error(f"[Telegram] Failed ({resp.status_code}): {resp.text}")
                return False
    except Exception as e:
        logger.error(f"[Telegram] Error sending alert: {e}")
        return False
