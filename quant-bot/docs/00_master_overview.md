# 🧭 Quant Bot Master Overview  
**Project Goal:** From learning → building → earning.

---

## 1. 💡 Core Vision  

### 🎯 Purpose  
Build a system of small machine-learning models that *listen to the market*, *analyze trends*, and *generate daily investment ideas.*

### 🧠 Why It Matters  
- Learn real applied ML and finance hands-on.  
- Automate stock research (no more endless tab-scrolling).  
- Grow a side stream of income through data-driven insight.

### 🏁 End Prize  
A working “Quant Bot” that can:  
1. Gather and summarize market chatter.  
2. Track live stock movements.  
3. Predict likely short-term price trends.  
4. Produce daily investment thoughts or watchlists.  

Later, this same engine could evolve into:  
- A **personal trading assistant**.  
- A **signals dashboard** or **Substack**.  
- A **public API or SaaS** project.  

---

## 2. 🏗️ The Journey (Zero → Bot → Income)

### **Phase 0 — Foundation: Learn + Setup**
**Purpose:**  
Understand the building blocks—data, sentiment, and prediction.  

You’ll learn:  
- Stock market data basics (price, returns, volatility).  
- Sentiment analysis from text.  
- How ML can link buzz + price patterns.  

**Deliverable:**  
Your first data folders and notebooks with basic charts.

---

### **Phase 1 — The Ears (Buzz Finder)**
**Goal:**  
Collect data on what tickers people are talking about.  

**Tasks:**  
- Pull Reddit and RSS feeds.  
- Extract tickers (e.g., `$AAPL`, `TSLA`).  
- Use VADER to score sentiment.  
- Save results → `data/buzz/YYYY-MM-DD.csv`.  

**Deliverable:**  
List of tickers ranked by mentions and sentiment.  

**Early UI Idea:**  
Simple Streamlit bar chart of top-mentioned tickers and their tone.

---

### **Phase 2 — The Eyes (Market Tracker)**
**Goal:**  
Track what’s actually happening in the market.  

**Tasks:**  
- Download daily price data via `yfinance`.  
- Compute indicators (returns, RSI, 52-week high/low distance).  
- Merge with buzz data.  

**Deliverable:**  
Merged dataset of tickers with buzz + price stats.  

**UI Idea:**  
Line chart comparing price vs. buzz volume for selected ticker.

---

### **Phase 3 — The Brain (Predictor)**
**Goal:**  
Predict short-term movements (next-day up/down).  

**Tasks:**  
- Train logistic regression + random forest models.  
- Use buzz + technical indicators as features.  
- Evaluate accuracy and decile spreads.  

**Deliverable:**  
Performance report (accuracy ≥ 0.52 baseline).  

**UI Idea:**  
Table view of model predictions with confidence scores.

---

### **Phase 4 — The Voice (Idea Generator)**
**Goal:**  
Turn signals into readable daily insights.  

**Tasks:**  
- Combine prediction output + buzz + risk metrics.  
- Output Markdown reports like:  