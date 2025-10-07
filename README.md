# quant-bot

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/Ericka-7james/quant-bot)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Ericka-7james/quant-bot)](https://github.com/Ericka-7james/quant-bot/commits/main)

An experimental trading bot project.

## 📚 Documentation

The `docs/` folder contains detailed notes on how `quant-bot` works. Use these pages to track progress, document new features, and guide future development.

- [00 - Overview](docs/00_master_overview.md)  
  High-level description, guiding principles, and roadmap.
- [10 – Buzz UI](docs/10_buzz_ui.md) — how to generate buzz data and run the dashboard


# 🚀 Getting Started with Quant Bot

This project builds a small ecosystem of machine-learning tools that analyze market buzz, track stock prices, and visualize trends.  
Below is how to **set up and run the first interactive dashboard** (Phase 1 — Buzz Finder).

---

## 🧩 Setup (in GitHub Codespaces or locally)

### 1. Create & activate your Python environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

### 2. Launch Streamlit dashboard
streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0
