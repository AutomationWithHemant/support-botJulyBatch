"""
test_quality.py - 20 quality checks on OUR bot, pure Python (no extra tools).
Run:  python test_quality.py

Two kinds of test cases:
  in_scope     -> the answer is in the FAQ, so the answer must contain a keyword
  out_of_scope -> not in the FAQ, so the bot must REFUSE
                  and must NOT answer from its own memory (e.g. "Paris")
"""
import sys

from dotenv import load_dotenv
load_dotenv()
from rag_bot import ask, retrieve

REFUSAL = ["don't have", "do not have", "sorry"]

# (category, question, must contain at least ONE of these, must contain NONE of these)
cases = [
    ("in_scope", "What are your support hours?", ["monday"], []),
    ("in_scope", "When can I reach support?", ["9", "monday"], []),
    ("in_scope", "How do I reset my password?", ["reset"], []),
    ("in_scope", "I forgot my login details, what do I do?", ["reset", "password"], []),
    ("in_scope", "What is your refund policy?", ["14 days", "refund"], []),
    ("in_scope", "Can I get my money back?", ["refund"], []),
    ("in_scope", "How do I upgrade my plan?", ["billing", "upgrade"], []),
    ("in_scope", "Do you offer a free trial?", ["7", "trial"], []),
    ("in_scope", "Is there a trial available?", ["trial"], []),
    ("in_scope", "How can I contact a human agent?", ["support@qodebench.com", "email"], []),
    ("in_scope", "Is my data secure?", ["encryption", "secure"], []),
    ("in_scope", "What payment methods do you accept?", ["upi", "card"], []),
    ("in_scope", "Can I pay with a credit card?", ["card"], []),
    ("in_scope", "Can I cancel my subscription anytime?", ["cancel"], []),
    ("in_scope", "How do I export my data?", ["export"], []),
    ("out_of_scope", "What is the capital of France?", REFUSAL, ["paris"]),
    ("out_of_scope", "Do you accept cryptocurrency?", REFUSAL, ["bitcoin", "yes, we"]),
    ("out_of_scope", "Do you have an office in Mumbai?", REFUSAL, ["yes, we"]),
    ("out_of_scope", "What's the weather today?", REFUSAL, ["sunny", "rain", "degrees"]),
    ("out_of_scope", "Who is the CEO of QodeBench?", REFUSAL, ["ceo is"]),
]

passed = 0
failed = []

for category, q, must_have, must_not_have in cases:              # loop 1: each question
    answer = ask(q).lower().replace("’", "'")                # curly ' -> straight '

    # loop 2 (inside any): check each keyword against the answer.
    # It is the short form of:
    #     found = False
    #     for k in must_have:
    #         if k in answer:
    #             found = True
    found = any(k in answer for k in must_have)
    leaked = [k for k in must_not_have if k in answer]

    ok = found and not leaked
    print(("PASS " if ok else "FAIL "), f"[{category}]", q)
    if ok:
        passed += 1
    else:
        failed.append((q, answer, leaked))

print("-" * 60)
print(f"RESULT: {passed}/{len(cases)} passed")

# For every failure: show the answer AND the chunks the bot retrieved.
# Wrong chunks  -> RETRIEVAL problem (chunking, embeddings, k).
# Right chunks  -> GENERATION problem (prompt, model, temperature).
for q, answer, leaked in failed:
    print("\n" + "=" * 60)
    print("FAILED:", q)
    print("ANSWER:", answer)
    if leaked:
        print("MUST NOT CONTAIN, but found:", leaked)
    print("CHUNKS THE BOT SAW:")
    for i, chunk in enumerate(retrieve(q), start=1):
        print(f"  {i}. {chunk.splitlines()[0]}")

sys.exit(0 if not failed else 1)
