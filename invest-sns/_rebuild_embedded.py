import json, re

# The 5 rejected video_id + asset pairs
REJECTED_5 = [
    ("oC-mHWKj8m8", "BMNR"),
    ("hr5v-QUws9c", "CC"),
    ("axurZUkC5Dc", "\uc774\ub354\ub9ac\uc6c0"),  # 이더리움
    ("2wdlIAF0OrA", "NVDA"),
    ("2wdlIAF0OrA", "PLTR"),
]

with open("signal-review-v4-embedded.html", "r", encoding="utf-8") as f:
    html = f.read()

lines = html.split('\n')

# Find the embedded review/signal data block
# The signals are in a big JS array, each with "status" field
# We need to find each signal object and check video_id + asset to determine if rejected

# Strategy: find all "status": "approved"/"rejected" lines and their context
# Each signal block has video_id and asset nearby

changed = 0
i = 0
while i < len(lines):
    line = lines[i]
    if '"status":' in line and ('approved' in line or 'rejected' in line):
        # Look backwards for video_id and asset/stockName
        context = '\n'.join(lines[max(0,i-20):i+5])
        
        # Check if this should be rejected
        should_reject = False
        for vid, asset in REJECTED_5:
            if vid in context and asset in context:
                should_reject = True
                break
        
        current_rejected = '"rejected"' in line
        
        if should_reject and not current_rejected:
            lines[i] = line.replace('"approved"', '"rejected"')
            changed += 1
            print(f"Line {i}: approved -> rejected")
        elif not should_reject and current_rejected:
            lines[i] = line.replace('"rejected"', '"approved"')
            changed += 1
            print(f"Line {i}: rejected -> approved")
    i += 1

print(f"\nChanged {changed} lines")

# Verify counts
new_html = '\n'.join(lines)
new_approved = new_html.count('"status": "approved"')
new_rejected = new_html.count('"status": "rejected"')
print(f"After: approved={new_approved}, rejected={new_rejected}, total={new_approved+new_rejected}")

if new_approved == 172 and new_rejected == 5:
    with open("signal-review-v4-embedded.html", "w", encoding="utf-8") as f:
        f.write(new_html)
    print("File saved!")
else:
    print(f"WARNING: Expected 172/5 but got {new_approved}/{new_rejected}, NOT saving")
    # Debug: show what's currently rejected
    for i, line in enumerate(lines):
        if '"status": "rejected"' in line:
            ctx = '\n'.join(lines[max(0,i-10):i+1])
            vid_match = re.search(r'"video_id":\s*"([^"]+)"', ctx)
            asset_match = re.search(r'"asset":\s*"([^"]+)"', ctx)
            print(f"  Rejected at line {i}: vid={vid_match.group(1) if vid_match else '?'} asset={asset_match.group(1) if asset_match else '?'}")
