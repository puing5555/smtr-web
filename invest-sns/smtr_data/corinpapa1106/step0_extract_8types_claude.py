#!/usr/bin/env python3
"""
8개 시그널 타입으로 유튜브 자막에서 투자 시그널 재추출
Anthropic Claude API 사용
"""
import json
import os
import glob
import time
import anthropic

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
2. 단순 정보 전달이나 뉴스 읽기는 제외 (NEUTRAL은 의미있는 분석이 있을 때만)
3. 가격 목표 언급 시 매수/매도 맥락에 따라 적절한 시그널 타입 부여
4. 같은 종목이 여러 번 언급되면 가장 강한 시그널 하나만 추출
5. 시그널이 없으면 빈 배열 반환: {{"signals": []}}
6. 반드시 valid JSON만 출력하세요. 다른 텍스트 없이 JSON만."""


def extract_signals_from_subtitle(client, video_id, subtitle, title, channel):
    """단일 자막에서 시그널 추출"""
    user_msg = f"유튜버: {channel}\n영상 제목: {title}\n영상 ID: {video_id}\n\n=== 자막 ===\n{subtitle}"
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}]
    )
    
    text = response.content[0].text.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    
    return json.loads(text)


def main():
    subtitle_dir = os.path.dirname(os.path.abspath(__file__))
    client = anthropic.Anthropic()
    
    # Load video metadata
    videos_meta = {}
    videos_path = os.path.join(subtitle_dir, "_all_videos.json")
    if os.path.exists(videos_path):
        with open(videos_path, 'r', encoding='utf-8') as f:
            for v in json.load(f):
                vid = v.get('video_id') or v.get('id', '')
                videos_meta[vid] = v
    
    # Get subtitle files
    txt_files = sorted(glob.glob(os.path.join(subtitle_dir, "*.txt")))
    txt_files = [f for f in txt_files if not os.path.basename(f).startswith('_')]
    
    # Load progress if exists
    progress_path = os.path.join(subtitle_dir, "_extract_8types_progress.json")
    all_signals = []
    done_ids = set()
    if os.path.exists(progress_path):
        with open(progress_path, 'r', encoding='utf-8') as f:
            progress = json.load(f)
            all_signals = progress.get("signals", [])
            done_ids = set(progress.get("done_ids", []))
        print(f"Resuming: {len(done_ids)} already done, {len(all_signals)} signals so far")
    
    print(f"Processing {len(txt_files)} subtitle files...")
    
    for i, txt_path in enumerate(txt_files):
        video_id = os.path.splitext(os.path.basename(txt_path))[0]
        
        if video_id in done_ids:
            continue
        
        with open(txt_path, 'r', encoding='utf-8') as f:
            subtitle = f.read()
        
        if len(subtitle.strip()) < 50:
            done_ids.add(video_id)
            continue
        
        meta = videos_meta.get(video_id, {})
        title = meta.get('title', video_id)
        channel = meta.get('channel', '코린이 아빠')
        
        try:
            result = extract_signals_from_subtitle(client, video_id, subtitle, title, channel)
            signals = result.get("signals", [])
            for sig in signals:
                sig["video_id"] = video_id
                sig["channel"] = channel
                sig["title"] = title
            all_signals.extend(signals)
            done_ids.add(video_id)
            print(f"  [{len(done_ids)}/{len(txt_files)}] {video_id}: {len(signals)} signals ({title[:40]})")
            
            # Save progress every 5 videos
            if len(done_ids) % 5 == 0:
                with open(progress_path, 'w', encoding='utf-8') as f:
                    json.dump({"signals": all_signals, "done_ids": list(done_ids)}, f, ensure_ascii=False, indent=2)
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ERROR {video_id}: {e}")
            time.sleep(2)
            continue
    
    # Save final results
    output_path = os.path.join(subtitle_dir, "_all_signals_8types.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_signals, f, ensure_ascii=False, indent=2)
    
    # Save progress
    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump({"signals": all_signals, "done_ids": list(done_ids)}, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal signals: {len(all_signals)}")
    from collections import Counter
    types = Counter(s.get('signal_type', '?') for s in all_signals)
    print(f"Types: {dict(types)}")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
