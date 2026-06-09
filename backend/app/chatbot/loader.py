import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "study_visa_info.json")

def load_rules():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data
