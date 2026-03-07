import pykrx, os
pykrx_path = os.path.dirname(pykrx.__file__)

for root, dirs, files in os.walk(pykrx_path):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as fh:
                c = fh.read()
                if 'krx.co.kr' in c:
                    print('FILE:', path)
                    # find URL lines
                    for line in c.split('\n'):
                        if 'url' in line.lower() or 'bld' in line.lower():
                            print('  ', line.strip()[:120])
                    print()
                    break
