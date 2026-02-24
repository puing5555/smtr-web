import json, re

# 리뷰 백업 - utf-16 + 깨진 JSON 수리
with open('smtr_data/corinpapa1106/_review_results_backup.json', 'rb') as f:
    raw = f.read()

# Try utf-16
text = raw.decode('utf-16')
# Fix control chars
text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', text)
# Fix broken quotes - replace fancy quotes
text = text.replace('\u201c', '"').replace('\u201d', '"')
text = text.replace('\u2018', "'").replace('\u2019', "'")

# Try to parse with strict=False
try:
    reviews = json.loads(text, strict=False)
except json.JSONDecodeError as e:
    print(f"Parse error at pos {e.pos}: {repr(text[max(0,e.pos-20):e.pos+20])}")
    # Brute force: extract key-value pairs with regex
    reviews = {}
    pattern = r'"([^"]+)":\s*\{\s*"status":\s*"(approved|rejected)"'
    for m in re.finditer(pattern, text):
        key, status = m.groups()
        # Find reason if rejected
        reason = ""
        reason_match = re.search(r'"reason":\s*"([^"]*)"', text[m.end():m.end()+500])
        if reason_match:
            reason = reason_match.group(1)
        reviews[key] = {"status": status, "reason": reason}

approved = sum(1 for v in reviews.values() if v.get('status') == 'approved')
rejected = sum(1 for v in reviews.values() if v.get('status') == 'rejected')
print(f'Reviews: {len(reviews)} total, {approved} approved, {rejected} rejected')

for k, v in reviews.items():
    if v.get('status') == 'rejected':
        reason = v.get('reason', '')[:80]
        try:
            print(f'  REJECTED: {k} - {reason}')
        except:
            print(f'  REJECTED: {k} (reason has encoding issue)')

# Opus results
try:
    with open('_opus_review_results.json', 'rb') as f:
        raw2 = f.read()
    text2 = raw2.decode('utf-16') if raw2[:2] in (b'\xff\xfe', b'\xfe\xff') else raw2.decode('utf-8-sig')
    text2 = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', text2)
    opus = json.loads(text2, strict=False)
    print(f'\nOpus: {len(opus)} results')
    for k, v in opus.items():
        verdict = v.get('verdict', '?')
        print(f'  {k}: {verdict}')
except Exception as e:
    print(f'Opus error: {e}')

# Save clean reviews as utf-8 for embedding
with open('_clean_reviews.json', 'w', encoding='utf-8') as f:
    json.dump(reviews, f, ensure_ascii=False, indent=2)
print('\nSaved _clean_reviews.json')
