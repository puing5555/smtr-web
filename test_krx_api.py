"""KRX API 직접 테스트"""
import requests, json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://data.krx.co.kr/',
    'Content-Type': 'application/x-www-form-urlencoded',
})

# 초기 세션
session.get('https://data.krx.co.kr/', timeout=10)

def krx_post(bld, params):
    url = 'https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
    data = {'bld': bld, 'locale': 'ko_KR', 'csvxls_isNo': 'false'}
    data.update(params)
    resp = session.post(url, data=data, timeout=15)
    print(f"  status={resp.status_code}, size={len(resp.text)}, preview={resp.text[:100]}")
    if resp.status_code == 200 and resp.text != 'LOGOUT':
        try:
            return resp.json()
        except:
            pass
    return None

# 1) 전체지수시세 (코스피 등 지수 목록)
print('=== 전체지수시세 ===')
r = krx_post('dbms/MDC/STAT/standard/MDCSTAT00101', {
    'idxIndMidclssCd': '02',  # KOSPI
    'trdDd': '20250305'
})
if r:
    keys = list(r.keys())
    print('keys:', keys)
    if 'output' in r:
        print('output[0]:', r['output'][0] if r['output'] else 'empty')

# 2) 개별지수시세 (VKOSPI - 1004)
print('\n=== 개별지수시세 VKOSPI ===')
r2 = krx_post('dbms/MDC/STAT/standard/MDCSTAT00301', {
    'idxIndMidclssCd': '02',
    'trdDd': '20250305',
    'indIdx': '1',
    'indIdx2': '1004'
})
if r2:
    print('keys:', list(r2.keys()))
    if 'output' in r2 and r2['output']:
        print('output[0]:', r2['output'][0])

# 3) 투자자별 거래실적 일별추이
print('\n=== 투자자별 거래실적 일별추이 ===')
r3 = krx_post('dbms/MDC/STAT/standard/MDCSTAT02202', {
    'mktId': 'STK',
    'invstTpCd': '4000',  # 외국인
    'strtDd': '20250301',
    'endDd': '20250305',
    'money': '3'
})
if r3:
    print('keys:', list(r3.keys()))
    if 'output' in r3 and r3['output']:
        print('output[0]:', r3['output'][0])

# 4) 전종목등락률
print('\n=== 전종목등락률 (상승/하락 종목 수) ===')
r4 = krx_post('dbms/MDC/STAT/standard/MDCSTAT01602', {
    'mktId': 'STK',
    'strtDd': '20250301',
    'endDd': '20250305'
})
if r4:
    print('keys:', list(r4.keys()))
    if 'output' in r4 and r4['output']:
        print('first 2:', r4['output'][:2])
