import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('smtr_data/corinpapa1106/_opus4_analysis.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for k, v in d.items():
    r = v.get('result', {})
    print(f'=== {k} ===')
    print(f'  Sonnet 정확: {r.get("sonnet_accurate", "?")}')
    print(f'  거부 타당: {r.get("rejection_valid", "?")}')
    print(f'  제안 시그널: {r.get("correct_signal", "?")}')
    print(f'  제안 종목: {r.get("correct_asset", "?")}')
    analysis = str(r.get('analysis', ''))[:200]
    print(f'  분석: {analysis}')
    suggestion = str(r.get('prompt_improvement', ''))[:150]
    print(f'  프롬프트 제안: {suggestion}')
    print()
