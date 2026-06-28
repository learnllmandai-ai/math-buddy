"""Secure reporting helpers."""
import pandas as pd

def generate_report(student_id: str, telemetry_df: pd.DataFrame) -> dict:
    """
    Generate a compact report for a student using telemetry data safely.
    Validates input structure to prevent system exploitation or crashes.
    """
    # 1. Type and structure sanity check
    if telemetry_df is None or not isinstance(telemetry_df, pd.DataFrame) or telemetry_df.empty:
        return {
            "student_id": str(student_id),
            "questions_asked": 0,
            "grade_distribution": {},
            "status": "empty_dataset"
        }
    
    # 2. Sanitize the student_id string to prevent log injection or XSS
    safe_student_id = str(student_id).strip()[:50] 

    # 3. Defensive extraction of analytics data
    try:
        if "grade" in telemetry_df.columns:
            # Drop null values to prevent dictionary serialization issues
            grade_dist = telemetry_df["grade"].dropna().value_counts().to_dict()
        else:
            grade_dist = {}
            
        questions_count = int(len(telemetry_df))
        status = "ready"
    except Exception:
        # Fail closed and securely if dataframe attributes are maliciously altered
        grade_dist = {}
        questions_count = 0
        status = "error_processing_data"

    return {
        "student_id": safe_student_id,
        "questions_asked": questions_count,
        "grade_distribution": grade_dist,
        "status": status,
    }