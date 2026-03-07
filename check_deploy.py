import urllib.request

urls = [
    'https://puing5555.github.io/invest-sns/_next/static/css/a7914148b7b0df61.css',
    'https://puing5555.github.io/invest-sns/_next/static/chunks/app/dashboard/page-23b9fc9eaf200a63.js',
    'https://puing5555.github.io/invest-sns/dashboard.html',
]
for u in urls:
    name = u.split('/')[-1]
    try:
        r = urllib.request.urlopen(u, timeout=10)
        data = r.read()
        # JS에서 더미데이터 존재 여부 확인
        if name.endswith('.js') and b'\xec\x82\xbc\xec\x84\xb1\xec\xa0\x84\xec\x9e\x90' in data:  # 삼성전자
            print(f'OK  {r.status}  {len(data):>7}b  {name} ✅ 더미데이터 확인')
        else:
            print(f'OK  {r.status}  {len(data):>7}b  {name}')
    except urllib.error.HTTPError as e:
        print(f'HTTP {e.code}        {name}')
    except Exception as e:
        print(f'ERR {e}  {name}')
