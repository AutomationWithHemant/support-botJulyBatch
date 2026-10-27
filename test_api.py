"""
test_api.py - API-level tests: send questions over HTTP to the running server.
Needs the server running first:  uvicorn app:app --port 8000
Run:  python test_api.py
"""
import sys

import requests

URL = "http://localhost:8000/chat"

# (question, keyword the answer must contain)
cases = [
    ("I forgot my password, what are the steps to recover it?", "reset"),
    ("What are your support hours?", "monday"),
    ("Do you accept cryptocurrency?", "don't have"),
    ("What is the capital of France?", "don't have"),
]

passed = 0
for q, keyword in cases:
    try:
        response = requests.post(URL, json={"question": q}, timeout=60)
    except requests.exceptions.ConnectionError:
        print("Server is not running. Start it with:  uvicorn app:app --port 8000")
        sys.exit(1)

    if response.status_code != 200:
        print(f"FAIL  {q}  (HTTP {response.status_code})")
        continue

    answer = response.json()["answer"]
    ok = keyword in answer.lower().replace("’", "'")  # treat curly ' as straight '
    print(("PASS " if ok else "FAIL "), q)
    print("      A:", answer)
    passed += ok

print("-" * 60)
print(f"RESULT: {passed}/{len(cases)} passed")
sys.exit(0 if passed == len(cases) else 1)
