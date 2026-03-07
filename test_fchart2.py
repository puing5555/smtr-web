"""
Naver fchart API - working test (no unicode emoji)
"""
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.naver.com/',
}

def get_naver_chart(symbol, count=60):
    url = f'https://fchart.stock.naver.com/sise.nhn?symbol={symbol}&timeframe=day&count={count}&requestType=0'
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        return None
    
    content = r.content.decode('euc-kr', errors='replace')
    if '<protocol />' in content or len(content) < 100:
        return None
    
    try:
        root = ET.fromstring(content)
        chartdata = root.find('chartdata')
        if chartdata is None:
            return None
        
        items = chartdata.findall('item')
        rows = []
        for item in items:
            parts = item.get('data', '').split('|')
            if len(parts) >= 5:
                rows.append(parts)
        
        if not rows:
            return None
            
        name = chartdata.get('name', symbol)
        return {'symbol': symbol, 'name': name, 'rows': rows}
    except:
        return None

# Test all potential VKOSPI symbols
symbols = ['KOSPI', 'KOSDAQ', 'KPI200', 'KVALUE', 'KPI100', 'KRX100',
           'VKOSPI', 'VKOSP', 'VOLAT', 'VIX', 'FUTS', 'KOSP2V',
           'VKOSPI200', 'VKOS200', 'KS200V', 'COSP', 'COSP2I']

print("=== Naver fchart available symbols ===")
working = []
for sym in symbols:
    result = get_naver_chart(sym, count=5)
    if result:
        print(f"OK: {sym} ({result['name']}) - {len(result['rows'])} rows")
        print(f"   Latest: {result['rows'][-1][:6]}")
        working.append(sym)
    else:
        pass  # skip silent

print(f"\nWorking symbols: {working}")

# Now get KOSPI full history for 52-week calculations
print("\n=== KOSPI 1-year chart ===")
result = get_naver_chart('KOSPI', count=300)
if result:
    rows = result['rows']
    print(f"Total rows: {len(rows)}")
    # Parse: date|open|high|low|close|volume
    df = pd.DataFrame(rows, columns=['date','open','high','low','close','volume'])
    df['date'] = pd.to_datetime(df['date'])
    for col in ['open','high','low','close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.sort_values('date')
    print(df.tail(3).to_string())
    print(f"\nLatest KOSPI close: {df['close'].iloc[-1]:.2f}")

# Test KOSDAQ for breadth
print("\n=== KOSDAQ 1-year chart ===")
result_kq = get_naver_chart('KOSDAQ', count=300)
if result_kq:
    rows = result_kq['rows']
    df_kq = pd.DataFrame(rows, columns=['date','open','high','low','close','volume'])
    df_kq['close'] = pd.to_numeric(df_kq['close'], errors='coerce')
    print(f"Latest KOSDAQ close: {df_kq['close'].iloc[-1]:.2f}")

# Try VKOSPI via different method - check naver sise_index
print("\n=== Alternative VKOSPI sources ===")
alt_urls = [
    'https://polling.finance.naver.com/api/realtime/domestic/index/VKOSPI',
    'https://m.stock.naver.com/api/index/VKOSPI/histories?period=1m',
]
for url in alt_urls:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"{r.status_code}: {url}")
    if r.status_code == 200:
        print(f"  {r.text[:300]}")
