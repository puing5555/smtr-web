import json, re

# Load the correct review state
v5 = json.load(open("_review_results_v5.json", "r", encoding="utf-8"))

# Read embedded HTML
with open("signal-review-v4-embedded.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find where review state is stored in the HTML
# Look for patterns like: "status":"approved" or "status":"rejected" or "status":"pending"
# Also check for reviewState or similar embedded data

# Count current statuses
approved_before = html.count('"status":"approved"') + html.count("'status':'approved'") + html.count('"status": "approved"')
rejected_before = html.count('"status":"rejected"') + html.count("'status':'rejected'") + html.count('"status": "rejected"')
pending_before = html.count('"status":"pending"') + html.count("'status':'pending'") + html.count('"status": "pending"')
print(f"Before - approved: {approved_before}, rejected: {rejected_before}, pending: {pending_before}")

# Find the embedded review data section
# Look for review objects with status field
# The reviews are likely stored as a JS object

# Find lines with review status assignments
lines = html.split('\n')
review_lines = []
for i, line in enumerate(lines):
    if '"status"' in line and ('approved' in line or 'rejected' in line or 'pending' in line):
        review_lines.append((i, line.strip()[:100]))

print(f"\nFound {len(review_lines)} lines with status")
if review_lines:
    print("First 5:", review_lines[:5])
    print("Last 5:", review_lines[-5:])

# Let's look for the review data structure
for i, line in enumerate(lines):
    if 'reviewData' in line or 'REVIEW_STATE' in line or 'reviewState' in line:
        print(f"\nLine {i}: {line.strip()[:150]}")
