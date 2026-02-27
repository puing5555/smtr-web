import json
from collections import defaultdict

with open('C:/Users/Mario/work/3protv_signals.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

print('=== 1. STRONG_BUY 5개 상세 ===')
for i, s in enumerate(signals):
    if s['signal'] == 'STRONG_BUY':
        print(f"\n#{i+1}")
        print(f"  종목: {s['stock']}")
        print(f"  발언자: {s['speaker']}")
        print(f"  mention_type: {s['mention']}")
        print(f"  핵심발언: {s['quote']}")
        print(f"  타임스탬프: {s['ts']}")

print('\n\n=== 2. 진행자(MC)가 신호 준 건 ===')
mc_names = ['정프로', '여도훈', '홍선애', '앵커', '진행자', '여도은', '허재무', 'MC']
found_mc = False
for s in signals:
    for mc in mc_names:
        if mc in s['speaker']:
            print(f"  !! {s['stock']} | {s['signal']} | {s['speaker']} | {s['quote'][:60]}")
            found_mc = True
if not found_mc:
    print("  없음 - 모두 게스트 발언")

print('\n\n=== 3. 논거인데 BUY 이상 ===')
found_bug = False
for s in signals:
    if '논거' in s['mention'] and s['signal'] in ['STRONG_BUY', 'BUY']:
        print(f"  !! {s['stock']} | {s['signal']} | {s['mention']} | {s['speaker']} | {s['quote'][:60]}")
        found_bug = True
if not found_bug:
    print("  없음 - 논거 종목은 모두 POSITIVE 이하")

print('\n\n=== 4. 같은 종목+발언자, 다른 신호 ===')
groups = defaultdict(list)
for s in signals:
    key = (s['stock'], s['speaker'])
    groups[key].append(s)
found_diff = False
for key, sigs in groups.items():
    unique_signals = set(x['signal'] for x in sigs)
    if len(unique_signals) > 1:
        print(f"\n  {key[0]} / {key[1]}:")
        for x in sigs:
            print(f"    {x['signal']} | {x['mention']} | {x['quote'][:70]}")
        found_diff = True
if not found_diff:
    print("  없음 - 같은 종목+발언자 조합은 일관된 신호")
