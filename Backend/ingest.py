import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
from config import DB_DIR, DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, LLM_MODEL
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def build_vector_database():
    print(f"1. Scanning {DATA_DIR} for documents...")

   # 1. Load Text files
    print("Loading Text files...")
    text_loader = DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader)
    txt_docs = text_loader.load()

    # 2. Load PDF files
    print("Loading PDF files...")
    pdf_loader = DirectoryLoader(DATA_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader)
    pdf_docs = pdf_loader.load()

    # 3. Combine them all together
    documents = txt_docs + pdf_docs
    if not documents:
        print("No documents found!! Please add files to your data/ folder.")
        return
        
    print(f"Loaded {len(documents)} document(s).")
    print("2. Splitting documents into smaller chunks.....")

    # Double check if your config has uppercase or lowercase variable names
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    print("3. Generating Embeddings and saving to disk.....")

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    # Fixed typo: changed .form_documents to .from_documents
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )

    print("\n✅ Ingestion Completed! Vector database is ready.")

# Fixed Indentation: Moved completely to the left margin
if __name__ == "__main__":
    build_vector_database()