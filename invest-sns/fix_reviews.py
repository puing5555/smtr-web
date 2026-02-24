import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# Read raw bytes and try multiple approaches
with open('smtr_data/corinpapa1106/_review_results_backup.json', 'rb') as f:
    raw = f.read()

# Decode utf-16
text = raw.decode('utf-16')

# Fix all problematic characters
text = text.replace('\r\n', '\n').replace('\r', '\n')

# Find all key-status pairs with more flexible regex
reviews = {}
# Match: "key": { "status": "approved/rejected", ... }
entries = re.finditer(r'"([^"]+)"\s*:\s*\{([^}]+)\}', text)
for m in entries:
    key = m.group(1)
    body = m.group(2)
    
    status_m = re.search(r'"status"\s*:\s*"(approved|rejected)"', body)
    if not status_m:
        continue
    status = status_m.group(1)
    
    reason = ""
    reason_m = re.search(r'"reason"\s*:\s*"((?:[^"\\]|\\.)*)"', body)
    if reason_m:
        reason = reason_m.group(1)
    
    time_val = ""
    time_m = re.search(r'"time"\s*:\s*"((?:[^"\\]|\\.)*)"', body)
    if time_m:
        time_val = time_m.group(1)
    
    entry = {"status": status, "time": time_val}
    if reason:
        entry["reason"] = reason
    reviews[key] = entry

approved = sum(1 for v in reviews.values() if v.get('status') == 'approved')
rejected = sum(1 for v in reviews.values() if v.get('status') == 'rejected')
print(f'Total: {len(reviews)}, Approved: {approved}, Rejected: {rejected}')

# Show all rejected
for k, v in reviews.items():
    if v.get('status') == 'rejected':
        print(f'  REJECTED: {k}')

# Also check v5 results
try:
    with open('_review_results_v5.json', 'r', encoding='utf-8') as f:
        v5 = json.load(f)
    print(f'\nV5 results: {len(v5)}')
    for k, v in v5.items():
        if k not in reviews:
            print(f'  NEW in v5: {k} = {v.get("status")}')
            reviews[k] = v
except Exception as e:
    print(f'V5 error: {e}')

# Load current signal data to check coverage
try:
    with open('smtr_data/corinpapa1106/_deduped_signals_8types_dated.json', 'r', encoding='utf-8') as f:
        signals = json.load(f)
    print(f'\nSignals: {len(signals)}')
    missing = []
    for sig in signals:
        sig_id = sig.get('video_id', '') + '_' + sig.get('asset', sig.get('stock', sig.get('stockName', '')))
        if sig_id not in reviews:
            missing.append(sig_id)
    print(f'Missing reviews: {len(missing)}')
    for m in missing[:20]:
        print(f'  {m}')
except Exception as e:
    print(f'Signals error: {e}')

# Save final
with open('_clean_reviews_final.json', 'w', encoding='utf-8') as f:
    json.dump(reviews, f, ensure_ascii=False, indent=2)
print(f'\nSaved _clean_reviews_final.json ({len(reviews)} entries)')
