# Quant-Bot ML

This folder contains documentation and exploratory notebooks for the machine learning track of `quant-bot`.

---

## Structure
- **three-model-plan.md**  
  Documentation of the three-model forecasting approach:
  1. **Nowcast** — short-term trend from today’s state  
  2. **Window Patterns** — learning from recent historical sequences  
  3. **News-Aware** — headlines and sentiment

- **notebooks/**  
  Interactive Jupyter notebooks used for experiments:
  - `01_sanity_checks.ipynb` → test data pipeline, labels, features  
  - `02_nowcast_baseline.ipynb` → first ML baseline for Nowcast model

---

## Notes
- These notebooks are for **experimentation and learning**.  
- Production-ready ML code (datasets, features, training scripts) should live under `src/ml/`.  
- Results, metrics, and design decisions should be logged back into the main `docs/` folder (e.g., `docs/60-ml-roadmap.md`).
