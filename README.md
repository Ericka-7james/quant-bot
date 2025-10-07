# 🧠 quant-bot

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/Ericka-7james/quant-bot)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Ericka-7james/quant-bot)](https://github.com/Ericka-7james/quant-bot/commits/main)

An **experimental trading-intelligence project** — designed to learn, analyze, and evolve from financial data.

---

## 🧭 What Is Quant Bot?

Quant Bot is a learning-oriented ML system that:

1. **Listens** to the market (Reddit + RSS feeds).  
2. **Sees** stock behavior (daily price tracking + indicators).  
3. **Thinks** about relationships (predictive models).  
4. **Speaks** insights (dashboards & future reports).

The goal is to move from *learning how markets talk* → *building models that listen* → *earning with data-driven ideas.*

---

## 📘 Documentation Overview

| File | Description |
|------|--------------|
| [00 – Master Overview](docs/00_master_overview.md) | Vision, roadmap, and project phases (0–4). |
| [10 – Buzz UI](docs/10_buzz_ui.md) | How to generate buzz data and run the Streamlit dashboard. |
| [11 – Ingest Buzz](docs/11_ingest_buzz.md) | Technical breakdown of `src/ml/data/ingest_buzz.py`. |
| [12 – Ingest Prices](docs/12_ingest_prices.md) | Explanation and usage of `src/ml/data/ingest_prices.py`. |
| [13 – Train Nowcast](docs/13_train_nowcast.md) | Baseline predictor merging buzz + price data. |

---

# 🚀 Getting Started

### 1️⃣ Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
````

### 2️⃣ Generate Buzz Data

```bash
python -m src.ml.data.ingest_buzz --date 2025-10-05
```

→ Creates `data/buzz/2025-10-05.csv`

### 3️⃣ Fetch Market Data

```bash
python -m src.ml.data.ingest_prices --period 2y
```

→ Creates `data/market/daily.parquet`

### 4️⃣ Launch Dashboard

```bash
streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0
```

You’ll see three tabs:

* 📰 **Buzz & Market** — top-mentioned tickers & sentiment
* 📈 **Quick Price Peek** — live price chart
* 🔮 **Predictions** — model accuracy & ranked probabilities

---

## 🧩 Core Concepts

### 🧠 VADER Sentiment

**VADER** (Valence Aware Dictionary and sEntiment Reasoner) scores text between −1 (very negative) and +1 (very positive).
Optimized for short, informal sentences such as Reddit posts or headlines.

| Example Text                               | Score | Meaning      |
| ------------------------------------------ | ----- | ------------ |
| “Tesla smashes delivery record!”           | +0.81 | bullish tone |
| “Amazon stock crashes after weak forecast” | −0.65 | bearish tone |

---

### 🎯 Model Metrics

#### Accuracy

How often the model correctly predicts next-day up/down moves.
A random baseline is **0.500**; anything above **0.52** starts showing weak predictive signal.

#### Decile Spread (Toy Alpha)

Measures how much better the top 10% of predictions perform than the bottom 10%.

1. Rank stocks by predicted probability of going up.
2. Split into 10 equal “deciles.”
3. Compute:

   ```
   top decile avg return − bottom decile avg return
   ```

   → That’s your **daily spread**, which is annualized via `(1 + daily)^252 − 1`.
   Positive = model captures real structure.

#### Predicted Probability

Each prediction is a probability between 0 and 1 that tomorrow’s return will be positive.
Example: `0.78` = 78% chance the stock will rise → ranks high in dashboard.

---

## 🧱 Pipeline Summary

| Phase | Name                         | Purpose                                                       | Output                         |
| ----- | ---------------------------- | ------------------------------------------------------------- | ------------------------------ |
| **0** | Ticker Universe              | Defines which symbols to track (e.g., S&P 500).               | `data/universe/sp500.csv`      |
| **1** | Buzz Finder *(The Ears)*     | Collects Reddit/news sentiment & mentions.                    | `data/buzz/YYYY-MM-DD.csv`     |
| **2** | Market Tracker *(The Eyes)*  | Fetches daily prices & technical indicators.                  | `data/market/daily.parquet`    |
| **3** | Predictor *(The Brain)*      | Trains ML models to predict next-day up/down.                 | Model metrics + dashboard view |
| **4** | Idea Generator *(The Voice)* | (Future) Turns signals into natural-language daily summaries. | Markdown report                |

---

## 📊 Example Run

```bash
python -m src.ml.data.ingest_buzz --date 2025-10-05
python -m src.ml.data.ingest_prices --period 2y
python -m src.ml.models.train_nowcast
```

### Sample Output

```
== LogReg ==
Holdout accuracy: 0.531 (baseline 0.500)
Top-Bottom decile daily spread: 0.0478%
Top-Bottom decile annualized (toy): 12.6%

== RandForest ==
Holdout accuracy: 0.546 (baseline 0.500)
Top-Bottom decile daily spread: 0.0563%
Top-Bottom decile annualized (toy): 14.9%
```

**Interpretation:**
Both models perform slightly above random.
Positive daily spread = small but meaningful “toy alpha.”

---

## 📂 Docs Cross-Links

* 📰 [**Buzz & Dashboard Guide**](docs/10_buzz_ui.md) — run and interpret the Streamlit UI.
* 🧾 [**Ingest Buzz Script**](docs/11_ingest_buzz.md) — RSS + Reddit sentiment collector using VADER.
* 💹 [**Ingest Prices Script**](docs/12_ingest_prices.md) — price fetcher + feature builder.
* 🧮 [**Train Nowcast Script**](docs/13_train_nowcast.md) — baseline ML predictor.

---

## 💡 Next Steps

* Automate daily updates via GitHub Actions or cron.
* Add more features (buzz momentum, volatility regimes).
* Export top predictions to daily Markdown reports or Slack alerts.

---

### 🏁 Project Status

| Phase                    | Status          | Deliverable                 |
| ------------------------ | --------------- | --------------------------- |
| Phase 0 — Universe       | ✅ Complete      | `sp500.csv` loader          |
| Phase 1 — Buzz Finder    | ✅ Complete      | `ingest_buzz.py`, Buzz CSVs |
| Phase 2 — Market Tracker | ✅ Complete      | `ingest_prices.py`, Parquet |
| Phase 3 — Predictor      | ✅ Baseline done | `train_nowcast.py`, UI tab  |
| Phase 4 — Idea Generator | 🧩 In progress  | Future daily reports        |

---

### ✍️ Author

**Ericka James (@Ericka-7James)**
Software Engineer | Quant Learner | Builder of *Quant Bot*

```

---

✅ Just copy and paste that entire block into your root `README.md`.  
It’s 100% Markdown-ready with links, examples, and explanations for **VADER**, **accuracy**, **decile spread**, and **predicted probabilities**.
```