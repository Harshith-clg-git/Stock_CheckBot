from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    def __init__(self, platform_name: str):
        self.platform_name = platform_name

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
