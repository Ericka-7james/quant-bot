"""
ui/app.py — Streamlit dashboard for Quant Bot
=============================================

Displays three core views:

1. Buzz & Market (Phase 1 + Phase 2)
   • Shows top mentioned tickers and sentiment from news/reddit.
   • Provides quick price chart via yfinance.

2. Predictions (Phase 3 baseline)
   • Trains quick Logistic Regression and Random Forest models
     using features from `data/market/daily.parquet` and buzz data.
   • Reports holdout accuracy, decile spread (toy alpha), and
     predicted probabilities of next-day upward moves.

Run:
    streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0

Author:
    Ericka James, 2025
"""

import os
import glob
import pandas as pd
import streamlit as st
import plotly.express as px
import yfinance as yf
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# ---------------------------------------------------------------------
# Streamlit page setup
# ---------------------------------------------------------------------
st.set_page_config(page_title="Quant Bot • Buzz Dashboard", layout="wide")
st.title("🧠 Quant Bot — Buzz • Market • Predictions")

# ---------------------------------------------------------------------
# Load Buzz data
# ---------------------------------------------------------------------
paths = sorted(glob.glob("data/buzz/*.csv"))
if not paths:
    st.warning("No buzz files found.\nRun: `python -m src.ml.data.ingest_buzz --date YYYY-MM-DD`")
    st.stop()

# Let user pick a buzz file (latest first)
file_map = {os.path.basename(p).replace(".csv", ""): p for p in paths}
date_choice = st.selectbox("Pick a buzz file (date)", list(file_map.keys())[::-1])
buzz = pd.read_csv(file_map[date_choice])
buzz.columns = [c.lower() for c in buzz.columns]

expected_cols = {"date", "ticker", "mentions", "avg_sentiment"}
if not expected_cols.issubset(set(buzz.columns)):
    st.error("Buzz file missing expected columns. Re-run ingest_buzz.py.")
    st.stop()

buzz["date"] = pd.to_datetime(buzz["date"])
st.caption(f"Loaded: **{os.path.basename(file_map[date_choice])}** • Rows: {len(buzz)}")


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------
def fetch_price_chart(ticker: str, period: str = "3mo") -> None:
    """Download and plot recent prices for a given ticker.

    Args:
        ticker (str): Stock ticker (e.g. 'AAPL', 'MSFT', 'BRK-B').
        period (str): yfinance period string ('1mo', '3mo', '6mo', '1y').

    Notes:
        Automatically flattens MultiIndex columns returned by yfinance.
    """
    yf_symbol = ticker.replace("-", ".")
    try:
        df = yf.download(
            yf_symbol, period=period, interval="1d",
            auto_adjust=True, progress=False, threads=False
        )
        if df is None or df.empty:
            st.info("No price data returned for that ticker/period.")
            return

        # Flatten possible MultiIndex columns
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df = df.reset_index(names="Date")

        if "Close" not in df.columns or "Date" not in df.columns:
            st.warning("Unexpected columns in price data.")
            return

        fig = px.line(df, x="Date", y="Close", title=f"{ticker} — Close ({period})")
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Price fetch error: {e}")


# ---------------------------------------------------------------------
# Tabs: 1) Buzz & Market  2) Predictions
# ---------------------------------------------------------------------
tabs = st.tabs(["📰 Buzz & Market", "🔮 Predictions"])


# =====================================================================
# TAB 1 — Buzz & Market
# =====================================================================
with tabs[0]:
    st.header("📰 Buzz & Market Overview")

    # Top N slider
    top_n = st.slider("Show top N by mentions", min_value=5, max_value=30, value=15, step=1)

    # Aggregate mentions and sentiment per ticker
    agg = (
        buzz.groupby("ticker", as_index=False)
            .agg(
                mentions=("mentions", "sum"),
                avg_sentiment=("avg_sentiment", "mean")
            )
            .sort_values("mentions", ascending=False)
    )

    # Two side-by-side plots
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Mentioned Tickers")
        fig1 = px.bar(agg.head(top_n), x="ticker", y="mentions")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Average Sentiment (Top by Mentions)")
        fig2 = px.bar(agg.head(top_n), x="ticker", y="avg_sentiment")
        st.plotly_chart(fig2, use_container_width=True)

    # Expandable raw data view
    with st.expander("View raw buzz rows"):
        st.dataframe(
            buzz.sort_values(["mentions", "avg_sentiment"], ascending=[False, False]),
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("📈 Quick Price Peek (yfinance)")

    ticker = st.text_input(
        "Ticker (use same formatting as buzz file, e.g., AAPL, MSFT, BRK-B)",
        "NVDA"
    ).strip().upper()
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=1)

    # Draw chart
    fetch_price_chart(ticker, period)


