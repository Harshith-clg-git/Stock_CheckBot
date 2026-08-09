import os
from dotenv import load_dotenv

# Load .env file if available locally
load_dotenv()

# ---------------------------------------------------------------------------
# Notification Settings
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
YOUR_WHATSAPP_NUMBER = os.getenv("YOUR_WHATSAPP_NUMBER", "")

# ---------------------------------------------------------------------------
# Location Coordinates (Hyderabad Default)
# ---------------------------------------------------------------------------
BLINKIT_LAT = float(os.getenv("BLINKIT_LAT", "17.4297"))
BLINKIT_LON = float(os.getenv("BLINKIT_LON", "78.4406"))

ZEPTO_LAT = float(os.getenv("ZEPTO_LAT", "17.4297"))
ZEPTO_LON = float(os.getenv("ZEPTO_LON", "78.4406"))

INSTAMART_LAT = float(os.getenv("INSTAMART_LAT", "17.4297"))
INSTAMART_LON = float(os.getenv("INSTAMART_LON", "78.4406"))

PINCODE = os.getenv("PINCODE", "500073")

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
    "nissan", "skyline", "gtr", "gt-r", "r32", "r33", "r34",
    "silvia", "240sx", "fairlady", "370z", "350z",
    "toyota", "supra", "ae86", "trueno", "celica", "mr2", "land cruiser",
    "mazda", "rx7", "rx-7", "rx3", "miata", "mx5", "mx-5",
    "mitsubishi", "evo", "evolution", "3000gt",
    "subaru", "impreza", "wrx", "sti",
    "acura", "lexus", "lfa"
]

EXOTIC_KEYWORDS = [
    "ferrari", "lamborghini", "lambo", "huracan", "aventador",
    "revuelto", "countach", "bugatti", "chiron", "veyron",
    "pagani", "zonda", "huayra", "koenigsegg", "jesko", "agera",
    "mclaren", "p1", "senna", "720s", "765lt",
    "porsche", "911", "gt3", "gt2", "carrera", "taycan",
    "aston martin", "db5", "valkyrie"
]

MUSCLE_KEYWORDS = [
    "ford", "mustang", "shelby", "cobra", "bronco", "f-150", "raptor",
    "chevrolet", "chevy", "camaro", "chevelle", "nova", "silverado",
    "dodge", "charger", "challenger", "hellcat", "demon", "viper",
    "corvette", "c8", "pontiac", "firebird", "trans am", "gto"
]

EURO_KEYWORDS = [
    "bmw", "m3", "m4", "e30", "e36", "e46",
    "audi", "rs6", "quattro", "r8",
    "mercedes", "amg", "190e", "benz",
    "volkswagen", "vw", "golf", "beetle",
    "jaguar", "land rover", "range rover", "volvo",
    "alfa romeo"
]

POPULAR_CASTINGS = [
    "godzilla", "pandem", "lbwk", "liberty walk",
    "silhouette", "tooned", "wagon", "pickup", "drift", "widebody",
    "hot wheels", "hotwheels"
]

KEYWORDS = {
    "TREASURE_HUNT": TREASURE_HUNT_KEYWORDS,
    "PREMIUM":       PREMIUM_KEYWORDS,
    "JDM":           JDM_KEYWORDS,
    "EXOTIC":        EXOTIC_KEYWORDS,
    "MUSCLE":        MUSCLE_KEYWORDS,
    "EURO":          EURO_KEYWORDS,
    "POPULAR":       POPULAR_CASTINGS,
}

# Items matching these keywords will be flagged with ⚡ HIGH PRIORITY
TOP_PRIORITY = [
    "skyline", "gtr", "gt-r", "supra", "civic", "nsx", "rx7", "rx-7",
    "porsche", "911", "gt3", "lambo", "lamborghini", "ferrari",
    "premium", "boulevard", "godzilla",
    "treasure hunt", "super treasure hunt", "sth"
]
