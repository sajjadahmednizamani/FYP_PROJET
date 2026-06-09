INTENTS = {
    "study_eligibility": [
        "study permit eligibility",
        "eligibility for study permit",
        "study visa eligibility",
        "eligibility for canada study",
        "canada study permit eligibility",
        "student visa eligibility"
    ],

    "study_processing": [
        "processing time",
        "how long study visa",
        "study visa processing"
    ],

    "work_rights": [
        "work hours",
        "part time work",
        "student work",
        "work during study"
    ],

    "visit_visa": [
        "visit visa",
        "tourist visa",
        "visitor visa"
    ]
}

def detect_intent(question: str):
    q = question.lower()

    for intent, patterns in INTENTS.items():
        for p in patterns:
            if p in q:
                return intent

    # fallback logic (IMPORTANT)
    if "study" in q and "eligibility" in q:
        return "study_eligibility"

    if "visit" in q or "tourist" in q:
        return "visit_visa"

    return "unknown"
