# Three-Model Plan for Forecasting

## Purpose
Instead of hardcoding buy/sell rules, the first stage of `quant-bot` is to **forecast short-term direction**.  
These forecasts will be ranked, explained, and logged. Execution logic can be layered on later.

---

## Model 1 — Nowcast (Immediate Trend)
**Question:** *Given today’s state, what’s the next move?*  
- **Inputs:**  
  - Short-term returns (1, 3, 5, 10-day)  
  - Moving averages & crossovers (MA5, MA20, distance to MA)  
  - RSI(14), MACD histogram  
  - Volatility (ATR, Bollinger position)  
  - Liquidity signals (volume z-score, turnover)  
- **Target:** `+1` if next K-day return > threshold (e.g., +0.3%), else `0`.  
- **Approach:** Logistic regression or gradient boosting baseline.  
- **Output:** Probability that price rises in the next K days.

---

## Model 2 — Window Pattern Recognition (Past Context)
**Question:** *Does this recent pattern look like past upward moves?*  
- **Inputs:**  
  - Fixed window of normalized returns (e.g., last 20 trading days)  
  - Aggregated stats: mean, slope, min/max, volatility  
  - Same indicators as Model 1 but window-summarized  
- **Target:** Future K-day return sign  
- **Approach:** Gradient boosting on aggregates; later test 1D CNNs or LSTMs  
- **Output:** Probability that the window leads to an upward move.

---

## Model 3 — News-Aware Forecast (Headline Sentiment)
**Question:** *Do recent headlines suggest upside?*  
- **Inputs:**  
  - Article counts in last 24–72 hours  
  - Simple sentiment score of titles  
  - Number of distinct sources  
  - Recency of last headline  
- **Target:** Same K-day return direction as above  
- **Approach:** Start with counts + sentiment; extend with embeddings later  
- **Output:** Probability that news flow supports upward direction.

---

## Evaluation
- **Splits:** Walk-forward / time-series split (no leakage).  
- **Metrics:**  
  - AUC  
  - Precision@K (how many top predictions were right)  
  - Average forward return of top decile  
- **Backtest:** Apply ranked predictions to simulated trades with slippage + fees.

---

## Explainability
Every forecast must output a **Reason Table** row:  
- Inputs summary (key indicators / headline stats)  
- Model probability (e.g., `P(up in 3d)=0.63`)  
- Rank position among universe  
- Top contributing features (feature importance / SHAP values later)

---

## Roadmap
- **Phase 1:** Build dataset pipeline (features, labels, datasets) + Nowcast baseline  
- **Phase 2:** Add window-pattern recognition features + evaluate  
- **Phase 3:** Integrate news counts & sentiment  
- **Phase 4:** Explore deep models (CNN/LSTM), embeddings, ensemble of all three
