"""
ingest.py - load the FAQ, split it into chunks, store them in ChromaDB.
Run once before anything else:  python ingest.py
"""
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
DB_DIR = BASE_DIR / "chroma_db"

# Running ingest twice would ADD the same chunks again (duplicates),
# and duplicates crowd the top-3 search results. So start fresh each time.
if DB_DIR.exists():
    shutil.rmtree(DB_DIR)

docs = TextLoader(str(BASE_DIR / "company_faq.txt")).load()

# Splits at paragraphs first, then lines, then spaces - up to 300 characters.
# The 50-character overlap only matters when one paragraph is cut in two.
chunks = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50).split_documents(docs)

Chroma.from_documents(
    chunks,
    OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory=str(DB_DIR),
)

print(f"Stored {len(chunks)} chunks in {DB_DIR.name}/")
