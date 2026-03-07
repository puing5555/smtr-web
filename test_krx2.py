import requests
import io
import pandas as pd

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
})

# Visit main page to get session cookies
r0 = session.get('http://data.krx.co.kr/contents/MDC/MDI/mdim/index.cmd', timeout=15)
print(f'Session init: {r0.status_code}')

otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
dl_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'

# Use 20260306 (last trading day - Friday)
LAST_TRADING_DAY = '20260306'

# Test 1: OHLCV
print(f'\n--- Test 1: OHLCV by date {LAST_TRADING_DAY} ---')
params1 = {
    'locale': 'ko_KR',
    'mktId': 'STK',
    'trdDd': LAST_TRADING_DAY,
    'share': '1',
    'money': '1',
    'csvxls_isNo': 'false',
    'name': 'fileDown',
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT01501',
}
session.headers.update({'Referer': 'http://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT01501'})
r = session.post(otp_url, data=params1, timeout=15)
print(f'OTP: {r.status_code}, token len: {len(r.text)}')

if r.status_code == 200 and r.text.strip():
    r2 = session.post(dl_url, data={'code': r.text.strip()}, timeout=30)
    ct = r2.headers.get('Content-Type', '')
    print(f'Download: {r2.status_code}, size: {len(r2.content)}, type: {ct}')
    if len(r2.content) > 100:
        # Try to parse as CSV
        try:
            df = pd.read_csv(io.BytesIO(r2.content), encoding='cp949')
            print(f'CSV rows: {len(df)}, cols: {list(df.columns)}')
            print(df.head(3))
        except Exception as e:
            print(f'CSV parse error: {e}')
            # Try to decode
            try:
                text = r2.content.decode('cp949', errors='replace')
                print('Raw content:', text[:300])
            except:
                print('Raw bytes:', r2.content[:200])

# Test 2: HTTPS version
print(f'\n--- Test 2: HTTPS version ---')
session2 = requests.Session()
session2.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
})
r00 = session2.get('https://data.krx.co.kr/contents/MDC/MDI/mdim/index.cmd', timeout=15)
print(f'HTTPS session init: {r00.status_code}')

session2.headers.update({'Referer': 'https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT01501'})
r_otp2 = session2.post('https://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd', data=params1, timeout=15)
print(f'HTTPS OTP: {r_otp2.status_code}, token: {r_otp2.text[:80]}')

if r_otp2.status_code == 200 and r_otp2.text.strip():
    r_dl2 = session2.post('https://data.krx.co.kr/comm/fileDn/download_csv/download.cmd', 
                          data={'code': r_otp2.text.strip()}, timeout=30)
    print(f'HTTPS Download: {r_dl2.status_code}, size: {len(r_dl2.content)}')
    if len(r_dl2.content) > 100:
        try:
            df = pd.read_csv(io.BytesIO(r_dl2.content), encoding='cp949')
            print(f'CSV rows: {len(df)}')
            print(df.head(3))
        except Exception as e:
            print(f'Parse error: {e}')
            print('Raw:', r_dl2.content[:300])
