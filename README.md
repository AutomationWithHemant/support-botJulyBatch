# QodeBench Support Bot - Full Test Pipeline (Session 24)

A RAG customer-support chatbot plus a complete test pipeline:

| Layer | What it catches | Tool | File |
|---|---|---|---|
| Quality | wrong / missing answers, answering out-of-scope questions | Python, Promptfoo, DeepEval | `test_quality.py`, `promptfooconfig.yaml`, `test_hallucination.py` |
| API | endpoint errors, wrong status codes | requests | `test_api.py` |
| UI | input box, send button, answers shown on the page | Playwright | `ui-tests/` |
| Security | prompt injection, prompt leaks, off-topic use, harmful content | Promptfoo red team, Giskard | `redteam_config.yaml`, `giskard_scan.py` |
| Monitoring | every live question traced: chunks, prompt, tokens, cost | Langfuse | `rag_bot_traced.py` |

## Setup (once)

```bash
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # then put your real keys in .env (no quotes)

cd ui-tests && npm install && npx playwright install chromium && cd ..
```

## Run order

```bash
python ingest.py                    # 1. FAQ -> chunks -> chroma_db/  (safe to re-run)
python rag_bot.py "your question"   # 2. debug: shows the 3 retrieved chunks + the answer
uvicorn app:app --port 8000         # 3. server: /docs = Swagger, / = chat page

# Quality
python test_quality.py              # 20 keyword checks, prints chunks for every failure
npx promptfoo@0.125.0 eval          # same 20 cases + one LLM-rubric check
npx promptfoo@0.125.0 view          # report in the browser
python test_hallucination.py        # DeepEval: hallucination + answer relevancy + sanity check

# API + UI  (server must be running)
python test_api.py
cd ui-tests && npx playwright test && cd ..

# Security  (SLOW - run the night before, show the report in class)
npx promptfoo@0.125.0 redteam run -c redteam_config.yaml -o redteam.yaml
npx promptfoo@0.125.0 redteam report
python giskard_scan.py

# Monitoring
python rag_bot_traced.py            # then Langfuse -> Tracing

# Everything in one go
python run_all.py                   # quality + API + UI
python run_all.py --security        # + Giskard + red team
```

## Things that trip people up

- **DeepEval hallucination score: higher is better (DeepEval 4.2+).** 1.0 = grounded, 0.0 = contradicts the context, pass when score >= threshold. Older tutorials say "lower is better" - that was DeepEval 3.x. Check with `pip show deepeval`.
- **Context for DeepEval = the retrieved chunks**, not the whole FAQ as one string. With one context item the score can only be 0 or 1.
- **A correct refusal scores ~0 on answer relevancy.** That is expected, so relevancy only runs on in-scope questions.
- **Out-of-scope tests need a must-NOT-contain check.** "Sorry, but it's Paris" contains "sorry" and would pass a refusal-only check.
- **Retrieval vs generation:** when a test fails, look at the chunks first. Right chunk retrieved but the bot refused = generation problem (prompt/model). Wrong chunks = retrieval problem (chunking/embeddings/k).
- **Giskard 3.x** removed `giskard.Model` / `giskard.Dataset`. Install `giskard-scan` and use `vulnerability_scan(...)`.
- **Langfuse traces missing?** 401 = wrong keys or wrong region (EU `cloud.langfuse.com` vs US `us.cloud.langfuse.com`). Timeout = network/VPN/firewall. Never put quotes around values in `.env`.
- **Pin versions.** `@latest` and unpinned `pip install` are why code that worked last week breaks today.
- **Never push `.env`** - it is in `.gitignore`.
