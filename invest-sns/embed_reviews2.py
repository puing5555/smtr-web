import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# 1. Load review results backup (utf-16, broken JSON)
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
    time_match = re.search(r'"time":\s*"([^"]*)"', text[m.end():m.end()+500])
    time_val = time_match.group(1) if time_match else ""
    entry = {"status": status, "time": time_val}
    if reason:
        entry["reason"] = reason
    reviews[key] = entry

approved = sum(1 for v in reviews.values() if v.get('status') == 'approved')
rejected = sum(1 for v in reviews.values() if v.get('status') == 'rejected')
print(f'Reviews: {len(reviews)} ({approved} approved, {rejected} rejected)')

# 2. Read original HTML
with open('signal-review-v3.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 3. Create script that pre-loads localStorage
reviews_json = json.dumps(reviews, ensure_ascii=False)

embed_script = f'''<script>
// Pre-load review results from backup into localStorage
(function() {{
    var KEY = 'signal-reviews-v2';
    var embedded = {reviews_json};
    var existing = {{}};
    try {{ existing = JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch(e) {{}}
    // Merge: embedded first, then existing overrides (user's newer reviews win)
    var merged = Object.assign({{}}, embedded, existing);
    localStorage.setItem(KEY, JSON.stringify(merged));
}})();
</script>
'''

# 4. Inject right before the first <script> in body, or before </head>
# Best: inject at very start of <body> or before existing scripts
html = html.replace('<script>', embed_script + '<script>', 1)

# 5. Write
with open('signal-review-v3-final.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Output: signal-review-v3-final.html')
