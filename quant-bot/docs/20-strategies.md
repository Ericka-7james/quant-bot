# Strategies

## Purpose
This document records the trading strategies used in `quant-bot`. Each entry should explain:
- The **logic/rules**
- Key **indicators/inputs**
- **Risk checks** applied before execution
- Example **Reason Table output**

---

## Current Strategies
### Equity Price Rules (v0.1)
- Configurable in `rules.yml`
- Example:
  ```yaml
  AAPL:
    buy_below: 165
    take_profit: 195
    stop: 158
    max_size_pct: 4
