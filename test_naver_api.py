"""
Naver Finance API 테스트
- 52주 신고가/신저가
- 투자자 수급
- 시장 통계
"""
import requests
import json
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Referer': 'https://finance.naver.com/',
}

print("=== 1. 52주 신고가/신저가 ===")
# Try the new Naver URL format
urls = [
    # 신고가
    'https://finance.naver.com/sise/sise_high_low.naver?sosok=0&high_low=1',
    # 시장 통계
    'https://finance.naver.com/sise/sise_market_sum.naver?sosok=0',
    # 시가총액 상위
    'https://finance.naver.com/sise/sise_market_sum.naver',
    # 등락률
    'https://finance.naver.com/sise/siseList.naver?type=&sosok=0',
    # NAVER 금융 API - 검색
    'https://finance.naver.com/sise/field_submit.naver',
]

for url in urls:
    r = requests.get(url, headers=headers, timeout=10)
    print(f'{r.status_code}: {url}')
    if r.status_code == 200 and len(r.content) > 1000:
        content = r.content
        try:
            text = content.decode('euc-kr', errors='replace')
        except:
            text = content.decode('utf-8', errors='replace')
        print(f'  Size: {len(text)}, snippet: {text[:100]}')

print("\n=== 2. 투자자별 매매동향 JSON API ===")
# Naver mobile API for investor trends
urls2 = [
    'https://m.stock.naver.com/api/trades/KOSPI/foreign',
    'https://m.stock.naver.com/api/trades/KOSPI',
    'https://finance.naver.com/api/sise/investorDealTrendDay',
]
for url in urls2:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f'{r.status_code}: {url}')
        if r.status_code == 200:
            print(f'  Size: {len(r.content)}, content: {r.text[:200]}')
    except Exception as e:
        print(f'Error: {e}')

print("\n=== 3. VKOSPI via NAVER JSON ===")
urls3 = [
    'https://m.stock.naver.com/api/index/VKOSPI200/history?startDateTime=20260101&endDateTime=20260307',
    'https://m.stock.naver.com/api/index/KSV/history',
    'https://m.stock.naver.com/api/index/VKOS/history',
]
for url in urls3:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f'{r.status_code}: {url}')
        if r.status_code == 200:
            print(f'  {r.text[:200]}')
    except Exception as e:
        print(f'Error: {e}')

print("\n=== 4. Naver finance stats page ===")
# Check sise/main for market stats
r_main = requests.get('https://finance.naver.com/sise/', headers=headers, timeout=10)
print(f'Sise main: {r_main.status_code}, size: {len(r_main.content)}')
if r_main.status_code == 200:
    try:
        text = r_main.content.decode('euc-kr', errors='replace')
        soup = BeautifulSoup(text, 'html.parser')
        # Look for 신고가/신저가 mention
        for tag in soup.find_all(text=True):
            if '신고가' in tag or '신저가' in tag:
                print(f'  Found: {str(tag)[:100]}')
    except Exception as e:
        print(f'Error: {e}')
