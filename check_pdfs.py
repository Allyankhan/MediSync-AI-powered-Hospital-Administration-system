import os
from pypdf import PdfReader

# Make sure this points to your actual data folder
DATA_DIR = "data" 

def check_files():
    print("Checking PDFs for corruption...\n")
    
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".pdf"):
            filepath = os.path.join(DATA_DIR, filename)
            try:
                # Attempt to read the PDF
                PdfReader(filepath)
                print(f"✅ OK: {filename}")
            except Exception as e:
                # If it crashes, catch the error and print the bad file's name
                print(f"❌ CORRUPTED: {filename} -> Error: {e}")

if __name__ == "__main__":
    check_files()