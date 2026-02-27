import json
from collections import defaultdict

with open('C:/Users/Mario/work/3protv_signals.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

out = []

out.append('=== 1. STRONG_BUY 5개 상세 ===\n')
for i, s in enumerate(signals):
    if s['signal'] == 'STRONG_BUY':
        out.append(f"#{i+1}")
        out.append(f"  종목: {s['stock']}")
        out.append(f"  발언자: {s['speaker']}")
        out.append(f"  mention_type: {s['mention']}")
        out.append(f"  핵심발언: {s['quote']}")
        out.append(f"  타임스탬프: {s['ts']}")
        out.append('')

out.append('\n=== 2. 진행자(MC)가 신호 준 건 ===')
mc_names = ['정프로', '여도훈', '홍선애', '앵커', '진행자', '여도은', '허재무', 'MC']
found_mc = False
for s in signals:
    for mc in mc_names:
        if mc in s['speaker']:
            out.append(f"  !! {s['stock']} | {s['signal']} | {s['speaker']} | {s['quote'][:60]}")
            found_mc = True
if not found_mc:
    out.append("  없음 - 모두 게스트 발언")

out.append('\n\n=== 3. 논거인데 BUY 이상 ===')
found_bug = False
for s in signals:
    if '논거' in s['mention'] and s['signal'] in ['STRONG_BUY', 'BUY']:
        out.append(f"  !! {s['stock']} | {s['signal']} | {s['mention']} | {s['speaker']} | {s['quote'][:60]}")
        found_bug = True
if not found_bug:
    out.append("  없음 - 논거 종목은 모두 POSITIVE 이하")

out.append('\n\n=== 4. 같은 종목+발언자, 다른 신호 ===')
groups = defaultdict(list)
for s in signals:
    key = (s['stock'], s['speaker'])
    groups[key].append(s)
for key, sigs in groups.items():
    unique_signals = set(x['signal'] for x in sigs)
    if len(unique_signals) > 1:
        out.append(f"\n  {key[0]} / {key[1]}:")
        for x in sigs:
            out.append(f"    {x['signal']} | {x['mention']} | {x['quote'][:70]}")

with open('C:/Users/Mario/work/verify_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('saved')
