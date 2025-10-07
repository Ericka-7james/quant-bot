# src/ml/models/train_nowcast.py
from __future__ import annotations
import glob, os
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def _load_market(path="data/market/daily.parquet") -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}. Run ingest_prices first.")
    df = pd.read_parquet(path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["ticker","date"])
    # next-day return + binary target
    df["next_ret"] = df.groupby("ticker")["close"].pct_change().shift(-1)
    df["y"] = (df["next_ret"] > 0).astype(int)
    return df

def _load_buzz(pattern="data/buzz/*.csv") -> pd.DataFrame | None:
    paths = sorted(glob.glob(pattern))
    if not paths: return None
    dfs = []
    for p in paths:
        try:
            d = pd.read_csv(p)
            d["date"] = pd.to_datetime(d["date"])
            dfs.append(d[["date","ticker","mentions","avg_sentiment"]])
        except Exception:
            continue
    if not dfs: return None
    buzz = pd.concat(dfs, ignore_index=True)
    buzz = (buzz.groupby(["date","ticker"])
                 .agg(mentions=("mentions","sum"),
                      avg_sentiment=("avg_sentiment","mean"))
                 .reset_index())
    return buzz

def _time_split(df: pd.DataFrame, test_days: int = 60):
    last = df["date"].max()
    cutoff = last - pd.tseries.offsets.BDay(test_days)
    tr = df[df["date"] <= cutoff].copy()
    te = df[df["date"] >  cutoff].copy()
    return tr, te

def _decile_spread(probs: pd.Series, future_rets: pd.Series) -> tuple[float,float]:
    df = pd.DataFrame({"p": probs, "r": future_rets}).dropna()
    if df.empty: return 0.0, 0.0
    df["decile"] = pd.qcut(df["p"], 10, labels=False, duplicates="drop")
    top = df[df["decile"] == df["decile"].max()]["r"].mean()
    bot = df[df["decile"] == df["decile"].min()]["r"].mean()
    daily = float(top - bot)
    annual = (1 + daily) ** 252 - 1
    return daily, annual

def train_baseline(
    market_path="data/market/daily.parquet",
    use_buzz=True,
    test_days=60,
    random_state=42
):
    mkt = _load_market(market_path)
    buzz = _load_buzz() if use_buzz else None
    if buzz is not None:
        df = mkt.merge(buzz, on=["date","ticker"], how="left")
    else:
        df = mkt.copy()
        df["mentions"] = 0.0
        df["avg_sentiment"] = 0.0

    df = df.dropna(subset=["y"])  # drop last day per ticker

    feature_cols = [c for c in [
        "r1","r5","r20","vol20","rsi14","hi52d_dist","lo52d_dist",
        "mentions","avg_sentiment"
    ] if c in df.columns]

    train_df, test_df = _time_split(df, test_days=test_days)
    X_tr, y_tr = train_df[feature_cols].fillna(0), train_df["y"].astype(int)
    X_te, y_te = test_df[feature_cols].fillna(0), test_df["y"].astype(int)

    # Models
    lr = LogisticRegression(max_iter=1000)
    rf = RandomForestClassifier(n_estimators=300, random_state=random_state, n_jobs=-1)

    lr.fit(X_tr, y_tr)
    rf.fit(X_tr, y_tr)

    for name, model in [("LogReg", lr), ("RandForest", rf)]:
        prob = model.predict_proba(X_te)[:,1]
        pred = (prob >= 0.5).astype(int)
        acc  = accuracy_score(y_te, pred)
        daily, annual = _decile_spread(prob, test_df["next_ret"])
        print(f"\n== {name} ==")
        print(f"Holdout accuracy: {acc:.3f} (baseline 0.500)")
        print(f"Top-Bottom decile daily spread: {daily:.4%}")
        print(f"Top-Bottom decile annualized (toy): {annual:.2%}")

if __name__ == "__main__":
    train_baseline()
