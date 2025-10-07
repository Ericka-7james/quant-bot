# ui/app.py
import os, glob
import pandas as pd
import streamlit as st
import plotly.express as px
import yfinance as yf

st.set_page_config(page_title="Quant Bot • Buzz Dashboard", layout="wide")

st.title("🧠 Quant Bot — Phase 1: Buzz & Market Peek")

# ---- Load buzz files ---------------------------------------------------------
paths = sorted(glob.glob("data/buzz/*.csv"))
if not paths:
    st.warning("No buzz files found.\nRun: `python -m src.ml.data.ingest_buzz --date YYYY-MM-DD`")
    st.stop()

# Let user pick a date file
file_map = {os.path.basename(p).replace(".csv", ""): p for p in paths}
date_choice = st.selectbox("Pick a buzz file (date)", list(file_map.keys())[::-1])  # latest first
buzz = pd.read_csv(file_map[date_choice])

# Guard for empty file schema
expected_cols = {"date","ticker","mentions","avg_sentiment"}
if not expected_cols.issubset(set(map(str.lower, buzz.columns))):
    st.error("Buzz file missing expected columns. Re-run ingest_buzz.py.")
    st.stop()

# Normalize column names just in case
buzz.columns = [c.lower() for c in buzz.columns]

st.caption(f"Loaded: **{os.path.basename(file_map[date_choice])}** • Rows: {len(buzz)}")

# ---- Summary charts ----------------------------------------------------------
top_n = st.slider("Show top N by mentions", min_value=5, max_value=30, value=15, step=1)

agg = (
    buzz.groupby("ticker", as_index=False)
        .agg(mentions=("mentions","sum"),
             avg_sentiment=("avg_sentiment","mean"))
        .sort_values("mentions", ascending=False)
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Mentioned Tickers")
    fig1 = px.bar(agg.head(top_n), x="ticker", y="mentions")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Average Sentiment (Top by Mentions)")
    fig2 = px.bar(agg.head(top_n), x="ticker", y="avg_sentiment")
    st.plotly_chart(fig2, use_container_width=True)

# ---- Detail table ------------------------------------------------------------
with st.expander("View raw buzz rows"):
    st.dataframe(buzz.sort_values(["mentions","avg_sentiment"], ascending=[False, False]), use_container_width=True)

# ---- Quick price peek --------------------------------------------------------
st.markdown("---")
st.subheader("📈 Quick Price Peek (yfinance)")

ticker = st.text_input(
    "Ticker (use same formatting as buzz file, e.g., AAPL, MSFT, BRK-B)",
    "NVDA"
).strip().upper()
period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=1)

yf_symbol = ticker.replace("-", ".")
try:
    df = yf.download(
        yf_symbol, period=period, interval="1d",
        auto_adjust=True, progress=False, threads=False
    )
    if df is not None and not df.empty:
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]  # flatten
        df = df.reset_index(names="Date")
        if "Close" in df.columns and "Date" in df.columns:
            fig3 = px.line(df, x="Date", y="Close", title=f"{ticker} — Close ({period})")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("Unexpected columns in price data.")
    else:
        st.info("No price data returned for that ticker/period.")
except Exception as e:
    st.error(f"Price fetch error: {e}")