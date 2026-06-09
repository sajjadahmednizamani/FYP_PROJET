import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "study_visa_info.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)

LAST_COUNTRY = None

COUNTRY_MAP = {
    "usa": "USA",
    "canada": "Canada",
    "uk": "UK",
    "australia": "Australia"
}


def get_greeting():
    return DATA["meta"]["greeting"]


def chatbot_response(message: str):
    global LAST_COUNTRY
    msg = message.lower()

    # 🌍 Country detection
    for key in COUNTRY_MAP:
        if key in msg:
            LAST_COUNTRY = key
            return f"{COUNTRY_MAP[key]} selected. What do you want to know? (eligibility / documents / process / fees)"

    if not LAST_COUNTRY:
        return "Please specify the country (Canada / USA / UK / Australia)."

    country_key = COUNTRY_MAP[LAST_COUNTRY]
    country_data = DATA[country_key]

    if "eligib" in msg:
        return country_data["eligibility"]["overview"]

    if "document" in msg:
        return ", ".join(country_data["documents"]["list"])

    if "process" in msg or "apply" in msg:
        return " → ".join(country_data["process"]["steps"])

    if "fee" in msg or "cost" in msg:
        return country_data["fees"]

    return "Sorry, I can't answer that yet."
