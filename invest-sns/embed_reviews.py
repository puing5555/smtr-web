import json, re, sys

# 1. Load review results
with open('smtr_data/corinpapa1106/_review_results_backup.json', 'rb') as f:
    raw = f.read()
text = raw.decode('utf-16')
text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', text)

reviews = {}
pattern = r'"([^"]+)":\s*\{\s*"status":\s*"(approved|rejected)"'
for m in re.finditer(pattern, text):
    key, status = m.groups()
    reason = ""
    reason_match = re.search(r'"reason":\s*"([^"]*)"', text[m.end():m.end()+500])
    if reason_match:
        reason = reason_match.group(1)
    reviews[key] = {"status": status, "reason": reason}

# 2. Load opus results
try:
    with open('_opus_review_results.json', 'rb') as f:
        raw2 = f.read()
    text2 = raw2.decode('utf-16') if raw2[:2] in (b'\xff\xfe', b'\xfe\xff') else raw2.decode('utf-8-sig')
    text2 = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', text2)
    opus = json.loads(text2, strict=False)
except:
    opus = {}

# 3. Read HTML
with open('signal-review-v3.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 4. Create embedded data script
reviews_json = json.dumps(reviews, ensure_ascii=False)
opus_json = json.dumps(opus, ensure_ascii=False)

embed_script = f'''<script>
// Embedded review data (restored from backup)
window.EMBEDDED_REVIEWS = {reviews_json};
window.EMBEDDED_OPUS = {opus_json};

// Override fetch to return embedded data
const _originalFetch = window.fetch;
window.fetch = function(url, options) {{
    if (typeof url === 'string') {{
        if (url.includes('/api/reviews') && (!options || options.method === 'GET' || !options.method)) {{
            return Promise.resolve(new Response(JSON.stringify(window.EMBEDDED_REVIEWS), {{
                status: 200, headers: {{'Content-Type': 'application/json'}}
            }}));
        }}
        if (url.includes('/api/opus') && (!options || options.method === 'GET' || !options.method)) {{
            return Promise.resolve(new Response(JSON.stringify(window.EMBEDDED_OPUS), {{
                status: 200, headers: {{'Content-Type': 'application/json'}}
            }}));
        }}
        // For POST/save requests, store in localStorage
        if (url.includes('/api/review') && options && options.method === 'POST') {{
            try {{
                const body = JSON.parse(options.body);
                const stored = JSON.parse(localStorage.getItem('signal_reviews') || '{{}}');
                Object.assign(stored, body);
                localStorage.setItem('signal_reviews', JSON.stringify(stored));
                Object.assign(window.EMBEDDED_REVIEWS, body);
            }} catch(e) {{}}
            return Promise.resolve(new Response(JSON.stringify({{success: true}}), {{
                status: 200, headers: {{'Content-Type': 'application/json'}}
            }}));
        }}
    }}
    return _originalFetch.apply(this, arguments);
}};

// Merge localStorage reviews on load
document.addEventListener('DOMContentLoaded', function() {{
    try {{
        const stored = JSON.parse(localStorage.getItem('signal_reviews') || '{{}}');
        Object.assign(window.EMBEDDED_REVIEWS, stored);
    }} catch(e) {{}}
}});
</script>
'''

# 5. Inject before </head>
html = html.replace('</head>', embed_script + '</head>')

# 6. Write output
with open('signal-review-v3-embedded.html', 'w', encoding='utf-8') as f:
    f.write(html)

approved = sum(1 for v in reviews.values() if v.get('status') == 'approved')
rejected = sum(1 for v in reviews.values() if v.get('status') == 'rejected')
sys.stdout.reconfigure(encoding='utf-8')
print(f'Done! Reviews embedded: {len(reviews)} ({approved} approved, {rejected} rejected)')
print(f'Opus embedded: {len(opus)} results')
print(f'Output: signal-review-v3-embedded.html')
