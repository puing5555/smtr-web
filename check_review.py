import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\Mario\work\smtr-web\signal-review-v3.html', 'r', encoding='utf-8') as f:
    t = f.read()

i = t.find('SIGNALS_DATA = ') + 15
e = t.find(';\n', i)
d = t[i:e]
data = json.loads(d)

# Check for content with quotes that could break buildCard's string concatenation
issues = 0
for s in data:
    for field in ['content', 'asset', 'context', 'title']:
        val = s.get(field, '')
        if "'" in val:
            issues += 1
            if issues <= 3:
                print(f"Single quote in {field}: {val[:80]}")

print(f"\nTotal fields with single quotes: {issues}")
print(f"Total signals: {len(data)}")

# The real issue: buildCard uses string concatenation with single quotes for onclick
# Any single quote in asset name will break: onclick="setReview('video_id_asset', ...)"
for s in data:
    sid = s['video_id'] + '_' + s['asset']
    if "'" in sid:
        print(f"BREAKING: signal id has quote: {sid}")
