import os
import pandas as pd

def load_universe() -> set[str]:
    p = "data/universe/sp500.csv"
    if os.path.exists(p):
        df = pd.read_csv(p)
        return set(df["ticker"].astype(str).str.upper().str.replace(".", "-", regex=False))
    # fallback so the rest runs
    return {"AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","BRK-B".replace(".","-")}