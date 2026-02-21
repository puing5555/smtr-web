import json
from collections import defaultdict

with open('_all_signals_8types.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

groups = defaultdict(list)
for s in signals:
    key = s['video_id'] + '_' + s['asset']
    groups[key].append(s)

deduped = []
for key, sigs in groups.items():
    if len(sigs) == 1:
        deduped.append(sigs[0])
    else:
        best = max(sigs, key=lambda x: (x.get('confidence', 'LOW') == 'HIGH', len(x.get('content', ''))))
        best['merged_count'] = len(sigs)
        deduped.append(best)

print(f'Before dedup: {len(signals)}, After: {len(deduped)}')
from collections import Counter
types = Counter(s['signal_type'] for s in deduped)
print(f'Types: {dict(types)}')

with open('_deduped_signals_8types.json', 'w', encoding='utf-8') as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)
print('Saved')
