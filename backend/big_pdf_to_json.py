import os
import json
from PyPDF2 import PdfReader

# -------------------------
# Clean text function
# -------------------------
def clean_text(text: str) -> str:
    return text.replace("\x0c", "").replace("\x7f", "").strip()

# -------------------------
# Paths
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "study_visa_info.json")

# Ensure data folder exists
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# -------------------------
# Read PDFs and convert to JSON
# -------------------------
def pdfs_to_json():
    data = {"countries": []}

    for filename in os.listdir(PDF_DIR):
        if filename.endswith(".pdf"):
            country_name = filename.replace(".pdf", "")
            file_path = os.path.join(PDF_DIR, filename)

            try:
                reader = PdfReader(file_path)
                chunks = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text = clean_text(text)
                        chunks.append(text)

                data["countries"].append({
                    "name": country_name,
                    "chunks": chunks
                })

                print(f"[✅] Processed {filename}, {len(chunks)} chunks")

            except Exception as e:
                print(f"[❌] Error processing {filename}: {e}")

    # Save JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n[🎯] All PDFs processed. JSON saved at {OUTPUT_FILE}")

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    pdfs_to_json()
