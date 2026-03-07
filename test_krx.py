import requests

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
})

# First, visit main page
r0 = session.get('http://data.krx.co.kr/contents/MDC/MDI/mdim/index.cmd', timeout=15)
print(f'Main: {r0.status_code}, cookies: {list(session.cookies.keys())}')

# Try the correct OTP URL
otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
params = {
    'locale': 'ko_KR',
    'mktId': 'STK',
    'trdDd': '20260307',
    'share': '1',
    'money': '1',
    'csvxls_isNo': 'false',
    'name': 'fileDown',
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT01501',
}
session.headers.update({'Referer': 'http://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT01501'})
r1 = session.post(otp_url, data=params, timeout=15)
print(f'OTP: {r1.status_code}, token: {r1.text[:80]}')

if r1.status_code == 200 and r1.text.strip():
    # Try download
    dl_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
    r2 = session.post(dl_url, data={'code': r1.text.strip()}, timeout=15)
    ct = r2.headers.get('Content-Type', '')
    print(f'Download: {r2.status_code}, size: {len(r2.content)}, type: {ct}')
    if r2.content:
        print('First 200 bytes:', r2.content[:200])

# Test investor trading
print('\n--- Test investor trading ---')
params2 = {
    'locale': 'ko_KR',
    'mktId': 'STK',
    'strtDd': '20260304',
    'endDd': '20260307',
    'money': '1',
    'detailView': '1',
    'name': 'fileDown',
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT02301',
}
session.headers.update({'Referer': 'http://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT02301'})
r3 = session.post(otp_url, data=params2, timeout=15)
print(f'OTP2: {r3.status_code}, token: {r3.text[:80]}')

if r3.status_code == 200 and r3.text.strip():
    r4 = session.post(dl_url, data={'code': r3.text.strip()}, timeout=15)
    print(f'Download2: {r4.status_code}, size: {len(r4.content)}')
    if r4.content:
        print('First 200:', r4.content[:200])

# Test put/call ratio
print('\n--- Test put/call ---')
params3 = {
    'locale': 'ko_KR',
    'trdDd': '20260307',
    'prodId': 'KO2',
    'name': 'fileDown',
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT12501',
}
session.headers.update({'Referer': 'http://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT12501'})
r5 = session.post(otp_url, data=params3, timeout=15)
print(f'OTP3: {r5.status_code}, token: {r5.text[:80]}')

if r5.status_code == 200 and r5.text.strip():
    r6 = session.post(dl_url, data={'code': r5.text.strip()}, timeout=15)
    print(f'Download3: {r6.status_code}, size: {len(r6.content)}')
    if r6.content:
        print('First 200:', r6.content[:200])
