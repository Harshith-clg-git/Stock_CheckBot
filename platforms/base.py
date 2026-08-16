from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from config import get_playwright_proxy

COMMON_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
COMMON_VIEWPORT = {"width": 1280, "height": 800}
COMMON_BROWSER_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-infobars",
    "--window-position=0,0",
    "--ignore-certificate-errors",
    "--ignore-certificate-errors-spki-list",
]

STEALTH_JS = """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
    };
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en', 'en-IN']
    });
"""

class BaseScraper(ABC):
    def __init__(self, platform_name: str):
        self.platform_name = platform_name

    def get_proxy_config(self) -> Optional[dict]:
        """Returns proxy config if set in environment."""
        return get_playwright_proxy()

    @abstractmethod
    async def fetch_products(self) -> List[Dict]:
        """
        Abstract method to fetch active Hot Wheels products from platform.
        Returns a list of standardized dicts:
        {
            "id": str,
            "title": str,
            "price": str,
            "link": str,
            "platform": str
        }
        """
        pass
