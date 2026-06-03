"""Simple translation helpers for English/Tamil support."""


def translate_text(text: str, target_language: str) -> str:
    """Return a simple translated version of common tutoring terms."""
    translations = {
        "en": text,
        "ta": "கற்றலுக்கான உதவிக்குறிப்பு: " + text,
    }
    return translations.get(target_language, text)
