import json, re

with open('signal-review-v3.html', encoding='utf-8') as f:
    html = f.read()

# Extract SIGNALS_DATA
m = re.search(r'const SIGNALS_DATA = (\[.*?\]);\s*\n', html, re.DOTALL)
data = json.loads(m.group(1))

# 5 rejected signals
rejected_specs = [
    ('oC-mHWKj8m8', 'BMNR'),
    ('hr5v-QUws9c', None),  # 캐톤네트워크 CC - only signal
    ('axurZUkC5Dc', '이더리움'),
    ('2wdlIAF0OrA', 'NVDA'),
    ('2wdlIAF0OrA', 'PLTR'),
]

def is_rejected(vid, asset):
    for rv, hint in rejected_specs:
        if vid == rv:
            if hint is None:
                return True
            if hint in asset:
                return True
    return False

# Build complete review state for all 177 signals
reviews = {}
for s in data:
    key = s['video_id'] + '_' + s['asset']
    if is_rejected(s['video_id'], s['asset']):
        reviews[key] = {"status": "rejected", "time": "Opus review", "reason": "Opus 자동 검토에서 거부"}
    else:
        reviews[key] = {"status": "approved", "time": "Opus review"}

rejected_count = sum(1 for v in reviews.values() if v['status'] == 'rejected')
approved_count = sum(1 for v in reviews.values() if v['status'] == 'approved')
print(f"Total: {len(reviews)}, Approved: {approved_count}, Rejected: {rejected_count}")
assert rejected_count == 5
assert approved_count == 172

reviews_json = json.dumps(reviews, ensure_ascii=False)

# Remove old injection if present
html = re.sub(r'\n\s*// Auto-fix: ensure 5 rejected.*?\}\)\(\);\n', '\n', html, flags=re.DOTALL)

# New injection: completely replace localStorage reviews
injection = f"""
        // Force-set all review states (172 approved, 5 rejected)
        (function() {{
            var correctReviews = {reviews_json};
            localStorage.setItem('signal-reviews-v2', JSON.stringify(correctReviews));
        }})();
"""

target = "        document.addEventListener('DOMContentLoaded', function() {"
html = html.replace(target, injection + target, 1)

with open('signal-review-v3.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done! Full review state injected into v3.")
