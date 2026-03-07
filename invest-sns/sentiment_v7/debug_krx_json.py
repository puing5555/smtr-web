import requests, json
from datetime import datetime, timedelta

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'http://data.krx.co.kr/',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest'
}

# 최근 영업일 (금요일)
LAST_BIZ_DAY = '20260306'

# 1. 시장 전체 종목 데이터 (상승/하락 비율)
print('=== 시장 종목별 데이터 ===')
url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
data = {
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT01501',
    'mktId': 'STK',
    'trdDd': LAST_BIZ_DAY,
    'share': '1',
    'money': '1',
}
r = requests.post(url, data=data, headers=headers, timeout=10)
print(f'status={r.status_code}, len={len(r.text)}')
try:
    j = r.json()
    keys = list(j.keys())
    print('keys:', keys)
    if 'output' in j:
        items = j['output']
        print(f'종목 수: {len(items)}')
        if items:
            print('첫번째:', list(items[0].keys()))
            print(items[0])
except Exception as e:
    print(f'JSON 파싱 오류: {e}')
    print(r.text[:300])

# 2. 투자자별 거래실적
print('\n=== 투자자별 거래실적 ===')
data2 = {
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT02201',
    'mktId': 'STK',
    'strtDd': '20260220',
    'endDd': LAST_BIZ_DAY,
    'money': '1',
    'filetype': 'json',
}
r2 = requests.post(url, data=data2, headers=headers, timeout=10)
print(f'status={r2.status_code}, len={len(r2.text)}')
try:
    j2 = r2.json()
    keys2 = list(j2.keys())
    print('keys:', keys2)
    if 'output' in j2:
        items2 = j2['output']
        print(f'행 수: {len(items2)}')
        if items2:
            print('첫번째:', items2[0])
except Exception as e:
    print(f'오류: {e}')
    print(r2.text[:300])
