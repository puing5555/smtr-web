import requests, json, re
from datetime import datetime, timedelta

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120',
}

# 1. 네이버 금융 코스피 실시간 정보 (상승/하락 종목)
print('=== 네이버 코스피 현황 ===')
url = 'https://finance.naver.com/sise/sise_index.naver?code=KOSPI'
r = requests.get(url, headers=headers, timeout=10)
if r.status_code == 200:
    # 상승/하락 종목 수 파싱
    text = r.text
    # 상승 종목 찾기
    up_match = re.findall(r'상승\s*</span>\s*<span[^>]*>(\d+)', text)
    down_match = re.findall(r'하락\s*</span>\s*<span[^>]*>(\d+)', text)
    print('상승:', up_match)
    print('하락:', down_match)
    # 더 넓게 검색
    all_nums = re.findall(r'(\d+)</em>\s*<em[^>]*>(\d+)</em>\s*<em[^>]*>(\d+)</em>', text)
    print('숫자 트리플:', all_nums[:5])
else:
    print(f'실패: {r.status_code}')

# 2. 네이버 금융 마켓 인덱스 API (JSON)
print('\n=== 네이버 마켓 지수 ===')
url2 = 'https://m.stock.naver.com/api/index/KOSPI/basic'
r2 = requests.get(url2, headers={**headers, 'Referer': 'https://m.stock.naver.com/'}, timeout=10)
print(f'status={r2.status_code}')
if r2.status_code == 200:
    j = r2.json()
    print(json.dumps(j, ensure_ascii=False, indent=2)[:800])

# 3. VKOSPI 데이터 - KRX 인덱스 API
print('\n=== VKOSPI 데이터 ===')
url3 = 'https://m.stock.naver.com/api/index/VKOSPI/basic'
r3 = requests.get(url3, headers={**headers, 'Referer': 'https://m.stock.naver.com/'}, timeout=10)
print(f'status={r3.status_code}')
if r3.status_code == 200:
    print(r3.text[:300])

# 4. KRX 인덱스 공개 API
print('\n=== KRX 인덱스 ===')
url4 = 'http://www.krx.co.kr/data/COM/GenerateOTP.jspx'
r4 = requests.post(url4, data={
    'name': 'fileDown',
    'filetype': 'xls',
    'url': 'MKD/01/0110/01100305/mkd01100305_01',
    'idxIndMktClss': 'STK',
    'idxId': '1',
    'fromdate': '20260301',
    'todate': '20260306',
}, headers=headers, timeout=10)
print(f'status={r4.status_code}')
print(r4.text[:200])
