import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from config import DB_DIR, EMBEDDING_MODEL, LLM_MODEL

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from langchain_community.vectorstores import Chroma

from langchain_core.prompts import ChatPromptTemplate

from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain,
)


def get_rag_chain():

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    vectorstore = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k":2}
    )

    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0
    )

    system_prompt = """
You are a hospital administrative assistant.

Use ONLY the retrieved context.

If the answer is not available,
say:

"I cannot find that information in the hospital documents."

Never give medical advice.


Context:

{context}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system",system_prompt),
        ("human","{input}")
    ])

    qa_chain = create_stuff_documents_chain(
        llm,
        prompt
    )

    return create_retrieval_chain(
        retriever,
        qa_chain
    )