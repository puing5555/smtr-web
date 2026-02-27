import os, re, json
from collections import Counter

files = ['3protv_g1.md','3protv_g2.md','3protv_g3.md','3protv_g4.md','3protv_g5.md','3protv_g6.md']

signals = []
for fname in files:
    path = f'C:/Users/Mario/work/{fname}'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('|') and not line.startswith('|--') and not line.startswith('| 종목') and not line.startswith('|종목') and not line.startswith('|---'):
            cols = [c.strip() for c in line.split('|')]
            cols = [c for c in cols if c]
            if len(cols) >= 4:
                valid_sigs = ['STRONG_BUY','BUY','POSITIVE','HOLD','NEUTRAL','CONCERN','SELL','STRONG_SELL']
                if any(s in cols[2] for s in valid_sigs):
                    signals.append({
                        'stock': cols[0],
                        'mention': cols[1],
                        'signal': cols[2],
                        'speaker': cols[3] if len(cols) > 3 else '',
                        'quote': cols[4] if len(cols) > 4 else '',
                        'ts': cols[5] if len(cols) > 5 else '',
                    })

order = {'STRONG_BUY':0,'BUY':1,'POSITIVE':2,'HOLD':3,'NEUTRAL':4,'CONCERN':5,'SELL':6,'STRONG_SELL':7}
signals.sort(key=lambda x: order.get(x['signal'], 99))

sig_counts = Counter(s['signal'] for s in signals)
stock_counts = Counter(s['stock'] for s in signals)

print('=== SIGNAL DISTRIBUTION ===')
for sig, cnt in sorted(sig_counts.items(), key=lambda x: order.get(x[0],99)):
    print(f'{sig}: {cnt}')

print(f'\nTotal: {len(signals)} signals')
print(f'Unique stocks: {len(stock_counts)}')

print('\n=== TOP MENTIONED STOCKS ===')
for stock, cnt in stock_counts.most_common(10):
    print(f'{stock}: {cnt}x')

print('\n=== ALL SIGNALS ===')
for s in signals:
    sig = s['signal'].ljust(12)
    stk = s['stock'][:15].ljust(15)
    mt = s['mention'][:6].ljust(6)
    sp = s['speaker'][:10]
    print(f'{sig} | {stk} | {mt} | {sp}')

# Save as JSON
with open('C:/Users/Mario/work/3protv_signals.json', 'w', encoding='utf-8') as f:
    json.dump(signals, f, ensure_ascii=False, indent=2)
print(f'\nSaved to 3protv_signals.json')