# =====================================================================
# TAB 2 — Predictions
# =====================================================================
with tabs[1]:
    st.header("🔮 Baseline Predictions (Phase 3)")

    # Load price + features parquet
    market_path = "data/market/daily.parquet"
    if not os.path.exists(market_path):
        st.warning("Missing `data/market/daily.parquet`.\nRun: `python -m src.ml.data.ingest_prices --period 2y`")
        st.stop()

    market = pd.read_parquet(market_path)
    market["date"] = pd.to_datetime(market["date"])

    # Merge buzz with market features
    df = market.merge(buzz, on=["date", "ticker"], how="left").fillna({"mentions": 0, "avg_sentiment": 0})
    df = df.sort_values(["ticker", "date"]).copy()

    # Create next-day target (1 = up, 0 = down)
    df["next_ret"] = df.groupby("ticker")["close"].pct_change().shift(-1)
    df["y"] = (df["next_ret"] > 0).astype(int)
    df = df.dropna(subset=["y"])

    # Feature set
    feature_cols = [c for c in [
        "r1", "r5", "r20", "vol20", "rsi14",
        "hi52d_dist", "lo52d_dist", "mentions", "avg_sentiment"
    ] if c in df.columns]

    if not feature_cols:
        st.error("No feature columns found. Make sure Phase 2 features exist.")
        st.stop()

    # Split training / testing by date
    test_days = st.slider("Holdout window (business days)", 30, 120, 60, 10)
    last_date = df["date"].max()
    cutoff = last_date - pd.tseries.offsets.BDay(test_days)
    train_df = df[df["date"] <= cutoff].copy()
    test_df = df[df["date"] > cutoff].copy()

    if train_df.empty or test_df.empty:
        st.warning("Not enough data after split. Try a smaller holdout window.")
    else:
        X_tr, y_tr = train_df[feature_cols].fillna(0), train_df["y"].astype(int)
        X_te, y_te = test_df[feature_cols].fillna(0), test_df["y"].astype(int)

        # ------------------------------------------------------------------
        # Train two quick baseline models (Logistic Regression & RF)
        # ------------------------------------------------------------------
        lr = LogisticRegression(max_iter=1000)
        rf = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
        lr.fit(X_tr, y_tr)
        rf.fit(X_tr, y_tr)

        # Evaluate both
        cols = st.columns(3)
        for name, model, col in [("LogReg", lr, cols[0]), ("RandForest", rf, cols[1])]:
            prob = model.predict_proba(X_te)[:, 1]
            pred = (prob >= 0.5).astype(int)
            acc = accuracy_score(y_te, pred)

            # Decile spread (top−bottom return difference)
            tmp = pd.DataFrame({"p": prob, "r": test_df["next_ret"]}).dropna()
            if not tmp.empty:
                tmp["decile"] = pd.qcut(tmp["p"], 10, labels=False, duplicates="drop")
                top = tmp[tmp["decile"] == tmp["decile"].max()]["r"].mean()
                bot = tmp[tmp["decile"] == tmp["decile"].min()]["r"].mean()
                daily = float(top - bot)
                annual = (1 + daily) ** 252 - 1
            else:
                daily = annual = 0.0

            col.metric(f"{name} accuracy", f"{acc:.3f}")
            col.metric(f"{name} decile α (annualized)", f"{annual:.2%}")

        # ------------------------------------------------------------------
        # Predict for the latest date and show ranked table
        # ------------------------------------------------------------------
        latest_date = df["date"].max()
        todays = df[df["date"] == latest_date].copy()

        if not todays.empty:
            probs_lr = lr.predict_proba(todays[feature_cols].fillna(0))[:, 1]
            probs_rf = rf.predict_proba(todays[feature_cols].fillna(0))[:, 1]

            out = todays[["ticker", "mentions", "avg_sentiment", "rsi14", "r1", "r5", "r20"]].copy()
            out["pred_up_lr"] = probs_lr
            out["pred_up_rf"] = probs_rf
            out = out.sort_values("pred_up_rf", ascending=False)

            st.markdown(f"### Predictions for {latest_date.date()}")
            st.dataframe(out.head(25).reset_index(drop=True),
                         use_container_width=True, hide_index=True)
            st.caption("Higher values = greater predicted probability of next-day increase.")
