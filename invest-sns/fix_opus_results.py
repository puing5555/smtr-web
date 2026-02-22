"""Fix opus4 analysis results by re-parsing raw_response"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('smtr_data/corinpapa1106/_opus4_analysis.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixed = 0
for k, v in data.items():
    raw = v.get('raw_response', '')
    if not raw:
        continue
    
    # Try to extract key fields from raw text
    result = {}
    
    # sonnet_signal_correct
    m = re.search(r'"sonnet_signal_correct"\s*:\s*(true|false)', raw)
    if m:
        result['sonnet_accurate'] = m.group(1) == 'true'
    
    # rejection_valid
    m = re.search(r'"rejection_valid"\s*:\s*(true|false)', raw)
    if m:
        result['rejection_valid'] = m.group(1) == 'true'
    
    # correct_signal block
    m = re.search(r'"signal_type"\s*:\s*"([^"]*)"', raw)
    if m:
        result['correct_signal'] = m.group(1)
    
    m = re.search(r'"correct_signal".*?"asset"\s*:\s*"([^"]*)"', raw, re.DOTALL)
    if m:
        result['correct_asset'] = m.group(1)
    
    m = re.search(r'"correct_signal".*?"content"\s*:\s*"([^"]*)"', raw, re.DOTALL)
    if m:
        result['correct_content'] = m.group(1)[:200]
    
    m = re.search(r'"correct_signal".*?"timestamp"\s*:\s*"([^"]*)"', raw, re.DOTALL)
    if m:
        result['correct_timestamp'] = m.group(1)
    
    # prompt_improvement
    m = re.search(r'"prompt_improvement"\s*:\s*"([^"]*)"', raw)
    if m:
        result['prompt_improvement'] = m.group(1)
    
    # analysis - extract from raw text
    m = re.search(r'"analysis"\s*:\s*["{](.*?)["}]\s*[,}]', raw, re.DOTALL)
    if m:
        result['analysis'] = m.group(1)[:500]
    
    if result:
        v['result'] = result
        v['status'] = 'complete'
        fixed += 1
        print(f'Fixed: {k}')
        print(f'  Sonnet correct: {result.get("sonnet_accurate", "?")}')
        print(f'  Rejection valid: {result.get("rejection_valid", "?")}')
        print(f'  Correct signal: {result.get("correct_signal", "?")}')
        print(f'  Correct asset: {result.get("correct_asset", "?")}')
        print()

with open('smtr_data/corinpapa1106/_opus4_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\nFixed {fixed}/{len(data)} entries')
