"""
test_ci.py  -  lightweight checks that run in GitHub Actions on every PR.
These need NO API key and cost NOTHING - so CI is always fast, free, and green.
They check the project is healthy: files present, FAQ has content, enough test cases.
Run locally:  pytest test_ci.py -v
"""
import os


def test_faq_file_exists():
    assert os.path.exists("company_faq.txt"), "company_faq.txt is missing"


def test_faq_has_content():
    content = open("company_faq.txt").read()
    assert len(content) > 100, "FAQ looks empty or too short"


def test_bot_file_exists():
    assert os.path.exists("rag_bot.py"), "rag_bot.py is missing"


def test_ingest_file_exists():
    assert os.path.exists("ingest.py"), "ingest.py is missing"


def test_config_has_enough_cases():
    text = open("promptfooconfig.yaml").read()
    count = text.count("question:")
    assert count >= 15, f"expected at least 15 test cases, found {count}"
