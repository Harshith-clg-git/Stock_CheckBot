from config import KEYWORDS


def normalize(text):
    return text.lower().strip()


def match_keywords(title):
    normalized = normalize(title)

    for brand, words in KEYWORDS.items():
        for word in words:
            if word in normalized:
                return brand

    return None
