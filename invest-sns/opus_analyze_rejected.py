"""Opus analysis of 5 rejected signals"""
import json, os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

rejected = json.load(open('_rejected_5.json', 'r', encoding='utf-8'))
results = {}

for sig in rejected:
    vid = sig.get('video_id', '')
    asset = sig.get('asset', '')
    sig_id = f"{vid}_{asset}"
    
    # Load subtitle
    sub_path = f'smtr_data/corinpapa1106/{vid}.txt'
    subtitle = ''
    if os.path.exists(sub_path):
        with open(sub_path, 'r', encoding='utf-8') as f:
            subtitle = f.read()[:6000]
    
    prompt = f"""유튜브 영상에서 Claude Sonnet이 추출한 시그널을 인간 리뷰어가 거부했습니다. 분석해주세요.

**Sonnet 추출 시그널:**
- 종목: {sig.get('asset', 'N/A')}
- 시그널: {sig.get('signal_type', 'N/A')}
- 내용: {sig.get('content', 'N/A')}
- 맥락: {sig.get('context', 'N/A')}
- 타임스탬프: {sig.get('timestamp', 'N/A')}
- 신뢰도: {sig.get('confidence', 'N/A')}
- 영상 제목: {sig.get('title', 'N/A')}

**영상 자막 (일부):**
{subtitle if subtitle else '(자막 없음)'}

**분석 요청:**
1. 인간이 왜 이 시그널을 거부했을지 분석
2. Sonnet의 추출 오류 원인
3. 프롬프트 개선 제안

JSON으로 답변:
{{
  "agree_with_rejection": true/false,
  "reasoning": "거부 타당성 분석 (한국어, 2-3문장)",
  "extraction_error": "Sonnet 오류 원인 (한국어, 1-2문장)",
  "prompt_fix": "프롬프트에 추가할 규칙 (한국어, 구체적)",
  "pattern": "오류 패턴 분류 (예: 일반논평_시그널화, 조건부_과대해석, 부수적언급_메인시그널화)"
}}"""

    print(f"\nAnalyzing: {asset} ({sig.get('signal_type')})...")
    
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}]
    )
    
    text = resp.content[0].text
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        result = json.loads(text[start:end])
    except:
        result = {"reasoning": text, "error": "parse_failed"}
    
    results[sig_id] = {
        "signal": {"asset": asset, "signal_type": sig.get('signal_type'), "content": sig.get('content')},
        "analysis": result
    }
    print(f"  -> {result.get('pattern', '?')}: {result.get('reasoning', '?')[:80]}")

# Save results
json.dump(results, open('_opus_rejected_analysis.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"\nDone! {len(results)} analyses saved to _opus_rejected_analysis.json")
