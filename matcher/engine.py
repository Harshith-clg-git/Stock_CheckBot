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

# ---------------------------------------------------------------------------
# Real-world car brand / model names that qualify a car for MAINLINE alerts.
# If a Hot Wheels title doesn't match any keyword category AND doesn't contain
# at least one of these, it's treated as a fantasy casting and skipped.
# ---------------------------------------------------------------------------
REAL_CAR_BRANDS = [
    # --- Japanese ---
    "honda", "civic", "nsx", "s2000", "integra", "prelude", "accord", "fit", "jazz",
    "nissan", "skyline", "gtr", "gt-r", "r32", "r33", "r34", "r35",
    "silvia", "240sx", "180sx", "fairlady", "370z", "350z", "300zx", "z car",
    "toyota", "supra", "ae86", "trueno", "levin", "celica", "mr2", "land cruiser",
    "corolla", "hilux", "tundra", "4runner", "rav4",
    "datsun", "240z", "260z", "280z", "620", "510", "521",
    "mazda", "rx7", "rx-7", "rx3", "rx-3", "miata", "mx5", "mx-5", "cosmo",
    "mitsubishi", "evo", "evolution", "eclipse", "3000gt", "lancer", "galant",
    "subaru", "impreza", "wrx", "sti", "brz", "outback", "forester",
    "acura", "lexus", "lfa", "is300", "is200",
    "isuzu", "suzuki", "swift", "samurai",
    "infiniti", "q60",

    # --- American ---
    "ford", "mustang", "shelby", "gt500", "gt350", "cobra", "gt40", "bronco",
    "f-150", "f150", "raptor", "focus", "escort", "torino", "falcon",
    "chevrolet", "chevy", "camaro", "chevelle", "nova", "silverado", "corvette",
    "c8", "c7", "c6", "c5", "c4", "c3", "c2", "c1", "impala", "el camino", "blazer",
    "dodge", "charger", "challenger", "hellcat", "demon", "viper", "hemi",
    "dart", "coronet", "polara", "neon", "omni",
    "pontiac", "firebird", "trans am", "gto", "grand am", "bonneville",
    "plymouth", "cuda", "barracuda", "superbird", "road runner", "satellite",
    "buick", "riviera", "skylark", "grand national", "regal", "gsx",
    "oldsmobile", "442", "cutlass",
    "cadillac", "eldorado", "coupe deville",
    "amc", "javelin", "gremlin", "pacer",
    "jeep", "wrangler", "gladiator",
    "ram", "1500",
    "lincoln", "continental",
    "mercury", "cougar", "cyclone",
    "studebaker",

    # --- German ---
    "bmw", "m3", "m4", "m5", "m8", "e30", "e36", "e46", "e92", "e39", "e60",
    "audi", "rs6", "rs4", "rs3", "quattro", "r8", "tt", "a4",
    "mercedes", "amg", "190e", "benz", "sls", "gtr", "sl",
    "volkswagen", "vw", "golf", "gti", "beetle", "bug", "type 1", "corrado",
    "porsche", "911", "gt3", "gt2", "carrera", "taycan", "cayman", "boxster",
    "918", "959", "356", "944", "968", "914",
    "opel",

    # --- Italian ---
    "ferrari", "f40", "f50", "enzo", "laferrari", "488", "458", "360", "f355",
    "testarossa", "308", "328",
    "lamborghini", "lambo", "huracan", "aventador", "revuelto", "countach",
    "miura", "diablo", "gallardo", "urus",
    "bugatti", "chiron", "veyron", "bolide", "divo", "eb110",
    "alfa romeo", "maserati", "lancia", "fiat", "abarth", "de tomaso", "pantera",

    # --- British ---
    "jaguar", "land rover", "range rover", "defender",
    "aston martin", "db5", "db11", "valkyrie", "vantage", "vulcan", "dbs",
    "lotus", "elise", "exige", "evora", "esprit",
    "bentley", "rolls royce", "mclaren", "p1", "senna", "720s", "765lt", "speedtail",
    "mini", "triumph", "tvr", "jensen",

    # --- French ---
    "renault", "alpine", "peugeot", "citroen", "ds",

    # --- Swedish / Others ---
    "volvo", "saab", "koenigsegg", "jesko", "agera", "gemera", "cc850",
    "pagani", "zonda", "huayra", "utopia",

    # --- Korean ---
    "hyundai", "genesis", "kia",

    # --- Real models / body styles sometimes used alone ---
    "roadster", "speedster", "roadrunner",

    # --- Trucks & SUVs based on real platforms ---
    "pickup", "f-100", "c10", "gmc", "sierra", "suburban", "tahoe", "yukon",
    "hummer", "humvee",
]

# Compile to set for fast O(1) lookup during matching
_REAL_BRAND_SET = set(REAL_CAR_BRANDS)


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


def has_real_car_brand(normalized_title: str) -> bool:
    """
    Returns True if the title contains at least one recognisable real-world
    car brand or model name.  This gates the MAINLINE fallback so that
    fantasy castings (Bone Shaker, Twin Mill, Roller Toaster, etc.) are
    silently skipped rather than labelled MAINLINE.
    """
    for brand in _REAL_BRAND_SET:
        brand_norm = normalize(brand)
        # Use word-boundary matching for short tokens to avoid false positives
        if len(brand_norm) <= 4:
            if re.search(rf"\b{re.escape(brand_norm)}\b", normalized_title):
                return True
        else:
            if brand_norm in normalized_title:
                return True
    return False


def match_category(title: str) -> Optional[str]:
    """
    Evaluates a product title against categorized keyword lists.
    Filters out tracks, monster trucks, fantasy castings, and non-car items.

    Returns a category name or None (skip entirely):
      TREASURE_HUNT → super/treasure hunt variants
      PREMIUM       → car culture, boulevard, real riders, etc.
      JDM           → Japanese brands/models
      EXOTIC        → supercars (Ferrari, Lambo, Bugatti …)
      MUSCLE        → American muscle (Ford, Dodge, Chevy …)
      EURO          → European everyday brands (BMW, VW, Audi …)
      POPULAR       → Popular castings that match known real-car derivatives
      MAINLINE      → Any other real-brand car that passed the above filters
      None          → Fantasy casting or excluded item — do NOT alert
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

    # 4. MAINLINE only if a real-world car brand/model is present in the title.
    #    Fantasy castings (Bone Shaker, Twin Mill, Duck N Roll, Roller Toaster,
    #    Mountain Mauler, Head Gasket, Gone Mad, etc.) return None → skipped.
    if has_real_car_brand(normalized_title):
        return "MAINLINE"

    return None


def is_priority(title: str) -> bool:
    """Returns True if item qualifies for ⚡ HIGH PRIORITY tag."""
    normalized_title = normalize(title)
    return any(normalize(kw) in normalized_title for kw in TOP_PRIORITY)
