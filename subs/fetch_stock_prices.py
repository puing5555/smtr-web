"""Fetch real stock price data from Yahoo Finance and save as JSON for the chart component."""
import httpx
import json
import time
from datetime import datetime, timedelta

def fetch_yahoo_chart(ticker, period="1y"):
    """Fetch chart data from Yahoo Finance."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    params = {
        "range": period,
        "interval": "1wk" if period in ("1y", "2y", "5y", "max") else "1d",
        "includePrePost": "false"
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    
    r = httpx.get(url, params=params, headers=headers, timeout=15)
    if r.status_code != 200:
        print(f"FAIL {ticker}: {r.status_code}")
        return None
    
    data = r.json()
    result = data.get("chart", {}).get("result", [])
    if not result:
        print(f"No data for {ticker}")
        return None
    
    chart = result[0]
    timestamps = chart.get("timestamp", [])
    closes = chart["indicators"]["quote"][0].get("close", [])
    
    # Current price info
    meta = chart.get("meta", {})
    current_price = meta.get("regularMarketPrice", 0)
    prev_close = meta.get("previousClose", 0)
    
    prices = []
    for ts, close in zip(timestamps, closes):
        if close is not None:
            dt = datetime.fromtimestamp(ts)
            prices.append({
                "date": dt.strftime("%Y-%m-%d"),
                "close": round(close)
            })
    
    return {
        "ticker": ticker,
        "currentPrice": round(current_price),
        "previousClose": round(prev_close),
        "change": round(current_price - prev_close),
        "changePercent": round((current_price - prev_close) / prev_close * 100, 2) if prev_close else 0,
        "prices": prices,
        "fetchedAt": datetime.now().isoformat()
    }

# Stocks to fetch
tickers = {
    "005930": "005930.KS",  # Samsung Electronics
    "000660": "000660.KS",  # SK Hynix
}

all_data = {}

for code, yahoo_ticker in tickers.items():
    print(f"Fetching {code} ({yahoo_ticker})...")
    data = fetch_yahoo_chart(yahoo_ticker, "1y")
    if data:
        all_data[code] = data
        print(f"  OK: {len(data['prices'])} data points, current: {data['currentPrice']:,}")
    else:
        print(f"  FAILED")
    time.sleep(1)

# Save to invest-sns data folder
output_path = "C:/Users/Mario/work/invest-sns/data/stockPrices.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\nSaved to {output_path}")
print(f"Stocks: {list(all_data.keys())}")
