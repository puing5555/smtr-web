import os, re

pkg = r'C:\Users\Mario\AppData\Roaming\Python\Python314\site-packages\pykrx\website\krx'
for root, dirs, files in os.walk(pkg):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='replace') as fp:
                content = fp.read()
            if 'GenerateOTP' in content or 'generate.cmd' in content:
                print(path)
                urls = re.findall(r'https?://[^\s"\']+', content)
                print(urls[:5])
                # OTP bld 값 찾기
                blds = re.findall(r'"bld":\s*"([^"]+)"', content)
                print('bld:', blds[:5])
                print()
