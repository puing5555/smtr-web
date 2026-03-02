"""
해외주식/코인 가격 데이터 수집 스크립트
CoinGecko API + Yahoo Finance (yfinance)
"""
import json
import os
import sys
from datetime import datetime, timedelta

# === CoinGecko ===
import urllib.request

COIN_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'SOL': 'solana',
    'DOGE': 'dogecoin',
    'KLAY': 'klay-token',
}

STOCK_TICKERS = [
    'NVDA', 'TSLA', 'PLTR', 'AMD', 'TSM', 'ASML', 'GOOGL',
    'MSTR', 'RKLB', 'SQ', 'RIOT', 'GBTC', 'COIN', 'IREN',
    'GME', 'SOXX', 'MU',
]

KS11_TICKER = '^KS11'

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
STOCK_PRICES_PATH = os.path.join(DATA_DIR, 'stockPrices.json')

USD_KRW = 1380  # fallback

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def get_usd_krw():
    """Get USD/KRW from CoinGecko (bitcoin price ratio)"""
    global USD_KRW
    try:
        data = fetch_json('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=krw,usd')
        btc_krw = data['bitcoin']['krw']
        btc_usd = data['bitcoin']['usd']
        USD_KRW = round(btc_krw / btc_usd)
        print(f"USD/KRW: {USD_KRW}")
    except Exception as e:
        print(f"Failed to get USD/KRW, using {USD_KRW}: {e}")

def fetch_coin_prices():
    """Fetch coin current prices and 1-year history from CoinGecko"""
    results = {}
    
    # Current prices
    ids = ','.join(COIN_MAP.values())
    current = fetch_json(f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=krw&include_24hr_change=true')
    
    for code, cg_id in COIN_MAP.items():
        print(f"Fetching {code} ({cg_id})...")
        price_krw = current[cg_id]['krw']
        change_pct = current[cg_id].get('krw_24h_change', 0)
        change = round(price_krw * change_pct / 100)
        
        # History (365 days)
        import time
        time.sleep(6)  # rate limit (free tier: 10-15 req/min)
        for attempt in range(3):
            try:
                hist = fetch_json(f'https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart?vs_currency=krw&days=365')
                break
            except Exception as e:
                print(f"  Retry {attempt+1}/3: {e}")
                time.sleep(15)
        else:
            print(f"  Failed to fetch history for {code}, skipping")
            continue
        prices = []
        for ts, p in hist['prices']:
            dt = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d')
            prices.append({'date': dt, 'close': round(p)})
        
        # Deduplicate by date (keep last)
        seen = {}
        for p in prices:
            seen[p['date']] = p
        prices = sorted(seen.values(), key=lambda x: x['date'])
        
        results[code] = {
            'currentPrice': round(price_krw),
            'change': round(change),
            'changePercent': round(change_pct, 2),
            'prices': prices,
        }
        print(f"  {code}: {price_krw:,.0f} KRW, {len(prices)} data points")
    
    return results

def fetch_stock_prices():
    """Fetch US stock prices via yfinance"""
    import yfinance as yf
    results = {}
    
    all_tickers = STOCK_TICKERS + [KS11_TICKER]
    
    for ticker in all_tickers:
        code = 'KS11' if ticker == '^KS11' else ticker
        print(f"Fetching {code} ({ticker})...")
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period='1y')
            if hist.empty:
                print(f"  No data for {ticker}")
                continue
            
            last_close = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else last_close
            
            is_krw = ticker == '^KS11'
            if is_krw:
                price_krw = round(last_close)
                change_krw = round(last_close - prev_close)
            else:
                price_krw = round(last_close * USD_KRW)
                change_krw = round((last_close - prev_close) * USD_KRW)
            
            change_pct = round((last_close - prev_close) / prev_close * 100, 2) if prev_close else 0
            
            prices = []
            for date, row in hist.iterrows():
                dt = date.strftime('%Y-%m-%d')
                close = round(row['Close']) if is_krw else round(row['Close'] * USD_KRW)
                prices.append({'date': dt, 'close': close})
            
            results[code] = {
                'currentPrice': price_krw,
                'change': change_krw,
                'changePercent': change_pct,
                'prices': prices,
            }
            print(f"  {code}: {price_krw:,.0f} KRW, {len(prices)} data points")
        except Exception as e:
            print(f"  Error fetching {ticker}: {e}")
    
    return results

def main():
    print("=== Fetching USD/KRW rate ===")
    get_usd_krw()
    
    print("\n=== Fetching Coin Prices ===")
    coin_data = fetch_coin_prices()
    
    print("\n=== Fetching Stock Prices ===")
    stock_data = fetch_stock_prices()
    
    # Load existing stockPrices.json
    with open(STOCK_PRICES_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    # Merge
    existing.update(coin_data)
    existing.update(stock_data)
    
    # Save
    with open(STOCK_PRICES_PATH, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False)
    
    print(f"\n=== Done! Updated {len(coin_data) + len(stock_data)} entries in stockPrices.json ===")
    print(f"Total entries: {len(existing)}")

if __name__ == '__main__':
    main()
