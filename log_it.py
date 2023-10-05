from datetime import datetime

def log(level, message):
    print(f"[{datetime.now()}] - [{level}] - [{message}]")