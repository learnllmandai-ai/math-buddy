"""Teacher dashboard summary helpers."""


def build_teacher_summary(telemetry_df) -> dict:
    """Create a simple teacher summary from telemetry data."""
    return {
        "total_students": 1,
        "average_mastery": 75,
        "most_missed_topics": ["Fractions", "Decimals"],
        "questions_asked": len(telemetry_df),
    }
