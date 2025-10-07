from __future__ import annotations
import os, re
from typing import List
import pandas as pd
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .tickers import load_universe

FEEDS = [
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "https://www.investopedia.com/feedbuilder/feed/GetFeed?feedName=news",
    "https://finance.yahoo.com/news/rssindex",
    "https://www.reddit.com/r/stocks/.rss",
    "https://www.reddit.com/r/investing/.rss",
    "https://www.reddit.com/r/wallstreetbets/.rss",
]

TICKER_RE = re.compile(r'(?<![A-Z0-9])\$?([A-Z]{1,5})(?![A-Z])')
COMMON_FALSES = {"A","I","AM","ALL","FOR","EVER","DD","YOLO","CEO","CFO","OPEN","AI","USA","IPO","EPS","HOME"}

def _date(run_date: str | None) -> str:
    if run_date:
        return pd.to_datetime(run_date).strftime("%Y-%m-%d")
    return pd.Timestamp.now(tz="America/New_York").strftime("%Y-%m-%d")

def _clean(s: str | None) -> str:
    if not s: return ""
    return re.sub(r"\s+"," ",s).strip()

def _candidates(text: str) -> List[str]:
    return [m.group(1) for m in TICKER_RE.finditer(text.upper()) if m.group(1) not in COMMON_FALSES]

def run(run_date: str | None = None) -> str:
    out_date = _date(run_date)
    os.makedirs("data/buzz", exist_ok=True)
    uni = load_universe()
    analyzer = SentimentIntensityAnalyzer()
    rows = []

    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception:
            continue
        for e in feed.get("entries", []):
            title = _clean(e.get("title",""))
            summary = _clean(e.get("summary","") or e.get("description",""))
            text = f"{title}. {summary}".strip()
            if not text: continue
            sent = float(analyzer.polarity_scores(text).get("compound", 0.0))
            found = {t for t in _candidates(text) if t in uni}
            for t in found:
                rows.append({"date": out_date, "ticker": t, "sentiment": sent, "source": url, "title": title[:200]})

    out_path = f"data/buzz/{out_date}.csv"
    if not rows:
        pd.DataFrame(columns=["date","ticker","mentions","avg_sentiment","sources"]).to_csv(out_path, index=False)
        return out_path

    df = pd.DataFrame(rows)
    agg = (df.groupby(["date","ticker"])
             .agg(mentions=("ticker","count"),
                  avg_sentiment=("sentiment","mean"),
                  sources=("source", lambda s: ";".join(sorted(set(s)))))
             .reset_index())
    agg.to_csv(out_path, index=False)
    return out_path

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    args = ap.parse_args()
    p = run(args.date)
    print("wrote", p)
