import os
from dotenv import load_dotenv

# Load .env file if available locally
load_dotenv()

# ---------------------------------------------------------------------------
# Notification Settings
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# ---------------------------------------------------------------------------
# Proxy Settings (Optional - for Cloud / GitHub Actions Indian IP routing)
# ---------------------------------------------------------------------------
PROXY_SERVER = os.getenv("PROXY_SERVER", "").strip()  # e.g. "http://ip:port" or "socks5://ip:port"
PROXY_USERNAME = os.getenv("PROXY_USERNAME", "").strip()
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD", "").strip()

def get_playwright_proxy():
    """Returns proxy dictionary for Playwright if PROXY_SERVER is configured."""
    if not PROXY_SERVER:
        return None
    proxy_config = {"server": PROXY_SERVER}
    if PROXY_USERNAME:
        proxy_config["username"] = PROXY_USERNAME
    if PROXY_PASSWORD:
        proxy_config["password"] = PROXY_PASSWORD
    return proxy_config

# ---------------------------------------------------------------------------
# Location Coordinates — Hyderabad (hardcoded, change here if needed)
# ---------------------------------------------------------------------------
BLINKIT_LAT  = 17.4297
BLINKIT_LON  = 78.4406

ZEPTO_LAT    = 17.4297
ZEPTO_LON    = 78.4406

PINCODE = "500073"

# ---------------------------------------------------------------------------
# Hot Wheels Keyword Priority Tiers
# ---------------------------------------------------------------------------
TREASURE_HUNT_KEYWORDS = [
    "treasure hunt", "super treasure hunt", "sth", "th"
]

PREMIUM_KEYWORDS = [
    "premium", "boulevard", "car culture", "team transport",
    "real riders", "metal/metal", "fast & furious", "fast furious",
    "fnf", "retro racers", "race day"
]

JDM_KEYWORDS = [
    "honda", "civic", "nsx", "s2000", "integra", "type r", "prelude",
    "nissan", "skyline", "gtr", "gt-r", "r32", "r33", "r34", "r35",
    "silvia", "240sx", "180sx", "fairlady", "370z", "350z", "300zx",
    "toyota", "supra", "ae86", "trueno", "celica", "mr2", "land cruiser",
    "datsun", "240z", "620", "510",
    "mazda", "rx7", "rx-7", "rx3", "miata", "mx5", "mx-5", "cosmo",
    "mitsubishi", "evo", "evolution", "3000gt",
    "subaru", "impreza", "wrx", "sti", "brz",
    "acura", "lexus", "lfa"
]

EXOTIC_KEYWORDS = [
    "ferrari", "lamborghini", "lambo", "huracan", "aventador",
    "revuelto", "countach", "miura", "diablo",
    "bugatti", "chiron", "veyron", "bolide", "divo",
    "pagani", "zonda", "huayra", "utopia",
    "koenigsegg", "jesko", "agera", "gemera", "cc850",
    "mclaren", "p1", "senna", "720s", "765lt", "f1", "speedtail",
    "porsche", "911", "gt3", "gt2", "carrera", "taycan", "cayman", "boxster", "918", "959",
    "aston martin", "db5", "valkyrie", "vantage", "vulcan",
    "maserati"
]

MUSCLE_KEYWORDS = [
    "ford", "mustang", "shelby", "gt500", "gt350", "cobra", "gt40", "bronco", "f-150", "raptor",
    "chevrolet", "chevy", "camaro", "chevelle", "nova", "silverado", "corvette", "c8", "c7", "c6",
    "dodge", "charger", "challenger", "hellcat", "demon", "viper", "hemi",
    "pontiac", "firebird", "trans am", "gto",
    "plymouth", "cuda", "barracuda", "superbird"
]

EURO_KEYWORDS = [
    "bmw", "m3", "m4", "e30", "e36", "e46",
    "audi", "rs6", "quattro", "r8",
    "mercedes", "amg", "190e", "benz",
    "volkswagen", "vw", "golf", "beetle",
    "jaguar", "land rover", "range rover", "volvo",
    "alfa romeo"
]

# Note: POPULAR_CASTINGS is intentionally NOT in KEYWORDS anymore.
# Having 'hot wheels' as a catch-all keyword caused every fantasy casting
# (Bone Shaker, Twin Mill, etc.) to match POPULAR before the real-brand
# gate in engine.py could filter them out.
# Tooned / pandem / lbwk series still alert because they appear on real-car
# castings that DO pass the has_real_car_brand() check.
POPULAR_CASTINGS = [
    "godzilla", "pandem", "lbwk", "liberty walk",
    "silhouette", "tooned", "wagon", "pickup", "drift", "widebody",
]

KEYWORDS = {
    "TREASURE_HUNT": TREASURE_HUNT_KEYWORDS,
    "PREMIUM":       PREMIUM_KEYWORDS,
    "JDM":           JDM_KEYWORDS,
    "EXOTIC":        EXOTIC_KEYWORDS,
    "MUSCLE":        MUSCLE_KEYWORDS,
    "EURO":          EURO_KEYWORDS,
}

# Items matching these keywords will be flagged as HIGH PRIORITY
TOP_PRIORITY = [
    "skyline", "gtr", "gt-r", "supra", "civic", "nsx", "rx7", "rx-7",
    "porsche", "911", "gt3", "lambo", "lamborghini", "ferrari",
    "premium", "boulevard", "godzilla",
    "treasure hunt", "super treasure hunt", "sth"
]
