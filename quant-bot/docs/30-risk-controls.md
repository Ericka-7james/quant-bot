# Risk Controls

## Purpose
This document defines the risk rules applied before `quant-bot` executes any trade. Risk is non-negotiable: every signal must pass these checks.

---

## Position-Level Controls
- Max position size: **5% of total equity**
- Stop-loss required on every trade
- Minimum liquidity thresholds:
  - Equities: 1M+ average daily volume
  - Options: OI > 1000, bid-ask spread < $0.10

---

## Account-Level Controls
- Max daily loss: **–3% of account** (no new trades once breached)
- Max concurrent open positions: **5**
- Correlation cap: no more than **2 positions in highly correlated tickers** (e.g., AAPL + MSFT)

---

## Special Rules
- No trading within 2 days before/after earnings announcements
- IPOs: no entry until at least 15 min after market open, plus liquidity checks
- Options: avoid contracts with < 10 days to expiry unless hedging

---

## To-Do
- [ ] Implement automated risk gate in `execution/risk.py`
- [ ] Add configurable limits in `config/rules.yml`
- [ ] Test circuit breaker (auto-shutoff after daily drawdown)
