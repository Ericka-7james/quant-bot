"""
src/ml/data/ingest_buzz.py
==========================

Phase 1 — *The Ears* 📰  
Collects daily “buzz” data from financial news and Reddit feeds,
detects mentioned tickers, evaluates sentiment using VADER, and
aggregates the results into `data/buzz/YYYY-MM-DD.csv`.

Output CSV schema:
    date, ticker, mentions, avg_sentiment, sources

Usage:
    python -m src.ml.data.ingest_buzz --date 2025-10-05

Author:
    Ericka James, 2025
"""

from __future__ import annotations
import os, re
from typing import List
import pandas as pd
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .tickers import load_universe

# ---------------------------------------------------------------------
# Data sources to monitor (RSS + Reddit)
# ---------------------------------------------------------------------
FEEDS = [
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",           # WSJ Markets
    "https://www.investopedia.com/feedbuilder/feed/GetFeed?feedName=news",
    "https://finance.yahoo.com/news/rssindex",
    "https://www.reddit.com/r/stocks/.rss",
    "https://www.reddit.com/r/investing/.rss",
    "https://www.reddit.com/r/wallstreetbets/.rss",
]

# ---------------------------------------------------------------------
# Regex and constants for ticker detection
# ---------------------------------------------------------------------
# Matches $AAPL, TSLA, etc. — up to 5 letters.
TICKER_RE = re.compile(r'(?<![A-Z0-9])\$?([A-Z]{1,5})(?![A-Z])')

# Excluded “false positives” (common words or abbreviations)
COMMON_FALSES = {
    "A","I","AM","ALL","FOR","EVER","DD","YOLO","CEO","CFO",
    "OPEN","AI","USA","IPO","EPS","HOME"
}

# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------
def _date(run_date: str | None) -> str:
    """Return a formatted run date string (YYYY-MM-DD).

    Args:
        run_date (str | None): Optional explicit date (any parseable format).
            If None, uses current date in US/Eastern timezone.

    Returns:
        str: Formatted date string, e.g. "2025-10-07".
    """
    if run_date:
        return pd.to_datetime(run_date).strftime("%Y-%m-%d")
    return pd.Timestamp.now(tz="America/New_York").strftime("%Y-%m-%d")


def _clean(s: str | None) -> str:
    """Normalize whitespace and strip text safely.

    Args:
        s (str | None): Input string or None.

    Returns:
        str: Cleaned text with collapsed spaces, or empty string if None.
    """
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def _candidates(text: str) -> List[str]:
    """Extract valid ticker candidates from text.

    Args:
        text (str): Raw article or post content.

    Returns:
        List[str]: Unique uppercase tickers found that are not in COMMON_FALSES.
    """
    return [
        m.group(1)
        for m in TICKER_RE.finditer(text.upper())
        if m.group(1) not in COMMON_FALSES
    ]

# ---------------------------------------------------------------------
# Main ingestion pipeline
# ---------------------------------------------------------------------
def run(run_date: str | None = None) -> str:
    """Run the daily buzz collection process.

    Steps:
        1. Resolve output date and universe.
        2. Parse each RSS/Reddit feed.
        3. Extract candidate tickers and sentiment per entry.
        4. Aggregate by (date, ticker) to compute:
            - mentions
            - avg_sentiment
            - concatenated source list
        5. Write CSV to `data/buzz/YYYY-MM-DD.csv`.

    Args:
        run_date (str | None): Optional override date (defaults to today).

    Returns:
        str: Path to the written CSV file.
    """
    out_date = _date(run_date)
    os.makedirs("data/buzz", exist_ok=True)

    # Load valid ticker universe (e.g., S&P 500)
    uni = load_universe()

    # Initialize VADER sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    rows = []  # list of raw mention rows before aggregation

    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception:
            continue  # Skip feed on network/parse failure

        for entry in feed.get("entries", []):
            # Extract and clean title + summary text
            title = _clean(entry.get("title", ""))
            summary = _clean(entry.get("summary", "") or entry.get("description", ""))
            text = f"{title}. {summary}".strip()
            if not text:
                continue

            # Compute compound sentiment score
            sent = float(analyzer.polarity_scores(text).get("compound", 0.0))

            # Find tickers mentioned that exist in our universe
            found = {t for t in _candidates(text) if t in uni}

            # Record each match
            for t in found:
                rows.append({
                    "date": out_date,
                    "ticker": t,
                    "sentiment": sent,
                    "source": url,
                    "title": title[:200],
                })

    # -----------------------------------------------------------------
    # Aggregate results and write output
    # -----------------------------------------------------------------
    out_path = f"data/buzz/{out_date}.csv"

    if not rows:
        # Write empty file with schema headers if nothing found
        pd.DataFrame(columns=["date","ticker","mentions","avg_sentiment","sources"]).to_csv(out_path, index=False)
        return out_path

    df = pd.DataFrame(rows)
    agg = (
        df.groupby(["date", "ticker"])
          .agg(
              mentions=("ticker", "count"),
              avg_sentiment=("sentiment", "mean"),
              sources=("source", lambda s: ";".join(sorted(set(s))))
          )
          .reset_index()
    )

    agg.to_csv(out_path, index=False)
    return out_path


# ---------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Fetch and aggregate daily stock buzz sentiment.")
    ap.add_argument("--date", default=None, help="Optional run date (YYYY-MM-DD). Defaults to today.")
    args = ap.parse_args()

    path = run(args.date)
    print("wrote", path)
