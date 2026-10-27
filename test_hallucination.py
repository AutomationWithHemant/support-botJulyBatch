"""
test_hallucination.py - DeepEval checks on OUR RAG bot.
Run:  python test_hallucination.py

SCORE DIRECTION (DeepEval 4.2 and later):
  HallucinationMetric score = share of contexts the answer does NOT contradict.
  1.0 = fully grounded (good)      0.0 = contradicts the context (bad)
  Pass when score >= threshold. Older blogs/videos say "lower is better" -
  that was DeepEval 3.x. Always check:  pip show deepeval
"""
import sys
from importlib.metadata import version

from dotenv import load_dotenv
load_dotenv()

from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric
from deepeval.test_case import LLMTestCase
from rag_bot import ask, retrieve

print("DeepEval version:", version("deepeval"))
THRESHOLD = 0.8

# (question, is it in the FAQ?)
questions = [
    ("What are your support hours?", True),
    ("How do I get a refund?", True),
    ("Do you accept cryptocurrency?", False),    # out of scope - should refuse
    ("What is the capital of France?", False),   # out of scope - should refuse
]

all_ok = True

for q, in_scope in questions:
    answer = ask(q)

    # context = the chunks the bot ACTUALLY retrieved (3 items), not the whole FAQ.
    # With the whole FAQ as ONE item, the score can only ever be 0 or 1.
    case = LLMTestCase(input=q, actual_output=answer, context=retrieve(q))

    hallucination = HallucinationMetric(threshold=THRESHOLD)
    hallucination.measure(case)

    print("Q:", q)
    print("A:", answer)
    print(f"Hallucination score: {hallucination.score:.2f} (higher is better) ->",
          "PASS" if hallucination.success else "FAIL")
    print("Reason:", hallucination.reason)
    all_ok = all_ok and hallucination.success

    # Answer relevancy only makes sense for in-scope questions.
    # A correct refusal ("I'm sorry...") is NOT relevant to the question,
    # so it would score ~0 even though the bot behaved correctly.
    if in_scope:
        relevancy = AnswerRelevancyMetric(threshold=THRESHOLD)
        relevancy.measure(case)
        print(f"Answer relevancy:    {relevancy.score:.2f} (higher is better) ->",
              "PASS" if relevancy.success else "FAIL")
        all_ok = all_ok and relevancy.success
    print("-" * 60)

# ---- Sanity check: prove the metric catches a WRONG answer ----
# Never trust a metric until you have seen it fail on purpose.
bad_q = "What are your support hours?"
bad_case = LLMTestCase(
    input=bad_q,
    actual_output="Our support team is available 24/7, including weekends.",
    context=retrieve(bad_q),
)
bad_metric = HallucinationMetric(threshold=THRESHOLD)
bad_metric.measure(bad_case)
caught = not bad_metric.success
print("SANITY CHECK - deliberately wrong answer: '24/7, including weekends'")
print(f"Hallucination score: {bad_metric.score:.2f} ->",
      "correctly FAILED (metric works)" if caught else "PASSED - metric did NOT catch it!")
all_ok = all_ok and caught

sys.exit(0 if all_ok else 1)
