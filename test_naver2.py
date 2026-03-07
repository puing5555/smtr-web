"""
Naver Finance 심화 테스트
"""
import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Referer': 'https://finance.naver.com/',
}

# 1. Parse sise_market_sum for market breadth
print("=== Naver Market Sum (KOSPI) ===")
r = requests.get('https://finance.naver.com/sise/sise_market_sum.naver?sosok=0', headers=headers, timeout=15)
text = r.content.decode('euc-kr', errors='replace')
soup = BeautifulSoup(text, 'html.parser')

# Look for 상승/하락/보합 data (market breadth)
# The page has "등락" statistics at the top
print("Looking for market breadth data...")
for tag in soup.find_all(['td', 'th', 'span']):
    t = tag.get_text(strip=True)
    if any(k in t for k in ['상승', '하락', '보합', '등락', '신고가', '신저가']):
        print(f'  Found: {t[:80]}')

# 2. Check Naver Sise main for stats
print("\n=== Naver Sise Main ===")
r2 = requests.get('https://finance.naver.com/sise/', headers=headers, timeout=15)
text2 = r2.content.decode('euc-kr', errors='replace')
soup2 = BeautifulSoup(text2, 'html.parser')

# Look for 신고가/신저가 in AJAX calls or page
script_tags = soup2.find_all('script')
for script in script_tags:
    if script.string and ('신고가' in script.string or 'highLow' in script.string or 'high_low' in script.string):
        print('Script containing 신고가:', script.string[:200])

# 3. Check Naver 시장 마감 data
print("\n=== Naver Market Summary API ===")
urls_to_check = [
    'https://polling.finance.naver.com/api/realtime/domestic/market-summary',
    'https://m.stock.naver.com/api/summary',
    'https://m.stock.naver.com/api/market/KOSPI/summary',
    'https://m.stock.naver.com/api/market/KOSPI/breadth',
]
for url in urls_to_check:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f'{r.status_code}: {url}')
        if r.status_code == 200:
            print(f'  {r.text[:300]}')
    except Exception as e:
        print(f'  Error: {e}')

# 4. Naver investor deal trend - check what GET params work
print("\n=== Investor Deal Trend ===")
# Try without date - get latest
for sosok in ['0']:  # 0=KOSPI
    for page in ['1']:
        url = f'https://finance.naver.com/sise/investorDealTrendDay.naver'
        params = {'sosok': sosok, 'page': page}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        text = r.content.decode('euc-kr', errors='replace')
        soup = BeautifulSoup(text, 'html.parser')
        # Find all tables
        tables = soup.find_all('table')
        print(f'sosok={sosok}, page={page}: {r.status_code}, tables={len(tables)}')
        if tables:
            for tbl in tables:
                rows = tbl.find_all('tr')
                data_rows = [row for row in rows if row.find('td') and '0' in row.get_text()]
                if data_rows:
                    print(f'  Data rows: {len(data_rows)}')
                    print(f'  First: {data_rows[0].get_text(separator="|").strip()[:150]}')
