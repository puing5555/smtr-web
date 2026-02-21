#!/usr/bin/env python3
"""
8개 시그널 타입으로 유튜브 자막에서 투자 시그널 재추출
OpenAI Batch API 사용 (GPT-4o-mini)
"""
import json
import os
import glob
from openai import OpenAI

SIGNAL_TYPES = """
시그널 타입 (반드시 아래 8개 중 하나만 사용):

1. STRONG_BUY - 강력매수: "지금 당장 사야 한다", "올인해야 한다" 등 매우 강한 매수 추천
2. BUY - 매수: "사는 게 좋다", "매수 추천", "들어가도 된다" 등 일반적 매수 추천  
3. POSITIVE - 긍정: "전망이 좋다", "성장 가능성 있다" 등 긍정적 전망 (매수 추천 없이)
4. HOLD - 보유: "지금은 들고 있어라", "팔지 마라" 등 보유 추천
5. NEUTRAL - 중립: 단순 정보 전달, 시장 분석, 교육 목적 (방향성 없음)
6. CONCERN - 우려: "주의해야 한다", "리스크가 있다" 등 부정적 전망 (매도 추천 없이)
7. SELL - 매도: "팔아라", "빠져라", "손절해라" 등 일반적 매도 추천
8. STRONG_SELL - 강력매도: "당장 던져라", "절대 들고 있으면 안 된다" 등 매우 강한 매도 추천

주의사항:
- PRICE_TARGET(가격 목표)은 시그널 타입이 아닙니다. 가격 목표가 언급되면 맥락에 따라 위 8개 중 적절한 것을 선택하세요.
- MARKET_VIEW(시장 전망)도 시그널 타입이 아닙니다. 위 8개 중 선택하세요.
- 단순히 가격이나 수치를 언급하는 것만으로는 시그널이 아닙니다. 화자의 의견/추천이 있어야 합니다.
"""

SYSTEM_PROMPT = f"""당신은 유튜브 투자 채널의 자막을 분석하여 투자 시그널을 추출하는 전문가입니다.

{SIGNAL_TYPES}

각 시그널에 대해 다음 JSON 형식으로 추출하세요:
{{
  "signals": [
    {{
      "asset": "종목명 (영문 티커 또는 공식 명칭)",
      "signal_type": "위 8개 타입 중 하나 (대문자)",
      "content": "화자의 핵심 발언 (원문 인용, 한국어)",
      "confidence": "HIGH/MEDIUM/LOW",
      "context": "발언의 맥락 설명 (한국어)",
      "timestamp": "자막의 타임스탬프 [M:SS] 형식"
    }}
  ]
}}

규칙:
1. 화자가 특정 종목/코인/자산에 대해 명확한 의견을 표현한 경우만 추출
2. 단순 정보 전달이나 뉴스 읽기는 NEUTRAL로 분류하되, 의미있는 것만 추출
3. 가격 목표 언급 시 매수/매도 맥락에 따라 적절한 시그널 타입 부여
4. 같은 종목이 여러 번 언급되면 가장 강한 시그널 하나만 추출
5. 시그널이 없으면 빈 배열 반환: {{"signals": []}}
"""

def build_batch_requests(subtitle_dir):
    """자막 파일들로 배치 요청 생성"""
    requests = []
    txt_files = sorted(glob.glob(os.path.join(subtitle_dir, "*.txt")))
    
    # Load video metadata if available
    videos_meta = {}
    videos_path = os.path.join(subtitle_dir, "_all_videos.json")
    if os.path.exists(videos_path):
        with open(videos_path, 'r', encoding='utf-8') as f:
            for v in json.load(f):
                vid = v.get('video_id') or v.get('id', '')
                videos_meta[vid] = v
    
    for txt_path in txt_files:
        video_id = os.path.splitext(os.path.basename(txt_path))[0]
        if video_id.startswith('_'):
            continue  # Skip non-subtitle files
            
        with open(txt_path, 'r', encoding='utf-8') as f:
            subtitle = f.read()
        
        if len(subtitle.strip()) < 50:
            continue
            
        meta = videos_meta.get(video_id, {})
        title = meta.get('title', video_id)
        channel = meta.get('channel', '코린이 아빠')
        
        user_msg = f"유튜버: {channel}\n영상 제목: {title}\n영상 ID: {video_id}\n\n=== 자막 ===\n{subtitle}"
        
        request = {
            "custom_id": f"extract_{video_id}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
        }
        requests.append(request)
    
    return requests

