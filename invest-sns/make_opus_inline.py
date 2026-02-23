import json

r = json.load(open('_opus_rejected_analysis.json', 'r', encoding='utf-8'))
out = {}
for sid, data in r.items():
    a = data['analysis']
    out[sid] = {
        'agree_with_rejection': a.get('agree_with_rejection', True),
        'reasoning': a.get('reasoning', ''),
        'extraction_error': a.get('extraction_error', ''),
        'prompt_fix': a.get('prompt_fix', ''),
        'pattern': a.get('pattern', '')
    }

with open('_opus_inline.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False)
print("Done:", len(out), "results")
