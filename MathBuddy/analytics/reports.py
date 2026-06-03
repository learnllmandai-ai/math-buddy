"""Simple reporting helpers."""


def generate_report(student_id: str, telemetry_df) -> dict:
    """Generate a compact report for a student using telemetry data."""
    return {
        "student_id": student_id,
        "questions_asked": len(telemetry_df),
        "grade_distribution": telemetry_df["grade"].value_counts().to_dict() if "grade" in telemetry_df.columns else {},
        "status": "ready",
    }
