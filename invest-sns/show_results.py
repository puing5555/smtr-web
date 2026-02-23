import json

r = json.load(open('_opus_rejected_analysis.json', 'r', encoding='utf-8'))
for sid, data in r.items():
    sig = data['signal']
    a = data['analysis']
    print(f"=== {sig['asset']} ({sig['signal_type']}) ===")
    print(f"Pattern: {a.get('pattern', '?')}")
    print(f"Reasoning: {a.get('reasoning', '?')}")
    print(f"Error: {a.get('extraction_error', '?')}")
    print(f"Fix: {a.get('prompt_fix', '?')}")
    print(f"Agree: {a.get('agree_with_rejection', '?')}")
    print()
