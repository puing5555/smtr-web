import json, sys
sys.stdout.reconfigure(encoding='utf-8')
signals = json.load(open(r'C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_deduped_signals_8types.json', 'r', encoding='utf-8'))
for t in ['STRONG_BUY','BUY','POSITIVE','HOLD','NEUTRAL','CONCERN','SELL','STRONG_SELL']:
    examples = [s for s in signals if s.get('signal_type') == t][:4]
    print(f'\n=== {t} ===')
    for e in examples:
        content = e.get('content', '')[:100]
        asset = e.get('asset', '')
        print(f'  [{asset}] "{content}"')
