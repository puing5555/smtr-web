import json, os, glob

subs_dir = 'C:/Users/Mario/work/subs'
for jf in glob.glob(os.path.join(subs_dir, '*.json')):
    base = os.path.splitext(jf)[0]
    ft = base + '_fulltext.txt'
    if os.path.exists(ft) or 'mass_extract' in jf:
        continue
    try:
        d = json.load(open(jf, 'r', encoding='utf-8'))
        subs = d.get('subtitles', d if isinstance(d, list) else [])
        if not subs:
            print(f'SKIP (empty): {os.path.basename(jf)}')
            continue
        with open(ft, 'w', encoding='utf-8') as f:
            for s in subs:
                start = s.get('start', 0)
                mins = int(start // 60)
                secs = int(start % 60)
                f.write(f"[{mins}:{secs:02d}] {s.get('text','')}\n")
        print(f'OK: {os.path.basename(jf)} -> {len(subs)} lines')
    except Exception as e:
        print(f'ERR: {os.path.basename(jf)}: {e}')
