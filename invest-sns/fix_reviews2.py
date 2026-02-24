import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# 1. Load backup reviews
with open('smtr_data/corinpapa1106/_review_results_backup.json', 'rb') as f:
    raw = f.read()
text = raw.decode('utf-16')

old_reviews = {}
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
    old_reviews[key] = entry

print(f'Old reviews loaded: {len(old_reviews)}')

# 2. Load current signals
with open('smtr_data/corinpapa1106/_deduped_signals_8types_dated.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)
print(f'Current signals: {len(signals)}')

# 3. Build video_id index from old reviews
old_by_video = {}
for key, val in old_reviews.items():
    parts = key.split('_', 1)
    if len(parts) == 2:
        vid_id, asset = parts
        if vid_id not in old_by_video:
            old_by_video[vid_id] = []
        old_by_video[vid_id].append((asset, val))

# 4. Match current signals to old reviews
new_reviews = {}
matched = 0
unmatched = 0

for sig in signals:
    vid_id = sig.get('video_id', '')
    asset = sig.get('asset', sig.get('stock', sig.get('stockName', '')))
    new_key = f'{vid_id}_{asset}'
    
    # Direct match
    if new_key in old_reviews:
        new_reviews[new_key] = old_reviews[new_key]
        matched += 1
        continue
    
    # Try matching by video_id + fuzzy asset
    if vid_id in old_by_video:
        old_entries = old_by_video[vid_id]
        # Try partial match
        found = False
        for old_asset, old_val in old_entries:
            # Check if assets are similar (share key characters)
            asset_lower = asset.lower().replace(' ', '')
            old_lower = old_asset.lower().replace(' ', '')
            
            # Extract known mappings
            if any([
                'cc' in asset_lower and ('캔톤' in old_asset or 'cc' in old_lower),
                'bmnr' in asset_lower and ('비트마인' in old_asset or 'bmnr' in old_lower),
                'nvda' in asset_lower and ('엔비디아' in old_asset or 'nvda' in old_lower),
                'mstr' in asset_lower and ('마이크로스트' in old_asset or 'mstr' in old_lower),
                'pltr' in asset_lower and ('팔란티어' in old_asset or 'pltr' in old_lower),
                'thar' in asset_lower and ('타르' in old_asset or 'thar' in old_lower),
                asset_lower == old_lower,
                asset in old_asset or old_asset in asset,
                # Common Korean substrings
                len(asset) > 2 and asset[:2] in old_asset,
            ]):
                new_reviews[new_key] = old_val
                matched += 1
                found = True
                # Remove from list to avoid double matching
                old_by_video[vid_id] = [(a, v) for a, v in old_by_video[vid_id] if a != old_asset]
                break
        
        if not found:
            # If only one unmatched old entry for this video, and one unmatched new signal
            remaining_old = old_by_video.get(vid_id, [])
            if len(remaining_old) == 1:
                old_asset, old_val = remaining_old[0]
                new_reviews[new_key] = old_val
                matched += 1
                old_by_video[vid_id] = []
            else:
                unmatched += 1
                print(f'  UNMATCHED: {new_key}')
                if remaining_old:
                    print(f'    candidates: {[a for a,v in remaining_old]}')
    else:
        # No video_id match at all - new signal
        unmatched += 1
        print(f'  NO VIDEO MATCH: {new_key}')

approved = sum(1 for v in new_reviews.values() if v.get('status') == 'approved')
rejected = sum(1 for v in new_reviews.values() if v.get('status') == 'rejected')
print(f'\nResult: {len(new_reviews)} matched ({approved} approved, {rejected} rejected), {unmatched} unmatched')

# 5. For unmatched, assume approved (user said all 177 were reviewed, ~5 rejected)
for sig in signals:
    vid_id = sig.get('video_id', '')
    asset = sig.get('asset', sig.get('stock', sig.get('stockName', '')))
    new_key = f'{vid_id}_{asset}'
    if new_key not in new_reviews:
        new_reviews[new_key] = {"status": "approved", "time": "auto-restored"}

final_approved = sum(1 for v in new_reviews.values() if v.get('status') == 'approved')
final_rejected = sum(1 for v in new_reviews.values() if v.get('status') == 'rejected')
print(f'Final: {len(new_reviews)} total ({final_approved} approved, {final_rejected} rejected)')

# 6. Save
with open('_matched_reviews.json', 'w', encoding='utf-8') as f:
    json.dump(new_reviews, f, ensure_ascii=False, indent=2)
print('Saved _matched_reviews.json')
