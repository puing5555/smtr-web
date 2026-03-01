import sys; sys.stdout.reconfigure(encoding='utf-8')
import json

path = r'C:\Users\Mario\work\subs\dalant_5mvn3PfKf9Y.json'
with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)
noise_words = ['Click', 'Settings', 'auto-generated', 'Subtitles']
orig = len(d['subtitles'])
d['subtitles'] = [s for s in d['subtitles'] if not any(n in s['text'] for n in noise_words)]
with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
count = len(d['subtitles'])
print(f"dalant cleaned: {count} (removed {orig - count})")

# Rebuild fulltexts
for name, p in [('hyoseok_bmXgryWXNrw', r'C:\Users\Mario\work\subs\hyoseok_bmXgryWXNrw.json'),
                ('dalant_5mvn3PfKf9Y', path)]:
    with open(p, 'r', encoding='utf-8') as f:
        dd = json.load(f)
    lines = []
    for s in dd['subtitles']:
        m = int(s['start'] // 60)
        sec = int(s['start'] % 60)
        lines.append(f"[{m:02d}:{sec:02d}] {s['text']}")
    out = p.replace('.json', '_fulltext.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"{name}: {len(lines)} lines")
