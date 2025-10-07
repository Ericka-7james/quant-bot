# 🔎 Phase 1 Dashboard — Buzz & Market Peek

This guide explains how to **generate buzz data** and **launch the Streamlit dashboard** inside **GitHub Codespaces** or a local environment.

---

## 🧰 Prerequisites

- Python 3.10 +
- Virtual environment (`.venv`)
- Installed dependencies (`requirements.txt`)

If not yet installed:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
⚙️ Generate Buzz Data
bash
Copy code
python -m src.ml.data.ingest_buzz --date 2025-10-05
This creates a file under:

bash
Copy code
data/buzz/2025-10-05.csv
Column	Description
date	Date of snapshot
ticker	Stock symbol mentioned
mentions	How many times it appeared
avg_sentiment	Mean VADER sentiment (−1 to +1)
sources	RSS/Reddit feeds containing the mention

🖥️ Launch Dashboard
bash
Copy code
streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0
UI Sections
Section	Description
Top Mentioned Tickers	Bar chart of tickers by mention volume
Average Sentiment	Tone of discussions (green = bullish, red = bearish)
Raw Buzz Rows	Expandable table of every parsed entry
Quick Price Peek	Live price chart via Yahoo Finance (yfinance)

🧠 How to Interpret
High Mentions + Positive Sentiment → bullish attention

High Mentions + Negative Sentiment → bearish panic / news event

Low Mentions / Neutral → background tickers with no chatter

🧩 Related Docs
11 – Ingest Buzz — how the buzz data is collected.

12 – Ingest Prices — market data for price context.