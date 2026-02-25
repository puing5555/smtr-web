import json, re

with open('signal-review-v3.html', encoding='utf-8') as f:
    html = f.read()

# Extract SIGNALS_DATA to find exact keys
m = re.search(r'const SIGNALS_DATA = (\[.*?\]);\s*\n', html, re.DOTALL)
data = json.loads(m.group(1))

# Build lookup: video_id -> list of assets
vid_assets = {}
for s in data:
    vid_assets.setdefault(s['video_id'], []).append(s['asset'])

# The 5 rejected: find exact asset names
rejected_specs = [
    ('oC-mHWKj8m8', 'BMNR'),
    ('hr5v-QUws9c', None),  # only one signal in this video
    ('axurZUkC5Dc', '이더리움'),
    ('2wdlIAF0OrA', 'NVDA'),
    ('2wdlIAF0OrA', 'PLTR'),
]

rejected_keys = []
for vid, hint in rejected_specs:
    assets = vid_assets.get(vid, [])
    for asset in assets:
        if hint is None:
            rejected_keys.append(vid + '_' + asset)
            break
        elif hint in asset:
            rejected_keys.append(vid + '_' + asset)
            break

print("Rejected keys:", rejected_keys)
assert len(rejected_keys) == 5, f"Expected 5, got {len(rejected_keys)}"

# Build JS injection: on DOMContentLoaded, force these 5 to rejected in localStorage
js_obj = {}
for k in rejected_keys:
    js_obj[k] = {"status": "rejected", "time": "Opus review", "reason": "Opus 자동 검토에서 거부"}

js_json = json.dumps(js_obj, ensure_ascii=False)

injection = f"""
        // Auto-fix: ensure 5 rejected signals are correctly set
        (function() {{
            var forced = {js_json};
            var r = JSON.parse(localStorage.getItem('signal-reviews-v2') || '{{}}');
            var changed = false;
            Object.keys(forced).forEach(function(k) {{
                if (!r[k] || r[k].status !== 'rejected') {{
                    r[k] = forced[k];
                    changed = true;
                }}
            }});
            if (changed) {{
                localStorage.setItem('signal-reviews-v2', JSON.stringify(r));
                console.log('Fixed rejected signals in localStorage');
            }}
        }})();
"""

# Inject before the DOMContentLoaded listener
target = "        document.addEventListener('DOMContentLoaded', function() {"
html = html.replace(target, injection + target, 1)

with open('signal-review-v3.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done! Injected fix into signal-review-v3.html")
