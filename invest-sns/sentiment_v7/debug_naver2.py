import requests, json, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120',
    'Referer': 'https://m.stock.naver.com/'
}

# 1. 네이버 시장폭 (상승/하락/보합 종목 수)
print('=== 네이버 시장폭 ===')
url = 'https://m.stock.naver.com/api/index/KOSPI/quotations/nhn-rising-falling'
r = requests.get(url, headers=headers, timeout=10)
print(f'status={r.status_code}')
if r.status_code == 200:
    print(r.text[:500])

# 2. 네이버 시장 요약 (상승/하락 종목 포함될 수 있음)
print('\n=== 네이버 시장 요약 ===')
url2 = 'https://m.stock.naver.com/api/index/KOSPI/summary'  
r2 = requests.get(url2, headers=headers, timeout=10)
print(f'status={r2.status_code}')
if r2.status_code == 200:
    j = r2.json()
    print(json.dumps(j, ensure_ascii=False, indent=2)[:800])

# 3. KOSPI 인덱스 상세
print('\n=== KOSPI 인덱스 상세 ===')
url3 = 'https://m.stock.naver.com/api/index/KOSPI/chart/area/5D'
r3 = requests.get(url3, headers=headers, timeout=10)
print(f'status={r3.status_code}')
if r3.status_code == 200:
    print(r3.text[:300])

# 4. 네이버 시장 통계 (상/하락)
print('\n=== 네이버 시장 통계 ===')
url4 = 'https://m.stock.naver.com/api/index/KOSPI/stat'
r4 = requests.get(url4, headers=headers, timeout=10)
print(f'status={r4.status_code}')
if r4.status_code == 200:
    print(r4.text[:300])

# 5. 네이버 PC 시세 - 상승/하락
print('\n=== 네이버 PC 시세 ===')
import urllib.parse
for code in ['KOSPI', 'KOSDAQ']:
    url5 = f'https://finance.naver.com/sise/sise_index.naver?code={code}'
    r5 = requests.get(url5, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.naver.com/'}, timeout=10)
    if r5.status_code == 200:
        text = r5.content.decode('euc-kr', errors='replace')
        # 상승/하락/보합 찾기
        matches = re.findall(r'(상승|하락|보합)[^\d]*(\d+)', text)
        print(f'{code}: {matches[:6]}')
