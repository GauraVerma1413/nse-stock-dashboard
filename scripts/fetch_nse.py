"""
fetch_nse.py
Downloads NSE equity list, fetches fundamentals via yfinance,
saves to data/raw_stocks.json.
"""

import json
import time
import requests
import yfinance as yf
import pandas as pd
from io import StringIO
from pathlib import Path

NSE_EQUITY_LIST_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def fetch_nse_tickers() -> list:
    """Download NSE equity list and return Yahoo Finance tickers (SYMBOL.NS)."""
    print("Fetching NSE ticker list...")
    resp = requests.get(NSE_EQUITY_LIST_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    symbols = df['SYMBOL'].dropna().str.strip().tolist()
    tickers = [f"{s}.NS" for s in symbols]
    print(f"Found {len(tickers)} NSE tickers")
    return tickers


def fetch_stock_fundamentals(ticker: str) -> dict:
    """Fetch fundamentals for a single ticker. Returns None on failure."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if not info or info.get('quoteType') not in ('EQUITY', 'ETF'):
            return None

        # Revenue history (last 5 years)
        revenue_5y = []
        try:
            financials = t.financials
            if financials is not None and not financials.empty and 'Total Revenue' in financials.index:
                revenue_5y = [
                    int(v) for v in
                    financials.loc['Total Revenue'].dropna().sort_index().tail(5).tolist()
                ]
        except Exception:
            pass

        # Volume data
        volume_today = 0
        volume_30d_avg = 0
        try:
            hist_1d = t.history(period='1d')
            if not hist_1d.empty:
                volume_today = int(hist_1d['Volume'].iloc[-1])
            hist_30d = t.history(period='30d')
            if not hist_30d.empty:
                volume_30d_avg = int(hist_30d['Volume'].mean())
        except Exception:
            pass

        return {
            "ticker": ticker,
            "name": info.get('longName') or info.get('shortName') or ticker,
            "sector": info.get('sector') or info.get('industry') or 'Other',
            "market_cap_cr": round((info.get('marketCap') or 0) / 1e7, 2),
            "cmp": info.get('regularMarketPrice') or info.get('currentPrice') or 0,
            "pe": info.get('trailingPE') or info.get('forwardPE'),
            "sector_pe_avg": None,
            "de_ratio": info.get('debtToEquity'),
            "revenue_5y": revenue_5y,
            "revenue_cagr_5y": None,
            "div_yield": round((info.get('dividendYield') or 0) * 100, 2),
            "payout_ratio": round((info.get('payoutRatio') or 0) * 100, 2),
            "roe_5y": [],
            "margin_5y": [],
            "beta": info.get('beta'),
            "volume_today": volume_today,
            "volume_30d_avg": volume_30d_avg,
        }
    except Exception as e:
        print(f"  WARN: {ticker} — {e}")
        return None


def main():
    tickers = fetch_nse_tickers()
    results = []
    for i, ticker in enumerate(tickers):
        if i % 50 == 0:
            print(f"Progress: {i}/{len(tickers)} ({len(results)} succeeded)")
        data = fetch_stock_fundamentals(ticker)
        if data:
            results.append(data)
        time.sleep(0.1)

    out_path = DATA_DIR / "raw_stocks.json"
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} stocks to {out_path}")


if __name__ == '__main__':
    main()
