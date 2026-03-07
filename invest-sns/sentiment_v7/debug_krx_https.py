import requests, json

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://data.krx.co.kr/contents/MDC/MDI/outerLoader/index.cmd',
}

# pykrx가 실제 사용하는 HTTPS URL
url = 'https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'

# 1. 시장 전체 종목 시세 (MDCSTAT01501)
print('=== 시장 종목별 시세 ===')
data = {
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT01501',
    'mktId': 'STK',
    'trdDd': '20260306',
    'share': '1',
    'money': '1',
}
r = requests.post(url, headers=headers, data=data, timeout=10)
print(f'status={r.status_code}, len={len(r.text)}')
try:
    j = r.json()
    keys = list(j.keys())
    print('keys:', keys)
    if 'output' in j:
        items = j['output']
        print(f'종목 수: {len(items)}')
        if items:
            print('컬럼:', list(items[0].keys())[:10])
            print('첫번째:', items[0])
except Exception as e:
    print(f'오류: {e}')
    print(r.text[:300])

print()

# 2. 투자자별 거래실적 (일별)
print('=== 투자자별 거래실적 ===')
data2 = {
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT02201',
    'mktId': 'STK',
    'strtDd': '20260220',
    'endDd': '20260306',
    'money': '1',
}
r2 = requests.post(url, headers=headers, data=data2, timeout=10)
print(f'status={r2.status_code}, len={len(r2.text)}')
try:
    j2 = r2.json()
    print('keys:', list(j2.keys()))
    if 'output' in j2:
        items2 = j2['output']
        print(f'행 수: {len(items2)}')
        if items2:
            print('컬럼:', list(items2[0].keys()))
            print('첫번째:', items2[0])
except Exception as e:
    print(f'오류: {e}')
    print(r2.text[:300])

print()

# 3. VKOSPI 인덱스 (MDCSTAT00601)  
print('=== VKOSPI 인덱스 ===')
data3 = {
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT00601',
    'idxIndMktClss': 'KRX',
    'idxCd': '1004',
    'strtDd': '20260201',
    'endDd': '20260306',
}
r3 = requests.post(url, headers=headers, data=data3, timeout=10)
print(f'status={r3.status_code}, len={len(r3.text)}')
try:
    j3 = r3.json()
    print('keys:', list(j3.keys()))
    if 'output' in j3:
        items3 = j3['output']
        print(f'행 수: {len(items3)}')
        if items3:
            print('컬럼:', list(items3[0].keys()))
            print('첫번째:', items3[0])
except Exception as e:
    print(f'오류: {e}')
    print(r3.text[:300])
