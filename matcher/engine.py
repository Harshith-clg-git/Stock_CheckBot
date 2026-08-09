import re
from typing import Optional
from config import KEYWORDS, TOP_PRIORITY

# Terms that immediately disqualify a listing (tracks, playsets, monster trucks, fantasy/non-car items)
EXCLUDED_PATTERNS = [
    # Tracks, Playsets & Accessories
    r"\btracks?\b",
    r"\bplaysets?\b",
    r"\bloops?\b",
    r"\bstunts?\b",
    r"\blaunch(?:er|ing)?\b",
    r"\bcyclone\b",
    r"\brace[\s\-]off\b",
    r"\bstarter pack\b",
    r"\btransporters?\b",
    r"\bdisplay sets?\b",
    r"\bgarages?\b",
    r"\bcar wash\b",
    r"\bbuilders?\b",
    r"\bcarriers?\b",
    r"\bhaulers?\b",
    r"\bboosters?\b",
    
    # Monster Trucks
    r"\bmonster trucks?\b",
    r"\btri to crush me\b",
    r"\bcrush delivery\b",
    r"\bdemolition\b",
    r"\bbigfoot\b",

    # Fantasy / Non-Car / Non-Diecast Vehicle Models
    r"\bshark hammer\b",
    r"\bshark\b",
    r"\bdragons?\b",
    r"\bdino(?:saur)?\b",
    r"\bcreatures?\b",
    r"\bx[\s\-]blade\b",
    r"\bbikes?\b",
    r"\bmotorcycles?\b",
    r"\bkarts?\b",
    r"\bstandard kart\b",
    r"\bmario kart\b",
    r"\bcolor reveal\b",
    r"\bcolor shifters?\b",
    r"\btwin tags\b",
    r"\btricycles?\b",
    r"\bquads?\b",
    r"\bairplanes?\b",
    r"\bplanes?\b",
    r"\bhelicopters?\b",
    r"\bboats?\b",
    r"\bhovercraft\b",

    # Multipacks / Sets
    r"\bpack of \d+\b",
    r"\bmultipack\b",
    r"\bcars? sets?\b",

    # Apparel & School supplies
    r"\bbackpacks?\b",
    r"\bbags?\b",
    r"\bpencils?\b",
    r"\bt[\s\-]shirts?\b",
    r"\bshirts?\b",
    r"\bapparels?\b",
    r"\bbottles?\b",
    r"\bsocks?\b",
    r"\bnotebooks?\b",
]

# Non-Hot-Wheels brands to exclude unless explicitly labeled as Hot Wheels
GENERIC_BRANDS = [
    "centy", "frendo", "chigy wooh", "toyshine", "kinsmart",
    "speedage", "solimo", "welly", "bburago", "maisto", "jada"
]


def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'[\s_\-]+', ' ', text)
    return text


def is_excluded(normalized_title: str) -> bool:
    """Returns True if the title contains any unwanted item patterns."""
    for pattern in EXCLUDED_PATTERNS:
        if re.search(pattern, normalized_title):
            return True

    for gb in GENERIC_BRANDS:
        if gb in normalized_title and not ("hot wheels" in normalized_title or "hotwheels" in normalized_title):
            return True

    return False


def match_category(title: str) -> Optional[str]:
    """
    Evaluates a product title against categorized keyword lists.
    Filters out tracks, monster trucks, fantasy castings, and non-car items.
    Returns matching category name ('TREASURE_HUNT', 'JDM', 'EXOTIC', 'MUSCLE', 'EURO', 'PREMIUM', 'MAINLINE') or None.
    """
    if not title:
        return None

    normalized_title = normalize(title)

    # 1. Filter out excluded categories (tracks, monster trucks, fantasy, apparel)
    if is_excluded(normalized_title):
        return None

    # 2. Must be a genuine Hot Wheels product
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

    # 3. Match specific categories in order of priority
    for category_name, keyword_list in KEYWORDS.items():
        for kw in keyword_list:
            kw_norm = normalize(kw)
            # Use word boundary matching for short keywords (e.g. STH, TH, EVO, M3, GT3, C8, 620)
            if len(kw_norm) <= 4:
                pattern = rf"\b{re.escape(kw_norm)}\b"
                if re.search(pattern, normalized_title):
                    return category_name
            else:
                if kw_norm in normalized_title:
                    return category_name

    # 4. If genuine Hot Wheels diecast car but no brand matched, label as MAINLINE
    return "MAINLINE"


def is_priority(title: str) -> bool:
    """Returns True if item qualifies for ⚡ HIGH PRIORITY tag."""
    normalized_title = normalize(title)
    return any(normalize(kw) in normalized_title for kw in TOP_PRIORITY)
