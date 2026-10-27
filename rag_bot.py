"""
rag_bot.py - the "brain" of the QodeBench support bot (RAG chain).

Run it directly to DEBUG one question - it prints the 3 retrieved chunks
and the final answer, so you can tell a RETRIEVAL failure from a
GENERATION failure:

    python rag_bot.py "I forgot my login details, what do I do?"
"""
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectorstore = Chroma(
    persist_directory=str(BASE_DIR / "chroma_db"),
    embedding_function=embeddings,
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # top 3 relevant chunks

template = """You are a helpful customer support assistant.
Answer the questions using ONLY the context below.
If the answer is not in the context, say
"I'm sorry, I don't have that information."

Context: {context}
Question: {question}
Answer:"""

prompt = ChatPromptTemplate.from_template(template)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def format_docs(docs):
    # join the 3 retrieved chunks into one block of context text
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


def ask(question: str) -> str:
    """Question in, answer out. Used by every test file."""
    return rag_chain.invoke(question)


def retrieve(question: str) -> list[str]:
    """Only the retrieval step: which chunks did the bot actually see?"""
    return [doc.page_content for doc in retriever.invoke(question)]


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "I forgot my login details, what do I do?"
    print("QUESTION:", q)
    print("=" * 60)
    for i, chunk in enumerate(retrieve(q), start=1):
        print(f"--- retrieved chunk {i} ---")
        print(chunk)
    print("=" * 60)
    print("ANSWER:", ask(q))
