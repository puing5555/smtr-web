import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('_matched_reviews.json', 'r', encoding='utf-8') as f:
    reviews = json.load(f)

with open('signal-review-v3.html', 'r', encoding='utf-8') as f:
    html = f.read()

reviews_json = json.dumps(reviews, ensure_ascii=False)

embed_script = f'''<script>
(function() {{
    var KEY = 'signal-reviews-v2';
    var embedded = {reviews_json};
    var existing = {{}};
    try {{ existing = JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch(e) {{}}
    var merged = Object.assign({{}}, embedded, existing);
    localStorage.setItem(KEY, JSON.stringify(merged));
}})();
</script>
'''

html = html.replace('<script>', embed_script + '<script>', 1)

with open('signal-review-v3-final.html', 'w', encoding='utf-8') as f:
    f.write(html)

approved = sum(1 for v in reviews.values() if v.get('status') == 'approved')
rejected = sum(1 for v in reviews.values() if v.get('status') == 'rejected')
print(f'Embedded: {len(reviews)} ({approved} approved, {rejected} rejected)')
