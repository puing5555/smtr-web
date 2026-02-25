import json, re

with open('signal-review-v3.html', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'const SIGNALS_DATA = (\[.*?\]);\s*\n', html, re.DOTALL)
data = json.loads(m.group(1))

targets = ['oC-mHWKj8m8', 'hr5v-QUws9c', 'axurZUkC5Dc', '2wdlIAF0OrA']
for s in data:
    if s['video_id'] in targets:
        key = s['video_id'] + '_' + s['asset']
        print(key)
