"""
Naver fchart API 탐색
fchart.stock.naver.com/sise.nhn?symbol=XXX
"""
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import io

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.naver.com/',
}

def get_naver_chart(symbol, count=60):
    url = f'https://fchart.stock.naver.com/sise.nhn?symbol={symbol}&timeframe=day&count={count}&requestType=0'
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}"
    
    content = r.content.decode('euc-kr', errors='replace')
    if '<protocol />' in content or len(content) < 100:
        return None, "empty protocol"
    
    # Parse XML
    try:
        root = ET.fromstring(content)
        chartdata = root.find('chartdata')
        if chartdata is None:
            return None, "no chartdata"
        
        items = chartdata.findall('item')
        if not items:
            return None, "no items"
        
        rows = []
        for item in items:
            data_str = item.get('data', '')
            parts = data_str.split('|')
            if len(parts) >= 2:
                rows.append(parts)
        
        name = chartdata.get('name', symbol)
        precision = chartdata.get('precision', '2')
        print(f"  Symbol: {symbol}, Name: {name}, count={len(rows)}, precision={precision}")
        if rows:
            print(f"  Latest: {rows[-1]}")
        return rows, "ok"
    except Exception as e:
        return None, f"parse error: {e}"

# 1. Test known symbols
symbols_to_test = [
    'KOSPI', 'KOSDAQ', 'KPI200', 'KOSPI200',
    'VKOSPI', 'VKOSP', 'VIX', 'VOLAT',
    'KVALUE', 'KPI100', 'KRX100',
    'FUT', 'OPTION',
    # KRX indices
    '1', '2', '1001', '2001', '4', '5',
    # Try numeric codes
    '1028',  # KOSPI
    '1004',  # VKOSPI (pykrx code)
]

print("=== Naver fchart symbol test ===")
for sym in symbols_to_test:
    rows, status = get_naver_chart(sym, count=5)
    if status == "ok":
        print(f"  ✅ {sym}: OK, {len(rows)} rows")
    else:
        # Only print if interesting
        if status not in ['empty protocol', f'HTTP 200']:
            print(f"  ❌ {sym}: {status}")

# 2. Now test working symbols in detail
print("\n=== KOSPI chart data ===")
rows, status = get_naver_chart('KOSPI', count=252)
if rows and status == "ok":
    # Parse as DataFrame
    # Format: date|open|high|low|close|volume (typical)
    # Or: date|close|changes (depends on api)
    # Let's check first few rows
    df_data = []
    for row in rows[-10:]:
        df_data.append(row)
    
    # Check column count
    print(f"Column count: {len(rows[0])}")
    print(f"Sample rows: {rows[-3:]}")
    
    # Parse
    df = pd.DataFrame(rows[-252:])
    print(f"DataFrame shape: {df.shape}")
    print(df.tail(3))

# 3. Test VKOSPI with different approach
print("\n=== VKOSPI via naver ===")
# Try the investor/index chart for VKOSPI
vkospi_urls = [
    'https://fchart.stock.naver.com/sise.nhn?symbol=VKOSPI&timeframe=day&count=60&requestType=1',
    'https://fchart.stock.naver.com/exe/sise.nhn?symbol=VKOSPI&timeframe=day&count=60',
]
for url in vkospi_urls:
    r = requests.get(url, headers=headers, timeout=10)
    print(f'{r.status_code}: {url[:70]}')
    if r.status_code == 200:
        print(f'  {r.text[:200]}')

# 4. Test Naver sise index with VKOSPI via mobile API
print("\n=== Mobile API indices ===")
mobile_urls = [
    'https://m.stock.naver.com/api/index/VKOSPI/history?startDateTime=20260101&endDateTime=20260307&type=day',
    'https://m.stock.naver.com/api/index/VKOSPI/histories/day?start=20260101&end=20260307',
    'https://m.stock.naver.com/api/index/VKOSPI/chart',
]
for url in mobile_urls:
    r = requests.get(url, headers=headers, timeout=10)
    print(f'{r.status_code}: {url[:70]}')
    if r.status_code == 200:
        print(f'  {r.text[:200]}')
