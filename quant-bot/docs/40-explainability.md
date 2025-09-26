# Explainability & Logging

## Purpose
This document defines how `quant-bot` explains its decisions. Every signal and trade should be easy to interpret — no black boxes. The output should answer **why** the bot made a decision.

---

## Reason Tables
Each signal produces a **Reason Table** (CSV/Markdown/console).  
Columns may include:

| Field          | Example Value                 | Description                                     |
|----------------|-------------------------------|-------------------------------------------------|
| Ticker         | AAPL                          | Symbol evaluated                                |
| Price (Now)    | 172.40                        | Current price at evaluation                     |
| Rule Triggered | `buy_below=165`               | Which rule or indicator fired                   |
| Key Inputs     | EMA20=171.9, RSI=28 (<30)     | Relevant indicator values                       |
| Risk Checks    | Pos ≤ 5% equity, liquidity OK | Risk rules verified before signal               |
| Suggested Act. | **Buy 30 shares**             | Suggested order or action                       |
| Order Details  | Stop=168.95, TP=178.30        | Execution details (stop-loss, take-profit)      |
| Notes          | Mean reversion entry          | Free-form explanation / context                 |

---

## Logging
- **File Logs**
  - Stored in `/logs/`
  - One CSV per day with all Reason Tables
  - Additional `.log` file for errors/exceptions
- **Database (optional)**
  - SQLite/Postgres for longer-term trade history
  - Tables: `signals`, `orders`, `fills`, `errors`

---

## Explainability Rules
- Every signal must output **what triggered** (rule/indicator).
- Every trade must output **why it passed risk checks**.
- Logs must include **date, time, source, and raw inputs**.
- Explanations should be **short, tabular, and human-readable**.

---

## Planned Features
- Streamlit dashboard to view daily Reason Tables
- News sentiment column (e.g., `news_heat=4 articles last 24h`)
- SHAP or feature attribution for future ML models
