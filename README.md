# OHLCV Candlestick Chart (Alpha Vantage, mplfinance)

Lightweight pipeline to fetch daily OHLCV data from Alpha Vantage and render a candlestick chart with volume using mplfinance.

---

## Features

- Vectorised data wrangling using pandas; no per-row Python loops.
- Layered design: data fetch, cleaning, and plotting are separate functions.
- Structured logging with timestamps and log levels (INFO / ERROR).
- Fail-fast validation: exits on missing data or NaNs in price or volume columns.
- Implements vectorised transformations to avoid Python-level row iteration, suitable for research workflows on larger universes.

---

## Requirements

| Package | Version |
|---|---|
| Python | >= 3.9 |
| pandas | >= 1.5 |
| mplfinance | >= 0.12 |
| alpha_vantage | >= 2.3 |

```bash
pip install -r requirements.txt
```

**requirements.txt**

```
pandas>=1.5
mplfinance>=0.12
alpha_vantage>=2.3
```

---

## API Key Setup

Alpha Vantage provides daily OHLCV time series suitable for backtesting and charting; this project wraps the API into a minimal, reproducible interface.

Set an environment variable before running:

```bash
export ALPHA_VANTAGE_KEY="your_key_here"
```

The script reads the key from `os.environ['ALPHA_VANTAGE_KEY']`. API keys must be supplied via environment variables; do not store credentials in source code or version control.

A free key is available at [alphavantage.co](https://www.alphavantage.co/support/#api-key).

---

## Usage

**CLI**

```bash
python stock_chart.py --symbol TSLA --outputsize compact
```

**Python import**

```python
from stock_chart import fetch_ohlcv, plot_candlestick

df = fetch_ohlcv("AAPL")
plot_candlestick(df, title="AAPL — Daily Candlestick")
```

`outputsize` accepts `"compact"` (last 100 trading days) or `"full"` (up to 20 years).

---

## Project Structure

```
.
├── stock_chart.py   # Pipeline: data fetch, cleaning, and chart rendering
├── requirements.txt # Pinned dependencies
└── README.md
```

---

## Design Notes

- **Data** — `fetch_ohlcv` handles the Alpha Vantage API call, column rename via dict map, chronological sort, and vectorised numeric coercion in a single pass.
- **Visualisation** — `plot_candlestick` configures mplfinance and outputs the candlestick chart with a volume sub-plot.
- **Entry point** — `main()` orchestrates argument parsing, pipeline execution, and process exit codes.

---

## License

MIT license. See LICENSE for details.
