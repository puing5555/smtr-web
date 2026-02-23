import json, sys, anthropic, time
sys.stdout.reconfigure(encoding='utf-8')

with open(r'invest-sns\smtr_data\corinpapa1106\_deduped_signals_8types_dated.json', 'r', encoding='utf-8') as f:
    sigs = json.load(f)

# Find English titles
eng_titles = set()
for s in sigs:
    t = s.get('title', '')
    if t and any(c.isascii() and c.isalpha() for c in t[:5]):
        # Check if mostly English
        ascii_count = sum(1 for c in t if c.isascii())
        if ascii_count / max(len(t),1) > 0.5:
            eng_titles.add(t)

print(f"English titles to translate: {len(eng_titles)}")

if not eng_titles:
    print("No English titles found")
    sys.exit(0)

client = anthropic.Anthropic()
translations = {}

# Batch translate
titles_list = list(eng_titles)
batch_size = 20
for i in range(0, len(titles_list), batch_size):
    batch = titles_list[i:i+batch_size]
    prompt = "다음 영어 유튜브 영상 제목들을 자연스러운 한국어로 번역해주세요. JSON 형식으로 {\"원본\": \"번역\"} 으로 출력하세요.\n\n"
    for t in batch:
        prompt += f"- {t}\n"
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    text = response.content[0].text.strip()
    if text.startswith('```'):
        text = text.split('\n',1)[1].rsplit('```',1)[0].strip()
    
    try:
        result = json.loads(text)
        translations.update(result)
        print(f"Translated batch {i//batch_size + 1}: {len(result)} titles")
    except:
        print(f"Failed to parse batch {i//batch_size + 1}")
        print(text[:200])
    
    time.sleep(0.5)

print(f"\nTotal translations: {len(translations)}")

# Apply to both files
for fname in ['_deduped_signals_8types_dated.json', '_all_signals_8types.json']:
    path = f'invest-sns/smtr_data/corinpapa1106/{fname}'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count = 0
    for s in data:
        t = s.get('title', '')
        if t in translations:
            s['title'] = translations[t]
            count += 1
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"{fname}: updated {count} titles")
