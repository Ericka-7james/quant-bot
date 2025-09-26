# ⚡ 2-Week Roadmap for `quant-bot`

---

## Week 1 – Foundation & Confidence
**Goal:** Get the project running locally, start documentation, and produce one simple signal.

### Day 1–2
- Finish setting up the repo + GitHub sync  
- Write `README.md` + `docs/00-overview.md`  
- Create a simple `rules.yml` with one ticker  
  - Example: `AAPL` → buy below $165, sell above $195  
- Make your first commit + push 🚀  

### Day 3–4
- Add a basic data loader (pull daily OHLCV bars for AAPL from Polygon/Finnhub)  
- Store results in a CSV (just to prove the pipeline works)  
- Document data sources in `docs/10-data-sources.md`  

### Day 5
- Write a tiny script to evaluate `rules.yml` against the latest price  
- Print a **Reason Table** to console (ticker, price, signal, reason)  
- 🎉 Celebrate: you’ve built your first signal engine!  

### Day 6–7 (Weekend)
- Relax 😎  
- If you want:  
  - Flesh out `docs/20-strategies.md` with a few sentences about your rule logic  
  - Add an “Example signal output” to the README  

---

## Week 2 – Extend & Play
**Goal:** Add one extra feature, improve logging, and prepare for paper trading.

### Day 8
- Add logging: save each Reason Table to a CSV in `/logs`  
- Document logging approach in `docs/40-explainability.md`  

### Day 9–10
- Add a news fetcher for 1 ticker (using NewsAPI or RSS)  
- Tag signals with `news_heat` = number of articles in the last 24h  

### Day 11
- Try a second ticker (MSFT, TSLA, SPY — whatever excites you)  
- Update `rules.yml` to handle multiple tickers  

### Day 12
- Install `alpaca-trade-api` (or just stub it for now)  
- Document basic risk caps in `docs/30-risk-controls.md`  
  - Example: “No more than 5% of account in one trade”  

### Day 13
- Add a simple **Streamlit** page to view Reason Tables  
- Doesn’t need to be pretty — just proof the dashboard works  

### Day 14
- Write a reflection in `docs/50-deploy-ops.md`:  
  - What works so far?  
  - What confused you?  
  - What you want to try in the next sprint  

---

## 🌱 Key Principles
- **One small win per day** → don’t try to do IPOs, options, and auto-trading at once  
- **Paper before live** → focus on getting signals right, not making profit right away  
- **Document as you go** → each doc page = future-you’s guidebook  

---

## ✨ By the End of 2 Weeks
You’ll have:
- A repo with **working docs**  
- A bot that can **load data, check rules, and output Reason Tables**  
- A clear **roadmap** for next steps (IPO, options, execution)  
