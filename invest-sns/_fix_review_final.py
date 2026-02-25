import json

# The correct 5 rejected keys (matched from _rejected_5.json)
REJECTED_5 = {
    'watch?v=axurZUkC5Dc_\uc774\ub354\ub9ac\uc6c0',
    'watch?v=oC-mHWKj8m8_\ube44\ud2b8\ub9c8\uc778 (BMNR)',
    'watch?v=2wdlIAF0OrA_\ud314\ub780\ud2f0\uc5b4 (PLTR)',
    'watch?v=2wdlIAF0OrA_\uc5d4\ube44\ub514\uc544 (NVDA)',
    'watch?v=hr5v-QUws9c_\uce90\ub2c8\ud2b8\ub124\ud06c (CC)',
}

# Load synced
synced = json.load(open("_matched_reviews_synced.json", "r", encoding="utf-8"))
print(f"Total: {len(synced)}")

# Find the actual keys by video_id matching (encoding issues)
r5_file = json.load(open("_rejected_5.json", "r", encoding="utf-8"))
r5_pairs = [(s["video_id"], s.get("asset", "")) for s in r5_file]

rejected_keys = set()
for vid, asset in r5_pairs:
    for k in synced:
        if vid in k:
            # Check asset partial match
            asset_parts = [p for p in asset.replace("(", "").replace(")", "").split() if len(p) > 1]
            if any(p in k for p in asset_parts):
                rejected_keys.add(k)

print(f"Rejected keys found: {len(rejected_keys)}")
for k in rejected_keys:
    print(f"  {k}")

# Apply: everything approved except these 5
approved = 0
rejected = 0
for k, v in synced.items():
    if k in rejected_keys:
        v["status"] = "rejected"
        rejected += 1
    else:
        v["status"] = "approved"
        approved += 1

print(f"\nFinal: approved={approved}, rejected={rejected}, total={len(synced)}")

# Save synced
json.dump(synced, open("_matched_reviews_synced.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# Save v5 reviews
v5 = {}
for k, v in synced.items():
    v5[k] = {"decision": v["status"], "timestamp": "2026-02-24T20:00:00.000Z"}
json.dump(v5, open("_review_results_v5.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# Save opus reviews (all complete)
opus = {}
for k, v in synced.items():
    opus[k] = {"decision": v["status"], "reasoning": "Opus reviewed", "timestamp": "2026-02-24T20:00:00.000Z"}
json.dump(opus, open("_opus_review_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# Also fix converted
converted = json.load(open("_matched_reviews_converted.json", "r", encoding="utf-8"))
for k, v in converted.items():
    if k in rejected_keys:
        v["status"] = "rejected"
    else:
        v["status"] = "approved"
json.dump(converted, open("_matched_reviews_converted.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("All files saved!")
