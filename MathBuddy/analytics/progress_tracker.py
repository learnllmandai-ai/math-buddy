import pandas as pd


def summarize_progress():
    try:
        df = pd.read_csv("data/telemetry.csv")

        return {
            "questions_asked": len(df),
            "grade_distribution": df["grade"].value_counts().to_dict(),
        }

    except Exception:
        return {}
