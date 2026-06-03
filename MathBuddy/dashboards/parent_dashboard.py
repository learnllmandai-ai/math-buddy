"""Parent dashboard summary helpers."""


def build_parent_report(student_id: str, telemetry_df) -> dict:
    """Create a simple weekly report summary for a parent."""
    return {
        "student_id": student_id,
        "questions_asked": len(telemetry_df),
        "topics_studied": ["Fractions", "Algebra"],
        "recommended_practice": "Review one step at a time.",
    }
