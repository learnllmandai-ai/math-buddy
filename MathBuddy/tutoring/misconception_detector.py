"""Basic misconception detection helpers."""


def detect_misconception(response: str) -> dict:
    """Detect a likely misconception from the student's response text."""
    lowered = response.lower()

    patterns = {
        "Fractions": ["add denominators", "common denominator", "denominator"],
        "Algebra": ["sign mistake", "minus sign", "solve for x", "combine like terms"],
        "Geometry": ["area vs perimeter", "perimeter", "area"],
        "Decimals": ["place value", "decimal point", "tenths"],
    }

    for topic, keywords in patterns.items():
        if any(keyword in lowered for keyword in keywords):
            return {"topic": topic, "misconception": "Detected a likely misconception pattern."}

    return {"topic": "General", "misconception": "No clear misconception pattern detected."}
