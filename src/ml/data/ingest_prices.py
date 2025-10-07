# src/ml/data/ingest_prices.py
from __future__ import annotations
import os
from typing import Dict, List
import pandas as pd
import numpy as np
import yfinance as yf

from .tickers import load_universe

# ---------- helpers ----------

def _yf_symbol(t: str) -> str:
    return t  # yfinance expects BRK-B, BF-B, etc.

def _from_yf_symbol(s: str) -> str:
    return s

def _rsi(series: pd.Series, window: int = 14) -> pd.Series:
    # Wilder's RSI
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def _compute_features(df: pd.DataFrame) -> pd.DataFrame:
    # df: date, ticker, open, high, low, close, volume
    df = df.sort_values(["ticker", "date"]).copy()

    # simple returns
    df["r1"]  = df.groupby("ticker")["close"].pct_change(1,  fill_method=None)
    df["r5"]  = df.groupby("ticker")["close"].pct_change(5,  fill_method=None)
    df["r20"] = df.groupby("ticker")["close"].pct_change(20, fill_method=None)

    # volatility (rolling std of daily returns)
    df["vol20"] = df.groupby("ticker")["r1"].rolling(20).std().reset_index(level=0, drop=True)

    # RSI(14)
    df["rsi14"] = df.groupby("ticker")["close"].apply(_rsi).reset_index(level=0, drop=True)

    # 52-week (252 trading days) high/low and distances
    roll_max = df.groupby("ticker")["close"].rolling(252, min_periods=20).max().reset_index(level=0, drop=True)
    roll_min = df.groupby("ticker")["close"].rolling(252, min_periods=20).min().reset_index(level=0, drop=True)
    df["hi52d"] = roll_max
    df["lo52d"] = roll_min
    df["hi52d_dist"] = df["close"] / df["hi52d"] - 1.0
    df["lo52d_dist"] = df["close"] / df["lo52d"] - 1.0

    return df

def _flatten_prices(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize yfinance output to long format:
    columns → date, ticker, open, high, low, close, volume
    """
    if raw is None or raw.empty:
        return pd.DataFrame(columns=["date","ticker","open","high","low","close","volume"])

    # If multiple tickers, columns are MultiIndex like ('Close','AAPL')
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [c[0] if isinstance(c, tuple) else c for c in raw.columns]  # level 0 only
        # Move ticker from index level to column
        # After .stack(level=1) the first level is fields (Open/High/Low/Close/Volume)
        # but we just flattened to level0, so we need a different approach:
        # yfinance with group_by='ticker' returns columns grouped per ticker. Instead,
        # call stack on axis=1 by chunks: detect tickers via intersection of columns
        # Simpler: call yfinance with group_by='column' (default) and then reshape:
        pass

    # If single ticker → simple columns
    # Ensure canonical column names
    cols = {c.lower(): c for c in raw.columns}
    # yfinance returns 'Open','High','Low','Close','Adj Close','Volume'
    df = raw.reset_index()
    # Prefer adjusted Close (auto_adjust=True already adjusts Close)
    out = pd.DataFrame({
        "date": df.iloc[:, 0],  # Date
        "open": df.get("Open", df.get("open")),
        "high": df.get("High", df.get("high")),
        "low": df.get("Low", df.get("low")),
        "close": df.get("Close", df.get("close")),
        "volume": df.get("Volume", df.get("volume"))
    })
    # We'll add ticker later upstream for single downloads
    return out

# ---------- main run ----------

def run(period: str = "2y", chunk_size: int = 40, out_path: str = "data/market/daily.parquet") -> str:
    """
    Download daily OHLCV for your universe using yfinance, compute features,
    and save a single parquet at data/market/daily.parquet.
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    uni = sorted(load_universe())
    if not uni:
        raise RuntimeError("Universe is empty. Put tickers in data/universe/sp500.csv (column 'ticker').")

    # yfinance prefers dot-class tickers
    yf_symbols = [_yf_symbol(t) for t in uni]

    frames: List[pd.DataFrame] = []

    # Batch to be gentle with network / avoid failures
    for i in range(0, len(yf_symbols), chunk_size):
        batch = yf_symbols[i:i+chunk_size]
        try:
            raw = yf.download(
                tickers=batch,
                period=period,
                interval="1d",
                auto_adjust=True,
                group_by="ticker",   # multiindex columns per ticker
                progress=False,
                threads=True,
            )
        except Exception:
            continue

        if raw is None or raw.empty:
            continue

        if not isinstance(raw.columns, pd.MultiIndex):
            # This happens when there's only ONE ticker in batch
            # Add a fake top level with that ticker symbol
            # Identify the only symbol we requested
            sym = batch[0] if batch else "UNKNOWN"
            raw.columns = pd.MultiIndex.from_product([[sym], raw.columns])

        # Normalize to long format: date, ticker, open, high, low, close, volume
        raw = raw.sort_index()
        long = (
    raw.stack(level=0, future_stack=True)  # adopt new pandas behavior, no warning
       .reset_index()
       .rename(columns={"level_1": "ticker"})
       )

        long.columns = [c.lower() if isinstance(c, str) else c for c in long.columns]
        # Keep essentials
        keep = long[["date","ticker","open","high","low","close","volume"]].copy()

        # Convert back to internal ticker form (BRK.B -> BRK-B)
        keep["ticker"] = keep["ticker"].apply(_from_yf_symbol)

        frames.append(keep)

    if not frames:
        # Write empty parquet for pipeline predictability
        empty = pd.DataFrame(columns=["date","ticker","open","high","low","close","volume","r1","r5","r20","rsi14","vol20","hi52d","lo52d","hi52d_dist","lo52d_dist"])
        empty.to_parquet(out_path, index=False)
        return out_path

    prices = pd.concat(frames, ignore_index=True)
    # Ensure types
    prices["date"] = pd.to_datetime(prices["date"])
    for c in ["open","high","low","close","volume"]:
        prices[c] = pd.to_numeric(prices[c], errors="coerce")

    # Compute indicators/features
    feat = _compute_features(prices)

    # Deduplicate just in case
    feat = feat.drop_duplicates(subset=["date","ticker"]).sort_values(["ticker","date"])

    # Save parquet
    feat.to_parquet(out_path, index=False)
    return out_path

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default="2y", help="yfinance period (e.g., 6mo, 1y, 2y, 5y)")
    ap.add_argument("--chunk-size", type=int, default=40)
    ap.add_argument("--out", default="data/market/daily.parquet")
    args = ap.parse_args()
    p = run(period=args.period, chunk_size=args.chunk_size, out_path=args.out)
    print("wrote", p)
