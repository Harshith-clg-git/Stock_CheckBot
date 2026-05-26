import os

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "ACa80362127ad03a8274d90bf60a8eb37c")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "4b0ef195a1f88c82c5fb1ac4242f3db1")

TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
YOUR_WHATSAPP_NUMBER = os.getenv("YOUR_WHATSAPP_NUMBER", "whatsapp:+918977633448")

# ---------------------------------------------------------------------------
# Location (Hyderabad) — used by quick-delivery platforms
# ---------------------------------------------------------------------------
BLINKIT_LAT = 17.4297
BLINKIT_LON = 78.4406

ZEPTO_LAT = 17.4297
ZEPTO_LON = 78.4406

SWIGGY_LAT = 17.4297
SWIGGY_LON = 78.4406

PINCODE = "500073"   # Hyderabad pincode — used by BigBasket / FirstCry

# ---------------------------------------------------------------------------
# Scan intervals (seconds)
# ---------------------------------------------------------------------------
SCAN_INTERVAL = 120          # Blinkit
ZEPTO_SCAN_INTERVAL = 180
SWIGGY_SCAN_INTERVAL = 180
FIRSTCRY_SCAN_INTERVAL = 300
BIGBASKET_SCAN_INTERVAL = 300

# ---------------------------------------------------------------------------
# Keywords — sourced from hotwheels_keywords.md
# ---------------------------------------------------------------------------

JDM_KEYWORDS = [
    # Honda
    "honda", "civic", "nsx", "s2000", "integra", "type r", "prelude",
    # Nissan
    "nissan", "skyline", "gtr", "gt-r", "r32", "r33", "r34",
    "silvia", "240sx", "fairlady", "370z", "350z",
    # Toyota
    "toyota", "supra", "ae86", "trueno", "celica", "mr2",
    "land cruiser", "fj40",
    # Mazda
    "mazda", "rx7", "rx-7", "rx3", "miata", "mx5", "mx-5", "cosmo",
    # Mitsubishi
    "mitsubishi", "evo", "evolution", "3000gt",
    # Subaru
    "subaru", "impreza", "wrx", "sti",
    # Acura / Lexus
    "acura", "lexus", "lfa",
]

EXOTIC_KEYWORDS = [
    "ferrari", "lamborghini", "lambo", "huracan", "aventador",
    "revuelto", "countach",
    "bugatti", "chiron", "veyron",
    "pagani", "zonda", "huayra",
    "koenigsegg", "jesko", "agera",
    "mclaren", "p1", "senna", "720s", "765lt",
    "porsche", "911", "gt3", "gt2", "carrera", "taycan",
    "aston martin", "db5", "valkyrie",
    "maserati",
]

MUSCLE_KEYWORDS = [
    "ford", "mustang", "shelby", "cobra", "bronco", "f-150", "raptor",
    "chevrolet", "chevy", "camaro", "chevelle", "nova", "silverado",
    "dodge", "charger", "challenger", "hellcat", "demon", "viper",
    "corvette", "c8",
    "pontiac", "firebird", "trans am", "gto",
    "jeep", "cadillac", "buick", "plymouth", "oldsmobile"
]

EURO_KEYWORDS = [
    "bmw", "m3", "m4", "e30", "e36", "e46",
    "audi", "rs6", "quattro", "r8",
    "mercedes", "amg", "190e", "benz",
    "volkswagen", "vw", "golf", "beetle",
    "jaguar", "land rover", "range rover", "volvo",
    "fiat", "renault", "peugeot", "alfa romeo", "mini"
]

PREMIUM_KEYWORDS = [
    "premium", "boulevard", "car culture", "team transport",
    "real riders", "metal/metal", "fast & furious", "fast furious",
    "fnf", "retro racers", "race day",
]

TREASURE_HUNT_KEYWORDS = [
    "treasure hunt", "super treasure hunt", "sth",
]

POPULAR_CASTINGS = [
    "godzilla", "pandem", "lbwk", "liberty walk",
    "silhouette", "tooned", "wagon", "pickup", "drift", "widebody",
]

KEYWORDS = {
    "TREASURE_HUNT": TREASURE_HUNT_KEYWORDS,  # rarest — check first
    "PREMIUM":       PREMIUM_KEYWORDS,
    "JDM":           JDM_KEYWORDS,
    "EXOTIC":        EXOTIC_KEYWORDS,
    "MUSCLE":        MUSCLE_KEYWORDS,
    "EURO":          EURO_KEYWORDS,
    "POPULAR":       POPULAR_CASTINGS,
}

# Items in this list get a ⚡ HIGH PRIORITY tag in the WhatsApp alert
TOP_PRIORITY = [
    "skyline", "gtr", "supra", "civic", "nsx", "rx7",
    "porsche", "911", "lambo", "ferrari",
    "premium", "boulevard", "godzilla",
    "treasure hunt", "super treasure hunt",
]
