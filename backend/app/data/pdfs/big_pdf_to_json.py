import os
import json
from pypdf import PdfReader

PDF_FOLDER = "data/pdfs"
OUTPUT = "data/study_visa_info.json"

dataset = {
    "meta": {
        "greeting": "Welcome to GoGlobalAI Visa Assistant!"
    },
    "countries": []
}


def chunk_text(text, size=500):
    chunks = []
    for i in range(0, len(text), size):
        chunks.append(text[i:i+size])
    return chunks


for file in os.listdir(PDF_FOLDER):

    if not file.endswith(".pdf"):
        continue

    path = os.path.join(PDF_FOLDER, file)
    reader = PdfReader(path)

    full_text = ""

    for page in reader.pages:
        t = page.extract_text()
        if t:
            full_text += t + "\n"

    country_name = file.replace("_study_visa.pdf","").replace("_student_visa.pdf","")

    country_obj = {
        "id": country_name.lower(),
        "name": country_name.capitalize(),
        "chunks": chunk_text(full_text, 600)   # big detailed chunks
    }

    dataset["countries"].append(country_obj)


with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)


print("✅ BIG detailed study_visa_info.json created successfully!")
