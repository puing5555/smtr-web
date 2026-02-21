#!/usr/bin/env python3
"""자막 원문에서 content 키워드를 찾아 타임스탬프 보정"""
import json, os, re, glob

with open('_deduped_signals_8types_dated.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

fixed = 0
checked = 0

for sig in signals:
    vid = sig['video_id']
    sub_path = f'{vid}.txt'
    if not os.path.exists(sub_path):
        continue
    
    with open(sub_path, 'r', encoding='utf-8') as f:
        subtitle = f.read()
    
    # Parse subtitle lines: [M:SS] text
    lines = []
    for line in subtitle.split('\n'):
        m = re.match(r'\[(\d+:\d+)\]\s*(.*)', line.strip())
        if m:
            lines.append((m.group(1), m.group(2)))
    
    if not lines:
        continue
    
    checked += 1
    content = sig.get('content', '')
    if not content or len(content) < 10:
        continue
    
    # Extract key phrases (first 15 chars of content)
    key_phrases = []
    # Try first sentence or first 20 chars
    words = content[:30].split()
    if len(words) >= 3:
        key_phrases.append(' '.join(words[:3]))
    if len(words) >= 2:
        key_phrases.append(' '.join(words[:2]))
    
    # Search for the key phrase in subtitle lines
    best_match = None
    best_score = 0
    for ts, text in lines:
        for phrase in key_phrases:
            if phrase in text:
                score = len(phrase)
                if score > best_score:
                    best_score = score
                    best_match = ts
    
    if best_match:
        old_ts = sig.get('timestamp', '')
        old_ts_clean = old_ts.strip('[] ')
        if old_ts_clean != best_match:
            # Parse both to seconds for comparison
            def to_sec(t):
                parts = t.split(':')
                try:
                    return int(parts[0])*60 + int(parts[1])
                except:
                    return 0
            
            old_sec = to_sec(old_ts_clean)
            new_sec = to_sec(best_match)
            
            if abs(old_sec - new_sec) > 15:  # More than 15 sec difference
                sig['timestamp'] = f'[{best_match}]'
                sig['timestamp_seconds'] = new_sec
                fixed += 1
                print(f'  {vid} {sig["asset"]}: [{old_ts_clean}] -> [{best_match}] (diff: {abs(old_sec-new_sec)}s)')

print(f'\nChecked: {checked}, Fixed: {fixed}')

with open('_deduped_signals_8types_dated.json', 'w', encoding='utf-8') as f:
    json.dump(signals, f, ensure_ascii=False, indent=2)
print('Saved')
