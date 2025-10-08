"""
src/ml/models/train_nowcast.py
==============================

Phase 3 — *Baseline Nowcast (Next-Day Up/Down)* 🔮
Trains quick baseline classifiers (Logistic Regression, Random Forest) to predict
whether a stock will rise on the next trading day, using:
- Market features from `data/market/daily.parquet` (Phase 2)
- Optional buzz features merged from `data/buzz/*.csv` (Phase 1)

Key outputs (printed to stdout):
    - Holdout accuracy vs. 0.500 baseline
    - Decile spread (top − bottom deciles of predicted ↑ probability) in:
        * Daily return spread
        * Annualized (toy alpha)

Usage:
    python -m src.ml.models.train_nowcast

Notes:
    - This is a simple baseline for learning and iteration — not investment advice.
    - Leakage guard: features at t predict return sign at t+1 (via shift).
"""

from __future__ import annotations
import glob
import os
from typing import Tuple, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def _load_market(path: str = "data/market/daily.parquet") -> pd.DataFrame:
    """Load market features (Phase 2 output) and create next-day target.

    Args:
        path: Parquet path for market features built by Phase 2.

    Returns:
        pd.DataFrame: Sorted by (ticker, date) with:
            - columns like r1, r5, r20, rsi14, vol20, hi52d_dist, lo52d_dist
            - next_ret: next-day close-to-close return
            - y: binary target (1 if next_ret > 0 else 0)

    Raises:
        FileNotFoundError: If the parquet is missing.

    Leakage note:
        We compute next_ret using shift(-1) so that features at date t predict
        returns at t+1; we later drop rows with missing y (last date per ticker).
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}. Run ingest_prices first.")
    df = pd.read_parquet(path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["ticker", "date"])

    # next-day return + binary target
    df["next_ret"] = df.groupby("ticker")["close"].pct_change().shift(-1)
    df["y"] = (df["next_ret"] > 0).astype(int)
    return df


def _load_buzz(pattern: str = "data/buzz/*.csv") -> Optional[pd.DataFrame]:
    """Load and aggregate buzz features (Phase 1 outputs).

    Args:
        pattern: Glob to match daily buzz CSVs.

    Returns:
        pd.DataFrame | None: Aggregated buzz with columns:
            date, ticker, mentions, avg_sentiment
        Returns None if no buzz files found or load fails.
    """
    paths = sorted(glob.glob(pattern))
    if not paths:
        return None

    dfs = []
    for p in paths:
        try:
            d = pd.read_csv(p)
            d["date"] = pd.to_datetime(d["date"])
            dfs.append(d[["date", "ticker", "mentions", "avg_sentiment"]])
        except Exception:
            # Skip unreadable files to keep pipeline robust
            continue

    if not dfs:
        return None

    buzz = pd.concat(dfs, ignore_index=True)
    buzz = (
        buzz.groupby(["date", "ticker"])
            .agg(
                mentions=("mentions", "sum"),
                avg_sentiment=("avg_sentiment", "mean"),
            )
            .reset_index()
    )
    return buzz


def _time_split(df: pd.DataFrame, test_days: int = 60) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split dataframe into train/test by time (no shuffling).

    Args:
        df: Full dataframe with a `date` column.
        test_days: Number of business days to reserve for holdout.

    Returns:
        (train_df, test_df): Split by cutoff = max(date) - test_days (BDay).
    """
    last = df["date"].max()
    cutoff = last - pd.tseries.offsets.BDay(test_days)
    tr = df[df["date"] <= cutoff].copy()
    te = df[df["date"] > cutoff].copy()
    return tr, te


