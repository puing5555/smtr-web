import json, os, glob

subs_dir = os.path.dirname(os.path.abspath(__file__))
skip_ids = ['Xv-wNA91EPE', 'tSXkj2Omz34', 'fDZnPoK5lyc']

files = glob.glob(os.path.join(subs_dir, '*.json'))
output = []

for f in sorted(files):
    fname = os.path.basename(f)
    if 'transcript' in fname or 'signal' in fname:
        continue
    try:
        data = json.load(open(f, encoding='utf-8'))
    except:
        continue
    vid = data.get('video_id', '?')
    if vid in skip_ids:
        continue
    
    subs = data.get('subtitles', data.get('transcript', []))
    if not isinstance(subs, list) or len(subs) <= 10:
        continue
    
    # Build fulltext
    lines = []
    for s in subs:
        if isinstance(s, dict):
            start = s.get('start', 0)
            text = s.get('text', '')
        else:
            continue
        mins = int(start // 60)
        secs = int(start % 60)
        lines.append(f"[{mins:02d}:{secs:02d}] {text}")
    
    if len(lines) <= 10:
        continue
    
    duration_min = 0
    if subs:
        last = subs[-1]
        if isinstance(last, dict):
            duration_min = (last.get('start', 0) + last.get('duration', 0)) / 60
    
    # Sample: first 15, middle 10, last 10 lines
    total = len(lines)
    sample = lines[:15]
    mid = total // 2
    sample.append(f"... (중간 {mid}줄 생략) ...")
    sample.extend(lines[mid:mid+10])
    sample.append(f"... (후반부 생략) ...")
    sample.extend(lines[-10:])
    
    output.append(f"\n=== {fname} | vid={vid} | {total}줄 | {duration_min:.0f}분 ===")
    output.extend(sample)

with open(os.path.join(subs_dir, 'all_samples.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f"Written {len(output)} lines")
