import json, re

# The 5 rejected - exact keys from the embedded HTML format
REJECTED_KEYS = [
    'watch?v=oC-mHWKj8m8_비트마인 (BMNR)',
    'watch?v=hr5v-QUws9c_캐니트네크 (CC)',  # might be different name
    'watch?v=axurZUkC5Dc_이더리움',
    'watch?v=2wdlIAF0OrA_엔비디아 (NVDA)',
    'watch?v=2wdlIAF0OrA_팔란티어 (PLTR)',
]

with open("signal-review-v4-embedded.html", "r", encoding="utf-8") as f:
    html = f.read()

# Extract reviewsData section
match = re.search(r'let reviewsData = (\{.*?\});', html, re.DOTALL)
if not match:
    print("Could not find reviewsData!")
    exit(1)

reviews_str = match.group(1)
# Fix potential issues and parse
reviews = json.loads(reviews_str)
print(f"Found {len(reviews)} review entries")

# Current state
approved = sum(1 for v in reviews.values() if v.get("status") == "approved")
rejected = sum(1 for v in reviews.values() if v.get("status") == "rejected")
print(f"Current: approved={approved}, rejected={rejected}")

# Show all currently rejected
print("\nCurrently rejected:")
for k, v in reviews.items():
    if v.get("status") == "rejected":
        print(f"  {k}")

# Find the correct 5 rejected keys by video_id matching
r5_file = json.load(open("_rejected_5.json", "r", encoding="utf-8"))
actual_rejected_keys = set()
for s in r5_file:
    vid = s["video_id"]
    asset = s.get("asset", "")
    # Find matching key in reviews
    for k in reviews:
        if vid in k:
            # Check if asset ticker matches
            ticker = ""
            m = re.search(r'\((\w+)\)', asset)
            if m:
                ticker = m.group(1)
            
            if ticker and ticker in k:
                actual_rejected_keys.add(k)
            elif not ticker and asset in k:
                # For 이더리움 (no ticker)
                actual_rejected_keys.add(k)

print(f"\nMatched rejected keys: {len(actual_rejected_keys)}")
for k in actual_rejected_keys:
    print(f"  {k}")

# Apply: set all to approved, then set these 5 to rejected
for k in reviews:
    reviews[k]["status"] = "approved"
for k in actual_rejected_keys:
    if k in reviews:
        reviews[k]["status"] = "rejected"

new_approved = sum(1 for v in reviews.values() if v.get("status") == "approved")
new_rejected = sum(1 for v in reviews.values() if v.get("status") == "rejected")
print(f"\nAfter fix: approved={new_approved}, rejected={new_rejected}")

if new_approved == 172 and new_rejected == 5:
    # Replace in HTML
    new_reviews_str = json.dumps(reviews, ensure_ascii=False, indent=2)
    new_html = html[:match.start(1)] + new_reviews_str + html[match.end(1):]
    
    with open("signal-review-v4-embedded.html", "w", encoding="utf-8") as f:
        f.write(new_html)
    print("HTML file saved!")
else:
    print(f"ERROR: Expected 172/5, got {new_approved}/{new_rejected}")
    # Try broader match for 이더리움
    print("\nAll keys with axurZUkC5Dc:")
    for k in reviews:
        if "axurZUkC5Dc" in k:
            print(f"  {k}")
    print("\nAll keys with hr5v-QUws9c:")
    for k in reviews:
        if "hr5v-QUws9c" in k:
            print(f"  {k}")
