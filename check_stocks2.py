import json
import sys
from collections import Counter

with open('C:/Users/Mario/work/signals_after.json', encoding='utf-8-sig') as f:
    data = json.load(f)

result = {}

# GOOGL
googl = [r for r in data if r.get('ticker') == 'GOOGL']
result['GOOGL'] = dict(Counter(r['stock'] for r in googl).most_common())

# ARM
arm = [r for r in data if r.get('ticker') == 'ARM']
result['ARM'] = dict(Counter(r['stock'] for r in arm).most_common())

# BTC
btc = [r for r in data if r.get('ticker') == 'BTC']
result['BTC'] = dict(Counter(r['stock'] for r in btc).most_common())

# 267260
h267 = [r for r in data if r.get('ticker') == '267260']
result['267260'] = [{k: r[k] for k in ['id','stock']} for r in h267]

# 298040
h298 = [r for r in data if r.get('ticker') == '298040']
result['298040'] = [{k: r[k] for k in ['id','stock']} for r in h298]

# All remaining duplicates
ticker_groups = {}
from collections import defaultdict
tg = defaultdict(list)
for r in data:
    t = r.get('ticker')
    s = r.get('stock', '')
    if t:
        tg[t].append(s)
for ticker, stocks in sorted(tg.items()):
    unique = set(stocks)
    if len(unique) > 1:
        ticker_groups[ticker] = dict(Counter(stocks).most_common())

result['remaining_dups'] = ticker_groups

with open('C:/Users/Mario/work/check_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('done')
