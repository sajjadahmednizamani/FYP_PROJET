import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings # ✅ Local Model
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

# ✅ Paths setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "data", "pdfs") 
DB_FAISS_PATH = os.path.join(BASE_DIR, "vectorstore", "db_faiss")

def create_vector_db():
    # 1. Folder check
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)
        print(f"❌ Folder missing! Created at {PDF_DIR}. Add your PDFs there.")
        return

    print("--- Step 1: Loading PDFs ---")
    loader = DirectoryLoader(PDF_DIR, glob='*.pdf', loader_cls=PyPDFLoader)
    documents = loader.load()
    
    if not documents:
        print("❌ Error: No PDFs found in 'data/pdfs' folder.")
        return

    print(f"--- Step 2: Splitting {len(documents)} pages ---")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    texts = text_splitter.split_documents(documents)

    print("--- Step 3: Creating Local Embeddings (Safe & Offline) ---")
    # ✅ Local model use kar rahe hain taake 404 error na aaye
    embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2',
        model_kwargs={'device': 'cpu'}
    )

    print("--- Step 4: Saving Vector Store ---")
    vector_db = FAISS.from_documents(texts, embeddings)
    vector_db.save_local(DB_FAISS_PATH)
    
    print(f"✅ SUCCESS: Vector Store created at {DB_FAISS_PATH}")

if __name__ == "__main__":
    create_vector_db()