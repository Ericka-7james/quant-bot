# Deployment & Operations

## Purpose
This document defines how `quant-bot` is run, scheduled, and maintained in both development and production modes. The goal is safe, repeatable operations with clear monitoring.

---

## Environments
- **Local Dev**
  - Run jobs manually via Python scripts
  - Use paper trading only
  - Logs saved locally in `/logs/`

- **Staging (Optional)**
  - Cloud VM or Docker container
  - Daily scheduled jobs
  - Paper trading connected to broker API

- **Production**
  - Runs in a controlled environment (server or cloud)
  - Broker API live trading enabled (tiny size to start)
  - Circuit breakers and monitoring active

---

## Scheduling
- **Daily Jobs**
  - End-of-day scan (EOD data → Reason Tables)
  - IPO calendar update
- **Intraday Jobs**
  - Run every 5–15 minutes during market hours
  - Refresh signals, update Reason Tables, check risk gates
- **Weekly Jobs**
  - Backtests with updated data
  - Generate performance reports

---

## Monitoring
- **Logs**
  - `/logs/` folder (rotated daily)
  - Error log separate from Reason Tables
- **Alerts**
  - Email/Slack/Discord webhook on:
    - Signal generated
    - Trade executed
    - Risk circuit breaker triggered
- **Dashboards**
  - Streamlit app for viewing signals, positions, and logs

---

## Safety Controls
- **Circuit Breaker**
  - Halt new trades if daily loss > 3%
- **Kill Switch**
  - Manual flag in config (`auto_trade: false`) to disable execution
- **Sandbox First**
  - All new features tested in paper before live

---

## Deployment Options
- **Local:** Run via `python src/jobs/intraday_scan.py`
- **Cloud:** Deploy with Docker + cron on AWS, GCP, or Azure
- **CI/CD:** GitHub Actions to run lint/tests on push

---

## To-Do
- [ ] Write Dockerfile
- [ ] Add cron/Task Scheduler examples
- [ ] Implement Slack/Discord notifications
- [ ] Automate daily backtest reports
