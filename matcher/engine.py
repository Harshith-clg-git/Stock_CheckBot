import re
from typing import Optional
from config import KEYWORDS, TOP_PRIORITY

def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    # Normalize punctuation and extra spaces
    text = re.sub(r'[\s_\-]+', ' ', text)
    return text


def match_category(title: str) -> Optional[str]:
    """
    Evaluates a product title against categorized keyword lists.
    Returns matching category name ('TREASURE_HUNT', 'JDM', 'PREMIUM', etc.) or None.
    """
    if not title:
        return None

    normalized_title = normalize(title)

    # Exclude non-diecast apparel/school supplies
    excluded_terms = ["backpack", "bag", "pencil", "t-shirt", "shirt", "apparel", "water bottle", "socks", "notebook"]
    if any(term in normalized_title for term in excluded_terms):
        return None

    # Exclude generic non-Hot Wheels toy brands unless title explicitly mentions Hot Wheels
    generic_brands = ["centy", "frendo", "chigy wooh", "kinsmart", "speedage", "solimo"]
    if any(gb in normalized_title for gb in generic_brands) and not ("hot wheels" in normalized_title or "hotwheels" in normalized_title):
        return None

    # Ensure title contains Hot Wheels marker or specific diecast brand
    is_hw = (
        "hot wheels" in normalized_title or 
        "hotwheels" in normalized_title or 
        "mattel" in normalized_title or
        "treasure hunt" in normalized_title or
        "boulevard" in normalized_title or
        "car culture" in normalized_title
    )

    if not is_hw:
        return None

    # Check categories in order of rarity priority
    for category_name, keyword_list in KEYWORDS.items():
        for kw in keyword_list:
            kw_norm = normalize(kw)
            # Use word boundary matching for short 2-3 char keywords like STH, TH, EVO, M3, GT3
            if len(kw_norm) <= 3:
                pattern = rf"\b{re.escape(kw_norm)}\b"
                if re.search(pattern, normalized_title):
                    return category_name
            else:
                if kw_norm in normalized_title:
                    return category_name

    # If explicitly Hot Wheels but no specific sub-brand matched, label as MAINLINE
    return "MAINLINE"


def is_priority(title: str) -> bool:
    """Returns True if item qualifies for ⚡ HIGH PRIORITY tag."""
    normalized_title = normalize(title)
    return any(normalize(kw) in normalized_title for kw in TOP_PRIORITY)
