import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

# Clean hyoseok
path = r'C:\Users\Mario\work\subs\hyoseok_bmXgryWXNrw.json'
with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)
noise = {'Korean (auto-generated)', 'English (auto-generated)', ''}
orig = len(d['subtitles'])
d['subtitles'] = [s for s in d['subtitles'] if s['text'].strip() not in noise]
with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print(f"hyoseok: {len(d['subtitles'])} (removed {orig - len(d['subtitles'])})")

# Check dalant
path2 = r'C:\Users\Mario\work\subs\dalant_5mvn3PfKf9Y.json'
with open(path2, 'r', encoding='utf-8') as f:
    d2 = json.load(f)
print(f"dalant: {len(d2['subtitles'])} subtitles")
for s in d2['subtitles'][:3]:
    print(f"  {s['text'][:60]}")

# Build fulltext for both
for name, path in [('hyoseok_bmXgryWXNrw', r'C:\Users\Mario\work\subs\hyoseok_bmXgryWXNrw.json'),
                    ('dalant_5mvn3PfKf9Y', r'C:\Users\Mario\work\subs\dalant_5mvn3PfKf9Y.json')]:
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    lines = []
    for s in d['subtitles']:
        mins = int(s['start'] // 60)
        secs = int(s['start'] % 60)
        lines.append(f"[{mins:02d}:{secs:02d}] {s['text']}")
    fulltext = '\n'.join(lines)
    out = path.replace('.json', '_fulltext.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(fulltext)
    print(f"Fulltext: {name} -> {len(lines)} lines")