def _decile_spread(probs: pd.Series, future_rets: pd.Series) -> Tuple[float, float]:
    """Compute top-minus-bottom decile return spread as toy alpha.

    Args:
        probs: Predicted probabilities of next-day up move (for holdout rows).
        future_rets: Realized next-day returns aligned with probs.

    Returns:
        (daily_spread, annualized_spread):
            daily_spread = mean(next_ret in top decile) - mean(next_ret in bottom decile)
            annualized_spread = (1 + daily_spread) ** 252 - 1
    """
    df = pd.DataFrame({"p": probs, "r": future_rets}).dropna()
    if df.empty:
        return 0.0, 0.0

    # Assign deciles by predicted probability
    df["decile"] = pd.qcut(df["p"], 10, labels=False, duplicates="drop")
    top = df[df["decile"] == df["decile"].max()]["r"].mean()
    bot = df[df["decile"] == df["decile"].min()]["r"].mean()

    daily = float(top - bot)
    annual = (1 + daily) ** 252 - 1
    return daily, annual


def train_baseline(
    market_path: str = "data/market/daily.parquet",
    use_buzz: bool = True,
    test_days: int = 60,
    random_state: int = 42,
) -> None:
    """Train baseline next-day classifiers and print evaluation metrics.

    Pipeline:
        1) Load market features and (optionally) buzz features.
        2) Merge on (date, ticker); fill missing buzz with zeros.
        3) Create next-day target (already in _load_market).
        4) Time-aware split: last `test_days` as holdout.
        5) Train Logistic Regression and Random Forest.
        6) Print holdout accuracy and decile spread metrics.
        7) (Optional extension) Save models for later scoring.

    Args:
        market_path: Path to Phase 2 parquet (features).
        use_buzz: Whether to merge buzz features (mentions, avg_sentiment).
        test_days: Business days reserved for holdout evaluation.
        random_state: Random seed for reproducibility.

    Returns:
        None. Prints metrics to stdout.
    """
    # 1) Load data
    mkt = _load_market(market_path)
    buzz = _load_buzz() if use_buzz else None

    # 2) Merge & fill buzz if missing
    if buzz is not None:
        df = mkt.merge(buzz, on=["date", "ticker"], how="left")
    else:
        df = mkt.copy()
        df["mentions"] = 0.0
        df["avg_sentiment"] = 0.0

    # Remove last row per ticker where y is NaN (no t+1 yet)
    df = df.dropna(subset=["y"])

    # 3) Feature set (order doesn’t matter)
    feature_cols = [
        c
        for c in [
            "r1", "r5", "r20",
            "vol20", "rsi14",
            "hi52d_dist", "lo52d_dist",
            "mentions", "avg_sentiment",
        ]
        if c in df.columns
    ]
    if not feature_cols:
        raise ValueError("No feature columns found. Did Phase 2 create features?")

    # 4) Time split
    train_df, test_df = _time_split(df, test_days=test_days)
    if train_df.empty or test_df.empty:
        raise ValueError("Not enough data after time split. Try a smaller test_days.")

    X_tr, y_tr = train_df[feature_cols].fillna(0), train_df["y"].astype(int)
    X_te, y_te = test_df[feature_cols].fillna(0), test_df["y"].astype(int)

    # 5) Models
    lr = LogisticRegression(max_iter=1000)
    rf = RandomForestClassifier(n_estimators=300, random_state=random_state, n_jobs=-1)

    lr.fit(X_tr, y_tr)
    rf.fit(X_tr, y_tr)

    # 6) Evaluate & print
    for name, model in [("LogReg", lr), ("RandForest", rf)]:
        prob = model.predict_proba(X_te)[:, 1]
        pred = (prob >= 0.5).astype(int)
        acc = accuracy_score(y_te, pred)
        daily, annual = _decile_spread(prob, test_df["next_ret"])

        print(f"\n== {name} ==")
        print(f"Holdout accuracy: {acc:.3f} (baseline 0.500)")
        print(f"Top-Bottom decile daily spread: {daily:.4%}")
        print(f"Top-Bottom decile annualized (toy): {annual:.2%}")


if __name__ == "__main__":
    # Keeping CLI simple & stable for now.
    # If you want flags, easy upgrade: argparse for --no-buzz, --test-days, etc.
    train_baseline()
