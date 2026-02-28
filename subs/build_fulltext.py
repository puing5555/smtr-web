import json

videos = ['syuka_4QlLhzLfhzU','syuka_g19QLu5tZlo','syuka_wPKfa2qWh4U',
          'hyoseok_fDZnPoK5lyc','hyoseok_ZXuQCpuVCYc','hyoseok_tSXkj2Omz34']

for v in videos:
    d = json.load(open(f'C:/Users/Mario/work/subs/{v}.json', 'r', encoding='utf-8'))
    subs = d.get('subtitles', [])
    full = ' '.join(s['text'] for s in subs)
    print(f'{v}: {len(subs)} segs, {len(full)} chars')
    with open(f'C:/Users/Mario/work/subs/{v}_fulltext.txt', 'w', encoding='utf-8') as f:
        for s in subs:
            mins = int(s['start'] // 60)
            secs = int(s['start'] % 60)
            f.write(f"[{mins}:{secs:02d}] {s['text']}\n")
