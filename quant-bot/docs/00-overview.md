# Project Overview

# Project Overview

## What is `quant-bot`?
`quant-bot` is an experimental trading bot designed to:
- Collect stock, IPO, and options data
- Apply **rule-based strategies** (and eventually ML models)
- Generate **buy/sell signals** with clear explanations
- Execute trades via broker APIs (paper → live)
- Keep detailed **documentation** for transparency and learning

This project is primarily a **learning lab**: the focus is on building, documenting, and experimenting with systematic trading ideas in a safe and explainable way.

---

## Guiding Principles
1. **Transparency**  
   Every signal and trade should come with a logged reason (in tables/logs).

2. **Safety First**  
   Start with **paper trading**, enforce strict position and risk limits before any real money.

3. **Iterative Growth**  
   Begin with simple rules → add IPO watchlists → integrate options → explore ML.

4. **Documentation**  
   Everything new (data source, strategy, risk rule) gets written down here in `/docs`.

---

## Roadmap (Phases)
- **Phase 1: Rules + Paper Trading**  
  - Implement basic price-point rules (`rules.yml`)  
  - Generate daily Reason Tables  
  - Paper trade via Alpaca  

- **Phase 2: IPO + Options Integration**  
  - Add IPO watchlists (wait after open, liquidity checks)  
  - Experiment with simple option strategies (covered calls, CSPs)

- **Phase 3: Explanations & Logs**  
  - Expand Reason Tables to include indicators, risk checks, and news sentiment  
  - Store logs in CSV/DB for later analysis

- **Phase 4: Dashboards**  
  - Streamlit dashboard to visualize signals, trades, and performance  

- **Phase 5: Automation**  
  - Live trading (very small size) with circuit breakers and full audit trail

---

## Questions We’re Exploring
- Which data sources are most reliable for IPOs and options?  
- How do we avoid bad trades (low liquidity, wide spreads, news halts)?  
- What’s the simplest way to explain signals clearly in tables?  
- How do paper-trade results compare to backtests?  
- When is it safe (and useful) to turn on auto-execution?

---

## Current Status
🚧 *Early stage*: repo scaffold + documentation setup.  
✅ Next step: build the first data loader and produce a Reason Table for one ticker.
