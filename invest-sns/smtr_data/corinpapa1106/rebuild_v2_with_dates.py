import json

# Load signals and dates
with open('_deduped_signals_8types.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)
with open('_video_dates.json', 'r', encoding='utf-8') as f:
    dates = json.load(f)

# Add dates to signals
for sig in signals:
    sig['upload_date'] = dates.get(sig['video_id'], '')

# Sort by date descending (newest first)
signals.sort(key=lambda s: s.get('upload_date', ''), reverse=True)

print(f"Signals: {len(signals)}")
print(f"Date range: {signals[-1].get('upload_date','')} ~ {signals[0].get('upload_date','')}")

# Save
with open('_deduped_signals_8types_dated.json', 'w', encoding='utf-8') as f:
    json.dump(signals, f, ensure_ascii=False, indent=2)
print("Saved _deduped_signals_8types_dated.json")
