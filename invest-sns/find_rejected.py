import json

sigs = json.load(open('smtr_data/corinpapa1106/_deduped_signals_8types_dated.json', 'r', encoding='utf-8'))

targets = [
    ('BMNR', 'POSITIVE', '2026-02-06'),
    ('CC', 'SELL', '2026-01-15'),
    ('이더리움', 'BUY', '2025-12-27'),
    ('NVDA', 'BUY', '2025-08-05'),
    ('PLTR', 'BUY', '2025-08-05'),
]

found = []
for sig in sigs:
    for asset, stype, date in targets:
        if asset in sig.get('asset', '') and sig.get('signal_type') == stype and sig.get('upload_date', '').startswith(date):
            found.append(sig)
            vid = sig.get('video_id', '?')
            a = sig.get('asset', '?')
            st = sig.get('signal_type', '?')
            ud = sig.get('upload_date', '?')
            print(f"Found: {a} | {st} | {ud} | vid={vid}")

print(f"\nTotal found: {len(found)}")
json.dump(found, open('_rejected_5.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
