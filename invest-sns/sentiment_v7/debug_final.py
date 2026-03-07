import requests, json, re
from datetime import datetime, timedelta

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# 1. 네이버 금융 외국인 수급
print('=== 네이버 외국인 수급 ===')
url_nv = 'https://finance.naver.com/sise/sise_index_detail.naver?code=KOSPI'
r = requests.get(url_nv, headers={**headers, 'Referer': 'https://finance.naver.com/'}, timeout=10)
if r.status_code == 200:
    text = r.content.decode('euc-kr', errors='replace')
    # 외국인 순매수 찾기
    foreign = re.findall(r'외국[^<]*<[^>]+>([+-]?[\d,]+)', text)
    print('외국인:', foreign[:5])
    idx = text.find('외국')
    if idx > 0:
        print(text[idx-20:idx+200])

# 2. ECOS 회사채 금리 - 다른 stat code 시도
print('\n=== ECOS 회사채 금리 탐색 ===')
api_key = 'sample'
# 722Y001 = 시장금리(일) - 회사채 포함
for item in ['0AA3', '0BBB3', '5040000', '4060100', '4030000', '403', '503', 'CD91']:
    url2 = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/3/722Y001/D/20260201/20260306/{item}'
    r2 = requests.get(url2, timeout=5)
    data = r2.json()
    if 'StatisticSearch' in data and data['StatisticSearch'].get('list_total_count', 0) > 0:
        rows = data['StatisticSearch']['row']
        print(f'HIT 722Y001/{item}: {rows[0].get("ITEM_NAME1","")}: {rows[0].get("DATA_VALUE","")}')

# 3. Investing.com VKOSPI
print('\n=== Investing.com VKOSPI ===')
url3 = 'https://api.investing.com/api/financialdata/historical/178399?start-date=2026-03-01&end-date=2026-03-07&time-frame=Daily&add-missing-rows=false'
headers3 = {
    **headers,
    'Accept': 'application/json',
    'domain-id': 'www',
}
r3 = requests.get(url3, headers=headers3, timeout=10)
print(f'status={r3.status_code}')
print(r3.text[:300])

# 4. freesis.kofia.or.kr - 올바른 POST 파라미터
print('\n=== freesis.kofia.or.kr ===')
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
})

# GET으로 먼저 접근해서 세션 쿠키 획득
r4 = session.get('http://freesis.kofia.or.kr/stats/M10050040000.do', timeout=10)
print(f'GET status={r4.status_code}')
print(r4.text[:200])
