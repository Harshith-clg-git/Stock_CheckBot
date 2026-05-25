from matcher.keywords import match_keywords

tests = [
    "Hot Wheels Honda NSX Die Cast",
    "Hot Wheels Ferrari 458 Italia",
    "Hot Wheels Dodge Charger Hellcat",
    "Hot Wheels BMW M3 E30",
    "Hot Wheels Premium Boulevard",
    "Hot Wheels Super Treasure Hunt Supra",
    "Hot Wheels Pandem Widebody Drift",
    "Hot Wheels Fiat Beast of Turin",
]

for t in tests:
    result = match_keywords(t) or "NO MATCH"
    print(f"{result:<15} | {t}")
