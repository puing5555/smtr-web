import json

with open('_deduped_signals_8types_dated.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

total = len(signals)
under_30 = sum(1 for s in signals if (s.get('timestamp_seconds') or 0) < 30)
under_60 = sum(1 for s in signals if (s.get('timestamp_seconds') or 0) < 60)
no_ts = sum(1 for s in signals if not s.get('timestamp_seconds'))

print(f'Total: {total}')
print(f'No timestamp_seconds: {no_ts}')
print(f'Under 30s: {under_30} ({under_30*100//total}%)')
print(f'Under 60s: {under_60} ({under_60*100//total}%)')

print('\nFirst 15:')
for s in signals[:15]:
    ts = s.get('timestamp', '?')
    ts_s = s.get('timestamp_seconds', '?')
    print(f'  {s["asset"]:25s} {ts:10s} = {ts_s}s')
