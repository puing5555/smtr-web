import requests, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120',
    'Referer': 'https://finance.naver.com/'
}

# 1. 네이버 금융 - 코스피 등락 통계
print('=== 네이버 시장 통계 ===')
# 코스피 상승/하락 종목 수
url = 'https://finance.naver.com/sise/sise_index.nhn?code=KOSPI'
r = requests.get(url, headers=headers, timeout=10)
print(f'status={r.status_code}')

# 2. 네이버 API
print('\n=== 네이버 시세 API ===')
url2 = 'https://finance.naver.com/api/sise/indexRatio.nhn?code=KOSPI'
r2 = requests.get(url2, headers=headers, timeout=10)
print(f'status={r2.status_code}')
print(r2.text[:500])

# 3. 네이버 상승/하락 종목
print('\n=== 상승/하락 종목 ===')
url3 = 'https://finance.naver.com/sise/sise_index_navi.naver?code=KOSPI'
r3 = requests.get(url3, headers=headers, timeout=10)
print(f'status={r3.status_code}')
print(r3.text[:500])

# 4. KRX 세션 없이 일반 GET
print('\n=== KRX 공시 API ===')
url4 = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
r4 = requests.get(url4 + '?bld=dbms/MDC/STAT/standard/MDCSTAT01501&mktId=STK&trdDd=20260306&share=1&money=1',
    headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'http://data.krx.co.kr/'},
    timeout=10)
print(f'status={r4.status_code}')
print(r4.text[:200])
