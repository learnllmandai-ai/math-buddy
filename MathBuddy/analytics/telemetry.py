import os
import csv
from datetime import datetime

def log_interaction(grade: str, question: str, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().isoformat() # ISO format is cleaner for string storage
    else:
        if hasattr(timestamp, "isoformat"):
            timestamp = timestamp.isoformat()

    file_path = "data/telemetry.csv"
    
    # 1. Ensure the 'data' directory actually exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 2. Check if we need to write headers (if file is brand new or empty)
    file_exists = os.path.exists(file_path) and os.path.getsize(file_path) > 0
    
    row = [timestamp, grade, question]

    # 3. Fast Append Mode ("a") - ignores past history, lightweight execution
    try:
        with open(file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "grade", "question"]) # Header
            writer.writerow(row)
    except Exception as e:
        # Prevent telemetry failure from crashing the student's entire live chat experience
        print(f"Telemetry logging failed safely: {e}")