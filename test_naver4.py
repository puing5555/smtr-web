"""
Naver Finance - 투자자 수급 + 시장폭 실전 테스트
"""
import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Referer': 'https://finance.naver.com/',
}

# 1. Investor deal trend - use last trading date 20260306
print("=== Investor Trend (20260306) ===")
r = requests.get('https://finance.naver.com/sise/investorDealTrendDay.naver',
    params={'bizdate': '20260306', 'sosok': '0'}, headers=headers, timeout=10)
text = r.content.decode('euc-kr', errors='replace')
print(f"Size: {len(text)}")
soup = BeautifulSoup(text, 'html.parser')
# Get all text
print("Full text:", soup.get_text(separator='|', strip=True)[:500])

# 2. Try raw HTML inspection for investor data
print("\n=== investorDealTrendDay raw HTML ===")
print(text[:2000])

# 3. Market summary for breadth
print("\n=== Naver sise main page ===")
r2 = requests.get('https://finance.naver.com/sise/sise_rise_fall.naver',
    params={'sosok': '0'}, headers=headers, timeout=10)
print(f"sise_rise_fall: {r2.status_code}, size: {len(r2.content)}")

# 4. Check for AJAX endpoints in the main sise page
print("\n=== Looking for AJAX endpoints ===")
r3 = requests.get('https://finance.naver.com/sise/', headers=headers, timeout=10)
text3 = r3.content.decode('euc-kr', errors='replace')
# Find all URLs in script tags
scripts = re.findall(r'["\']([^"\']*sise[^"\']*)["\']', text3)
for s in scripts[:20]:
    if '.naver' in s or '.nhn' in s:
        print(f'  URL found: {s}')

# 5. Try the correct sise main AJAX call for market stats  
print("\n=== sise main market stats ===")
r4 = requests.get('https://finance.naver.com/sise/sise_detail.naver',
    params={'sosok': '0'}, headers=headers, timeout=10)
print(f"Status: {r4.status_code}")
if r4.status_code == 200:
    text4 = r4.content.decode('euc-kr', errors='replace')
    print(text4[:500])

# 6. New naver endpoint for market status
r5 = requests.get('https://m.stock.naver.com/api/market/KOSPI/investorVolume',
    headers=headers, timeout=10)
print(f"\nm.stock KOSPI investorVolume: {r5.status_code}")
if r5.status_code == 200:
    print(r5.text[:300])
    
# 7. Check naver for 52주 신고가
r6 = requests.get('https://finance.naver.com/sise/sise_high.naver',
    params={'sosok': '0'}, headers=headers, timeout=10)
print(f"\nsise_high: {r6.status_code}")

r7 = requests.get('https://finance.naver.com/sise/sise_new.naver',
    params={'sosok': '0'}, headers=headers, timeout=10) 
print(f"sise_new: {r7.status_code}")

# 8. Check for naver's 52주 관련 pages
for path in ['sise_52week_high', 'sise_52week_low', '52week_high', 'new52', 'highLow']:
    url = f'https://finance.naver.com/sise/{path}.naver'
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code != 404:
            print(f'{path}: {r.status_code}, size={len(r.content)}')
    except:
        pass
