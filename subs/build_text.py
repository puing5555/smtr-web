import json

with open('C:/Users/Mario/work/subs/booreadman_Xv-wNA91EPE_transcript.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

lines = []
for s in data['segments']:
    mins = int(s['start'] // 60)
    secs = int(s['start'] % 60)
    lines.append(f"[{mins}:{secs:02d}] {s['text']}")

full = '\n'.join(lines)
print(f"Total chars: {len(full)}")
print("--- First 2000 chars ---")
print(full[:2000])

with open('C:/Users/Mario/work/subs/booreadman_Xv-wNA91EPE_fulltext.txt', 'w', encoding='utf-8') as f:
    f.write(full)
