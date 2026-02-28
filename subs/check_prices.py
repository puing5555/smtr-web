import json
with open('C:/Users/Mario/work/invest-sns/data/stockPrices.json', 'r') as f:
    data = json.load(f)

for code in ['005930', '000660']:
    s = data[code]
    prices = s['prices']
    closes = [p['close'] for p in prices]
    print(f"{code}: current={s['currentPrice']:,} range={min(closes):,}~{max(closes):,}")
    print(f"  first={prices[0]['date']} {prices[0]['close']:,} last={prices[-1]['date']} {prices[-1]['close']:,}")
    print(f"  points={len(prices)} change={s['change']:+,} ({s['changePercent']:+.2f}%)")
