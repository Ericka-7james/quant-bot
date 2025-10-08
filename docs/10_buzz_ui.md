# 🔎 Phase 1 Dashboard — Buzz & Market Peek

This page explains how to generate the buzz data and launch the Streamlit dashboard in **GitHub Codespaces**.

---

## 1) Prereqs (Codespaces)
- Python venv is already in this repo at `.venv`
- Dependencies are in `requirements.txt`

If needed:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

---

## 2) How to generate buzz data
python -m src.ml.data.ingest_buzz --date YYYY-MM-DD
# example:
python -m src.ml.data.ingest_buzz --date 2025-10-05

    This creates a CSV file under:

    data/buzz/YYYY-MM-DD.csv


Each row in that file represents:

Column	Description
date	The snapshot date of the data
ticker	Stock symbol mentioned
mentions	How many times it appeared in news/feeds
avg_sentiment	Average tone of mentions (−1 = very negative +1 = very positive)
sources	Which feeds contained the mentions
