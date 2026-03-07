import json
from collections import defaultdict, Counter

with open('C:/Users/Mario/work/signals_final.json', encoding='utf-8-sig') as f:
    data = json.load(f)

tg = defaultdict(list)
for r in data:
    t = r.get('ticker')
    s = r.get('stock', '')
    if t:
        tg[t].append(s)

remaining = {}
for ticker, stocks in sorted(tg.items()):
    unique = set(stocks)
    if len(unique) > 1:
        cnt = Counter(stocks)
        remaining[ticker] = dict(cnt)

# Check for any ? in stock names
question_records = [r for r in data if '?' in (r.get('stock') or '')]
garbled_records = [r for r in data if r.get('stock') and all(c == '?' or c == ' ' for c in r['stock'])]

result = {
    'total_records': len(data),
    'remaining_dups': remaining,
    'question_mark_stocks': [{'id': r['id'], 'stock': r['stock'], 'ticker': r['ticker']} for r in question_records],
    'fully_garbled': [{'id': r['id'], 'stock': r['stock'], 'ticker': r['ticker']} for r in garbled_records],
}

with open('C:/Users/Mario/work/final_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('done')
print(f'remaining dups: {len(remaining)} groups')
print(f'? in stock: {len(question_records)} records')
print(f'fully garbled: {len(garbled_records)} records')