def submit_batch(requests, subtitle_dir):
    """배치 API 제출"""
    client = OpenAI()
    
    # Write JSONL
    batch_input_path = os.path.join(subtitle_dir, "_batch_extract_8types.jsonl")
    with open(batch_input_path, 'w', encoding='utf-8') as f:
        for req in requests:
            f.write(json.dumps(req, ensure_ascii=False) + '\n')
    
    print(f"Created batch input: {len(requests)} requests")
    
    # Upload
    with open(batch_input_path, 'rb') as f:
        file_obj = client.files.create(file=f, purpose="batch")
    print(f"Uploaded file: {file_obj.id}")
    
    # Submit batch
    batch = client.batches.create(
        input_file_id=file_obj.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": "8-type signal extraction from YouTube subtitles"}
    )
    
    # Save batch info
    info_path = os.path.join(subtitle_dir, "_batch_extract_8types_info.json")
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump({
            "batch_id": batch.id,
            "input_file_id": file_obj.id,
            "status": batch.status,
            "created_at": batch.created_at,
            "request_count": len(requests)
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Batch submitted: {batch.id}")
    print(f"Status: {batch.status}")
    return batch

def check_batch(subtitle_dir):
    """배치 상태 확인 및 결과 다운로드"""
    client = OpenAI()
    
    info_path = os.path.join(subtitle_dir, "_batch_extract_8types_info.json")
    with open(info_path, 'r', encoding='utf-8') as f:
        info = json.load(f)
    
    batch = client.batches.retrieve(info["batch_id"])
    print(f"Batch {batch.id}: {batch.status}")
    print(f"Progress: {batch.request_counts}")
    
    if batch.status == "completed":
        # Download results
        result_file = client.files.content(batch.output_file_id)
        result_path = os.path.join(subtitle_dir, "_batch_extract_8types_result.jsonl")
        with open(result_path, 'wb') as f:
            f.write(result_file.content)
        print(f"Results saved to {result_path}")
        
        # Parse results
        all_signals = []
        with open(result_path, 'r', encoding='utf-8') as f:
            for line in f:
                result = json.loads(line)
                video_id = result["custom_id"].replace("extract_", "")
                response = result["response"]["body"]["choices"][0]["message"]["content"]
                try:
                    parsed = json.loads(response)
                    signals = parsed.get("signals", [])
                    for sig in signals:
                        sig["video_id"] = video_id
                    all_signals.extend(signals)
                    print(f"  {video_id}: {len(signals)} signals")
                except json.JSONDecodeError as e:
                    print(f"  {video_id}: JSON parse error: {e}")
        
        # Save all signals
        output_path = os.path.join(subtitle_dir, "_all_signals_8types.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_signals, f, ensure_ascii=False, indent=2)
        
        print(f"\nTotal signals extracted: {len(all_signals)}")
        from collections import Counter
        types = Counter(s.get('signal_type', '?') for s in all_signals)
        print(f"Signal types: {dict(types)}")
        
        return all_signals
    
    return None

if __name__ == "__main__":
    import sys
    subtitle_dir = os.path.dirname(os.path.abspath(__file__))
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_batch(subtitle_dir)
    else:
        requests = build_batch_requests(subtitle_dir)
        print(f"Found {len(requests)} subtitle files to process")
        submit_batch(requests, subtitle_dir)
