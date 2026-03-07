"""KRX OTP 방식 테스트"""
import requests, json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://data.krx.co.kr/contents/MDC/MDI/outerLoader/index.cmd',
})

def get_otp(bld, params):
    """KRX OTP 방식: 먼저 OTP 발급 후 데이터 요청"""
    otp_url = 'https://data.krx.co.kr/comm/bldAttendant/executeForResourceBundle.cmd'
    otp_params = {'bld': bld, 'locale': 'ko_KR'}
    otp_params.update(params)
    
    r = session.post(otp_url, data=otp_params, timeout=10)
    print(f'  OTP status={r.status_code}, text={r.text[:100]}')
    return r.text.strip()

def get_data_with_otp(bld, params):
    """OTP 받아서 데이터 조회"""
    otp = get_otp(bld, params)
    if not otp or len(otp) > 100:
        print('  OTP failed')
        return None
    
    data_url = 'https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
    data_params = {'bld': bld, 'token': otp}
    data_params.update(params)
    
    r = session.post(data_url, data=data_params, timeout=10)
    print(f'  DATA status={r.status_code}, size={len(r.text)}, preview={r.text[:100]}')
    if r.status_code == 200 and r.text not in ('LOGOUT', ''):
        try:
            return r.json()
        except:
            pass
    return None

print('=== 외국인 수급 OTP 방식 ===')
r = get_data_with_otp('dbms/MDC/STAT/standard/MDCSTAT02202', {
    'mktId': 'STK',
    'invstTpCd': '4000',
    'strtDd': '20250301',
    'endDd': '20250305',
    'money': '3'
})
if r:
    print('SUCCESS:', list(r.keys()))

# 다른 방식: 직접 data.krx.co.kr 접속 후 쿠키로
print('\n=== 세션 쿠키 방식 ===')
init = session.get('https://data.krx.co.kr/', timeout=10)
print('main page status:', init.status_code)
print('cookies:', dict(session.cookies))

data_url = 'https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
r2 = session.post(data_url, data={
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT02202',
    'mktId': 'STK',
    'invstTpCd': '4000',
    'strtDd': '20250301',
    'endDd': '20250305',
    'money': '3'
}, timeout=10)
print(f'with cookies: status={r2.status_code}, preview={r2.text[:100]}')
