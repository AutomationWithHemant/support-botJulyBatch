"""
rag_bot_traced.py - the SAME bot, with Langfuse monitoring switched on.
Every question becomes a trace on the Langfuse dashboard:
question -> retrieved chunks -> prompt -> LLM call (tokens, cost, time) -> answer.

Run:  python rag_bot_traced.py
Then: Langfuse dashboard -> Tracing -> look for "qodebench-chat"

.env needs (NO quotes around the values):
  LANGFUSE_PUBLIC_KEY=pk-lf-...
  LANGFUSE_SECRET_KEY=sk-lf-...
  LANGFUSE_BASE_URL=https://cloud.langfuse.com      (EU project)
               or   https://us.cloud.langfuse.com   (US project)
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from langfuse import get_client, observe
from langfuse.langchain import CallbackHandler

from rag_bot import rag_chain

# ---------------------------------------------------------
# 1. Check the connection BEFORE sending anything
# ---------------------------------------------------------
langfuse = get_client()
base_url = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
print("Langfuse URL:", base_url)

try:
    langfuse.auth_check()
    print("Authentication: SUCCESS")
except Exception as e:
    print("Authentication: FAILED ->", type(e).__name__, e)
    print("401 / Unauthorized -> keys are wrong, OR the keys belong to the other region")
    print("                      (EU = cloud.langfuse.com, US = us.cloud.langfuse.com)")
    print("Timeout / connection -> network problem: office Wi-Fi, VPN or firewall")
    sys.exit(1)

# ---------------------------------------------------------
# 2. Trace the bot
# ---------------------------------------------------------
# @observe creates one trace per call (input = question, output = answer).
# The LangChain CallbackHandler adds the inner steps: retriever, prompt, LLM.
langfuse_handler = CallbackHandler()


@observe(name="qodebench-chat")
def ask_traced(question: str) -> str:
    return rag_chain.invoke(question, config={"callbacks": [langfuse_handler]})


questions = [
    "What are your support hours?",
    "How do I reset my password?",
    "I forgot my login details, what do I do?",
    "What is the capital of France?",
]

for q in questions:
    print("\nQ:", q)
    print("A:", ask_traced(q))

# ---------------------------------------------------------
# 3. Send everything before the script exits
# ---------------------------------------------------------
# Traces are sent in the background. A short script can exit before
# they are delivered - flush() waits until they are sent.
langfuse.flush()
print("\nTraces sent. Open Langfuse -> Tracing (refresh after ~10 seconds).")
