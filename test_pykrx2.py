import pykrx, os
pykrx_path = os.path.dirname(pykrx.__file__)

# market/core.py 읽어서 실제 BLD 값들 확인
core_path = os.path.join(pykrx_path, 'website', 'krx', 'market', 'core.py')
with open(core_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 클래스명과 bld 값 추출
lines = content.split('\n')
current_class = ''
for i, line in enumerate(lines):
    if line.startswith('class '):
        current_class = line.strip()
    if 'return "dbms/' in line or "return 'dbms/" in line:
        print(f"{current_class}")
        print(f"  BLD: {line.strip()}")
        print()
