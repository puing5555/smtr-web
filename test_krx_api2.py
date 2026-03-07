"""KRX API - 올바른 Referer로 테스트"""
import requests, json

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://data.krx.co.kr/contents/MDC/MDI/outerLoader/index.cmd',
}

def krx_post(bld, params):
    url = 'https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
    data = {'bld': bld}
    data.update(params)
    resp = requests.post(url, headers=headers, data=data, timeout=15)
    print(f"  status={resp.status_code}, size={len(resp.text)}")
    if resp.status_code == 200 and resp.text.strip() not in ('LOGOUT', ''):
        try:
            j = resp.json()
            return j
        except Exception as e:
            print('  JSON parse error:', e)
            print('  text:', resp.text[:200])
    else:
        print('  text:', resp.text[:100])
    return None

# 외국인 수급 일별
print('=== 외국인 수급 일별 ===')
r = krx_post('dbms/MDC/STAT/standard/MDCSTAT02202', {
    'mktId': 'STK',
    'invstTpCd': '4000',
    'strtDd': '20250301',
    'endDd': '20250305',
    'money': '3'
})
if r:
    print('keys:', list(r.keys()))
    if 'output' in r and r['output']:
        print('sample:', r['output'][:2])

# 전종목등락률
print('\n=== 전종목등락률 ===')
r2 = krx_post('dbms/MDC/STAT/standard/MDCSTAT01602', {
    'mktId': 'STK',
    'strtDd': '20250301',
    'endDd': '20250305'
})
if r2:
    print('keys:', list(r2.keys()))
    if 'output' in r2 and r2['output']:
        print('sample:', r2['output'][:2])

# VKOSPI 지수
print('\n=== VKOSPI 지수 ===')
r3 = krx_post('dbms/MDC/STAT/standard/MDCSTAT00301', {
    'idxIndMidclssCd': '02',
    'trdDd': '20250305'
})
if r3:
    print('keys:', list(r3.keys()))
    if 'output' in r3 and r3['output']:
        print('sample:', r3['output'][:3])
