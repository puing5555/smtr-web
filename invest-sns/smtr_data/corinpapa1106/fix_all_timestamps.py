import json, re, os

with open('_deduped_signals_8types_dated.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

def parse_ts(ts_str):
    if not ts_str:
        return None
    ts_str = ts_str.strip('[] ')
    parts = ts_str.split(':')
    try:
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        pass
    return None

fixed = 0
for sig in signals:
    ts = sig.get('timestamp', '')
    secs = parse_ts(ts)
    if secs is not None and secs > 0:
        sig['timestamp_seconds'] = secs
        fixed += 1
    elif secs == 0:
        # Try to find better timestamp from subtitle
        vid = sig['video_id']
        sub_path = f'{vid}.txt'
        if os.path.exists(sub_path):
            with open(sub_path, 'r', encoding='utf-8') as f:
                subtitle = f.read()
            content = sig.get('content', '')[:20]
            for line in subtitle.split('\n'):
                m = re.match(r'\[(\d+:\d+)\]\s*(.*)', line.strip())
                if m and content[:10] in m.group(2):
                    new_secs = parse_ts(m.group(1))
                    if new_secs and new_secs > 10:
                        sig['timestamp'] = f'[{m.group(1)}]'
                        sig['timestamp_seconds'] = new_secs
                        fixed += 1
                        break

with open('_deduped_signals_8types_dated.json', 'w', encoding='utf-8') as f:
    json.dump(signals, f, ensure_ascii=False, indent=2)

has_ts = sum(1 for s in signals if s.get('timestamp_seconds') and s['timestamp_seconds'] > 0)
print(f'Fixed: {fixed}, With valid timestamp: {has_ts}/{len(signals)}')
