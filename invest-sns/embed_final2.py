import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('_matched_reviews.json', 'r', encoding='utf-8') as f:
    reviews = json.load(f)

with open('signal-review-v3.html', 'r', encoding='utf-8') as f:
    html = f.read()

reviews_json = json.dumps(reviews, ensure_ascii=False)

# Replace loadReviews to merge embedded + localStorage
old_load = """function loadReviews() {
            try { return JSON.parse(localStorage.getItem('signal-reviews-v2') || '{}'); }
            catch(e) { return {}; }
        }"""

new_load = f"""function loadReviews() {{
            var embedded = {reviews_json};
            try {{
                var stored = JSON.parse(localStorage.getItem('signal-reviews-v2') || '{{}}');
                // Merge: embedded first, stored overrides
                var merged = Object.assign({{}}, embedded, stored);
                return merged;
            }} catch(e) {{ return embedded; }}
        }}"""

html = html.replace(old_load, new_load)

with open('signal-review-v3-final.html', 'w', encoding='utf-8') as f:
    f.write(html)

approved = sum(1 for v in reviews.values() if v.get('status') == 'approved')
rejected = sum(1 for v in reviews.values() if v.get('status') == 'rejected')
print(f'Done! {len(reviews)} reviews embedded ({approved} approved, {rejected} rejected)')
