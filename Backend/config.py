import os
from dotenv import load_dotenv
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")


DB_DIR=os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector_db")
DATA_DIR=os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

CHUNK_OVERLAP = 200
CHUNK_SIZE = 1000
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-3.5-turbo"
MYSQL_URI = "mysql+pymysql://root:@localhost/hospital_ai"