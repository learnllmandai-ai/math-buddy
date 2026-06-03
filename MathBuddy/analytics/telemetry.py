import pandas as pd
from datetime import datetime


def log_interaction(grade, question, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now()

    row = {
        "timestamp": timestamp,
        "grade": grade,
        "question": question,
    }

    try:
        df = pd.read_csv("data/telemetry.csv")
    except Exception:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    df.to_csv("data/telemetry.csv", index=False)
