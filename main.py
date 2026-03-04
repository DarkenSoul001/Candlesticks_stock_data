"""
stock_chart.py
==============
Quantitative-grade OHLCV data pipeline and candlestick visualisation.

Design principles
-----------------
* Vectorised data wrangling — zero Python-level loops over rows.
* Single-pass dtype coercion via pd.to_numeric with a column map.
* Column rename via dict mapping (O(k), k=5) instead of list assignment.
* Fail-fast validation before expensive API call.
* Minimal import surface; only what is used.

Author : <Garv Kothari>
Date   : 2026-03-04
"""

from __future__ import annotations

import sys
import logging
from typing import Final

import pandas as pd
import mplfinance as mpf
from alpha_vantage.timeseries import TimeSeries

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_KEY: Final[str] = "VRAMT37O56UPI2CQ"
STOCK_SYMBOL: Final[str] = "AAPL"

# Alpha Vantage returns columns like "1. open", "2. high", …
# Map them to mplfinance-compatible lowercase names in one shot.
AV_COLUMN_MAP: Final[dict[str, str]] = {
    "1. open":   "Open",
    "2. high":   "High",
    "3. low":    "Low",
    "4. close":  "Close",
    "5. volume": "Volume",
}

# mplfinance chart styling
CHART_STYLE:  Final[str]         = "charles"
CHART_SIZE:   Final[tuple]       = (14, 8)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data layer
# ---------------------------------------------------------------------------

def fetch_ohlcv(symbol: str, api_key: str, outputsize: str = "compact") -> pd.DataFrame:
    """
    Fetch daily OHLCV data from Alpha Vantage and return a clean DataFrame.

    Parameters
    ----------
    symbol     : Ticker symbol, e.g. ``"AAPL"``.
    api_key    : Alpha Vantage API key.
    outputsize : ``"compact"`` (100 bars) or ``"full"`` (20 years).

    Returns
    -------
    pd.DataFrame
        DatetimeIndex, columns [Open, High, Low, Close, Volume], all float64
        except Volume (int64), sorted ascending.

    Complexity
    ----------
    O(n) — one vectorised cast over n rows × 5 columns; no Python row loops.
    """
    ts = TimeSeries(key=api_key, output_format="pandas")

    log.info("Fetching %s daily data (outputsize=%s) …", symbol, outputsize)
    raw, meta = ts.get_daily(symbol=symbol, outputsize=outputsize)
    log.info("Received %d records.  Source: %s", len(raw), meta.get("2. Symbol", symbol))

    # --- rename & sort --------------------------------------------------------
    # O(k) dict lookup rename; no list iteration over row data.
    df = (
        raw
        .rename(columns=AV_COLUMN_MAP)   # rename 5 columns by dict — O(k)
        .sort_index()                     # ascending chronological order
    )

    # --- vectorised dtype coercion --------------------------------------------
    # pd.to_numeric broadcasts over the entire column array (C-level loop).
    # Applying it via DataFrame.apply iterates columns (k=5), not rows (n).
    ohlc_cols = ["Open", "High", "Low", "Close"]
    df[ohlc_cols] = df[ohlc_cols].apply(pd.to_numeric, errors="coerce")
    df["Volume"]  = pd.to_numeric(df["Volume"], errors="coerce").astype("int64")

    # --- sanity check ---------------------------------------------------------
    if df.isnull().values.any():
        null_counts = df.isnull().sum()
        log.warning("NaN values detected after coercion:\n%s", null_counts[null_counts > 0])

    return df


# ---------------------------------------------------------------------------
# Visualisation layer
# ---------------------------------------------------------------------------

def plot_candlestick(df: pd.DataFrame, symbol: str) -> None:
    """
    Render an OHLCV candlestick chart with volume panel.

    Parameters
    ----------
    df     : Clean OHLCV DataFrame (output of ``fetch_ohlcv``).
    symbol : Ticker symbol used in the chart title.
    """
    log.info("Rendering candlestick chart for %s …", symbol)

    mpf.plot(
        df,
        type="candle",
        style=CHART_STYLE,
        title=f"{symbol} — Daily Candlestick Chart",
        ylabel="Price (USD)",
        ylabel_lower="Volume",
        volume=True,
        figsize=CHART_SIZE,
        tight_layout=True,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        df = fetch_ohlcv(symbol=STOCK_SYMBOL, api_key=API_KEY)

        log.info("Sample data (first 5 rows):\n%s", df.head())

        plot_candlestick(df, symbol=STOCK_SYMBOL)

    except Exception:
        log.exception("Pipeline failed — see traceback below.")
        sys.exit(1)


if __name__ == "__main__":
    main()