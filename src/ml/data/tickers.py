"""
src/ml/data/tickers.py
======================

Phase 0 — *Ticker Universe Loader* 🧩  
Provides a reusable helper function to load a consistent set of stock tickers  
for use across all data ingestion and modeling scripts.

This ensures that your buzz, price, and prediction modules
all reference the same defined universe (e.g., S&P 500 constituents).

Author:
    Ericka James, 2025
"""

import os
import pandas as pd

# ---------------------------------------------------------------------
# Ticker Universe Loader
# ---------------------------------------------------------------------
def load_universe() -> set[str]:
    """Load a universe of stock tickers for analysis.

    This function defines the “universe” of tickers your Quant Bot
    will monitor and model. It first checks for a CSV at:
        `data/universe/sp500.csv`

    The expected CSV format is:
        ticker
        AAPL
        MSFT
        NVDA
        ...

    If that file is missing, a default minimal fallback set is used
    (AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA, BRK-B).

    Returns:
        set[str]: A set of uppercase ticker symbols, with dots replaced
                  by dashes for compatibility (e.g., BRK.B → BRK-B).

    Example:
        >>> from src.ml.data.tickers import load_universe
        >>> load_universe()
        {'AAPL', 'MSFT', 'NVDA', 'BRK-B', ...}
    """
    p = "data/universe/sp500.csv"

    # If a CSV file of tickers exists, load and clean it
    if os.path.exists(p):
        df = pd.read_csv(p)
        return set(
            df["ticker"]
            .astype(str)
            .str.upper()
            .str.replace(".", "-", regex=False)
        )

    # -----------------------------------------------------------------
    # Fallback: minimal set for quick testing
    # -----------------------------------------------------------------
    return {
        "AAPL",   # Apple
        "MSFT",   # Microsoft
        "NVDA",   # Nvidia
        "AMZN",   # Amazon
        "GOOGL",  # Alphabet Class A
        "META",   # Meta Platforms
        "TSLA",   # Tesla
        "BRK-B",  # Berkshire Hathaway Class B
    }
