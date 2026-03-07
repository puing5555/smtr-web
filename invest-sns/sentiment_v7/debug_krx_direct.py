import requests, json, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'http://data.krx.co.kr/',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
}

# pykrx가 내부적으로 사용하는 URL 확인
import pykrx
import os
pkg_path = os.path.dirname(pykrx.__file__)
print('pykrx 경로:', pkg_path)

# 내부 HTTP 호출 추적
import pykrx.website.krx.market as mkt
import inspect
# 어떤 URL을 사용하는지 확인
for name, obj in inspect.getmembers(mkt):
    if hasattr(obj, '_bld'):
        print(f'{name}: _bld={obj._bld}')

# GenerateOTP 모듈 확인
krx_path = os.path.join(pkg_path, 'website', 'krx', 'market')
for fname in os.listdir(krx_path):
    if fname.endswith('.py'):
        print(f'파일: {fname}')

# 실제 bld 값 찾기
for fname in os.listdir(krx_path):
    if fname.endswith('.py'):
        with open(os.path.join(krx_path, fname), 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        if 'GenerateOTP' in content or 'bld' in content:
            print(f'\n{fname}의 bld 값들:')
            blds = re.findall(r'bld["\']?\s*[=:]\s*["\']([^"\']+)["\']', content)
            print(blds[:10])
