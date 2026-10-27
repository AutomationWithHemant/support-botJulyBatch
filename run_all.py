"""
run_all.py - the full test pipeline in ONE command.

    python run_all.py              # quality + API + UI   (fast - every code change)
    python run_all.py --security   # also Giskard + red team (slow - nightly)

Why two levels? Quality checks take a minute and cost cents, so they run on
every change. Security scans take much longer and cost more, so real teams
run them nightly or before a release.
"""
import subprocess
import sys
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
PY = sys.executable                      # the Python of the active venv
PROMPTFOO = "promptfoo@0.125.0"          # pinned: "@latest" can change under you overnight

FAST = [
    ("Quality - Python keyword checks", [PY, "test_quality.py"], BASE_DIR),
    ("Quality - Promptfoo eval", ["npx", "-y", PROMPTFOO, "eval", "-c", "promptfooconfig.yaml"], BASE_DIR),
    ("Quality - DeepEval hallucination", [PY, "test_hallucination.py"], BASE_DIR),
]
NEEDS_SERVER = [
    ("API - FastAPI /chat", [PY, "test_api.py"], BASE_DIR),
    ("UI - Playwright", ["npx", "playwright", "test"], BASE_DIR / "ui-tests"),
]
SECURITY = [
    ("Security - Giskard scan", [PY, "giskard_scan.py"], BASE_DIR),
    ("Security - Promptfoo red team", ["npx", "-y", PROMPTFOO, "redteam", "run",
                                       "-c", "redteam_config.yaml", "-o", "redteam.yaml"], BASE_DIR),
]


def run(name, cmd, cwd):
    print("\n" + "=" * 70 + f"\n>>> {name}\n" + "=" * 70, flush=True)
    start = time.time()
    code = subprocess.run(cmd, cwd=cwd).returncode
    return name, code == 0, time.time() - start


def start_server():
    server = subprocess.Popen([PY, "-m", "uvicorn", "app:app", "--port", "8000"], cwd=BASE_DIR)
    for _ in range(30):                                # wait up to 30 s for /health
        try:
            if requests.get("http://localhost:8000/health", timeout=1).ok:
                return server
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    server.terminate()
    raise RuntimeError("Server did not start - try:  uvicorn app:app --port 8000")


def main():
    results = [run(*step) for step in FAST]

    server = start_server()
    try:
        results += [run(*step) for step in NEEDS_SERVER]
    finally:
        server.terminate()

    if "--security" in sys.argv:
        results += [run(*step) for step in SECURITY]

    print("\n" + "=" * 70 + "\nPIPELINE SUMMARY\n" + "=" * 70)
    for name, ok, secs in results:
        print(f"{'PASS' if ok else 'FAIL':5} {name:40} {secs:6.1f}s")
    failed = sum(not ok for _, ok, _ in results)
    print("-" * 70)
    print("ALL GREEN" if not failed else f"{failed} stage(s) failed - scroll up for details")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
