import requests, json, re
from datetime import datetime, timedelta

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'http://freesis.kofia.or.kr/',
})

# freesis.kofia.or.kr 세션 쿠키 획득
r = session.get('http://freesis.kofia.or.kr/', timeout=10)
print(f'메인 status={r.status_code}, cookies={dict(session.cookies)}')

# 예탁금 페이지 접근
r2 = session.get('http://freesis.kofia.or.kr/stats/M10050040000.do', timeout=10)
print(f'예탁금 status={r2.status_code}')
# form 파라미터 찾기
forms = re.findall(r'<form[^>]*>(.*?)</form>', r2.text, re.DOTALL)
for form in forms[:2]:
    inputs = re.findall(r'<input[^>]+>', form)
    print('입력 필드:', inputs[:10])

# Hidden field들 추출
hidden_fields = re.findall(r'<input[^>]+name=["\']([^"\']+)["\'][^>]+value=["\']([^"\']*)["\']', r2.text)
print('Hidden fields:', hidden_fields[:10])

# Ajax 엔드포인트 찾기
ajax = re.findall(r'url\s*:\s*["\']([^"\']+)["\']', r2.text)
print('Ajax URLs:', ajax[:10])

# JS 내 함수 찾기  
js_funcs = re.findall(r'function\s+\w+[^{]*{[^}]{0,100}freesis[^}]*}', r2.text)
print('JS 함수:', js_funcs[:3])

# 전체 HTML 일부 출력
idx = r2.text.find('예탁금')
if idx > 0:
    print('\n예탁금 컨텍스트:', r2.text[idx-200:idx+400])
