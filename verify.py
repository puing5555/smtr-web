import json
from collections import defaultdict, Counter

with open('C:/Users/Mario/work/signals_after.json', encoding='utf-8-sig') as f:
    data = json.load(f)

ticker_groups = defaultdict(list)
for r in data:
    t = r.get('ticker')
    s = r.get('stock', '')
    if t:
        ticker_groups[t].append(s)

remaining = {}
for ticker, stocks in sorted(ticker_groups.items()):
    unique = set(stocks)
    if len(unique) > 1:
        cnt = Counter(stocks)
        remaining[ticker] = dict(cnt)

if remaining:
    print('남은 중복:')
    print(json.dumps(remaining, ensure_ascii=False, indent=2))
else:
    print('중복 없음! 모두 정리됨')

# 267260 ticker 확인
h267 = [r for r in data if r.get('ticker') == '267260']
print(f'\nticker=267260 records: {len(h267)}')
for r in h267:
    print(f'  id={r["id"]} stock={r["stock"]}')
