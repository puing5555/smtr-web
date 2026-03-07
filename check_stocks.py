import json
import sys
from collections import Counter

with open('C:/Users/Mario/work/signals_after.json', encoding='utf-8-sig') as f:
    data = json.load(f)

# GOOGL
googl = [r for r in data if r.get('ticker') == 'GOOGL']
print(f'GOOGL records ({len(googl)}):')
for s, c in Counter(r['stock'] for r in googl).most_common():
    print(f'  {c}x {repr(s)}')

# ARM
arm = [r for r in data if r.get('ticker') == 'ARM']
print(f'\nARM records ({len(arm)}):')
for s, c in Counter(r['stock'] for r in arm).most_common():
    print(f'  {c}x {repr(s)}')

# BTC
btc = [r for r in data if r.get('ticker') == 'BTC']
print(f'\nBTC records ({len(btc)}):')
for s, c in Counter(r['stock'] for r in btc).most_common():
    print(f'  {c}x {repr(s)}')

# 267260
h267 = [r for r in data if r.get('ticker') == '267260']
print(f'\nticker=267260 records ({len(h267)}):')
for r in h267:
    print(f'  id={r["id"]} stock={repr(r["stock"])}')

# 298040
h298 = [r for r in data if r.get('ticker') == '298040']
print(f'\nticker=298040 records ({len(h298)}):')
for r in h298:
    print(f'  id={r["id"]} stock={repr(r["stock"])}')
