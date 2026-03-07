#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
signal_analyzer.py - V10.11 신호 분석
Claude Sonnet으로 자막 텍스트에서 투자 시그널 추출
"""

import json
import os
import re
import time
import anthropic

ANTHROPIC_API_KEY = "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"
PIPELINE_V10_PATH = r'C:\Users\Mario\work\prompts\pipeline_v10.md'

VALID_SIGNALS = {'매수', '긍정', '중립', '경계', '매도'}
VALID_MARKETS = {'KR', 'US', 'CRYPTO'}
VALID_CONFIDENCES = {'high', 'medium', 'low'}

_pipeline_v10_prompt = None


def load_pipeline_v10_prompt() -> str:
    """pipeline_v10.md 로드 (캐시)"""
    global _pipeline_v10_prompt
    if _pipeline_v10_prompt is None:
        try:
            with open(PIPELINE_V10_PATH, 'r', encoding='utf-8') as f:
                _pipeline_v10_prompt = f.read()
        except Exception as e:
            print(f"[분석] pipeline_v10.md 로드 실패: {e}")
            _pipeline_v10_prompt = "투자 관련 유튜브 영상 자막을 분석해서 투자 시그널을 추출하세요."
    return _pipeline_v10_prompt


def parse_signals_from_response(response_text: str) -> list[dict]:
    """API 응답에서 JSON 시그널 파싱"""
    # ```json ... ``` 블록 추출
    json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # 직접 JSON 배열 찾기
        array_match = re.search(r'(\[.*?\])', response_text, re.DOTALL)
        if array_match:
            json_str = array_match.group(1)
        else:
            return []
    
    try:
        signals = json.loads(json_str)
        if not isinstance(signals, list):
            return []
        return signals
    except json.JSONDecodeError as e:
        print(f"  [분석] JSON 파싱 오류: {e}")
        return []


def validate_signal(signal: dict) -> dict | None:
    """시그널 유효성 검증 및 정규화"""
    # 필수 필드 체크
    if not signal.get('stock') or not signal.get('signal'):
        return None
    
    # signal 값 검증
    sig = signal.get('signal', '')
    if sig not in VALID_SIGNALS:
        return None
    
    # market 검증
    market = signal.get('market', 'KR')
    if market not in VALID_MARKETS:
        market = 'KR'
    
    # confidence 검증
    confidence = signal.get('confidence', 'medium')
    if confidence not in VALID_CONFIDENCES:
        confidence = 'medium'
    
    # timestamp 정규화
    ts = signal.get('timestamp_in_video', '00:00:00')
    if not re.match(r'\d{2}:\d{2}:\d{2}', str(ts)):
        ts = '00:00:00'
    
    return {
        'speaker': str(signal.get('speaker', ''))[:100],
        'stock': str(signal.get('stock', ''))[:100],
        'ticker': signal.get('ticker'),
        'market': market,
        'signal': sig,
        'confidence': confidence,
        'timestamp_in_video': ts,
        'key_quote': str(signal.get('key_quote', ''))[:200],
        'reasoning': str(signal.get('reasoning', ''))[:300],
    }


def analyze_video(
    channel_name: str,
    video_id: str,
    title: str,
    subtitle_text: str
) -> list[dict]:
    """
    단일 영상 신호 분석.
    반환: 검증된 시그널 목록
    """
    pipeline_prompt = load_pipeline_v10_prompt()
    
    # 자막이 너무 길면 잘라냄 (API 한도 고려)
    max_subtitle_chars = 15000
    if len(subtitle_text) > max_subtitle_chars:
        subtitle_text = subtitle_text[:max_subtitle_chars] + "\n[자막 잘림]"
    
    prompt = f"""{pipeline_prompt}

채널: {channel_name}
영상 제목: {title}

[자막]
{subtitle_text}

위 자막을 분석해서 투자 시그널을 JSON 배열로 추출해줘.
형식:
[
  {{
    "speaker": "발언자명",
    "stock": "종목명",
    "ticker": "티커 또는 null",
    "market": "KR/US/CRYPTO",
    "signal": "매수/긍정/중립/경계/매도",
    "confidence": "high/medium/low",
    "timestamp_in_video": "HH:MM:SS",
    "key_quote": "핵심 발언 50자 이내",
    "reasoning": "근거 100자 이내"
  }}
]
시그널 없으면 빈 배열 [] 반환.
"""
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text
        raw_signals = parse_signals_from_response(response_text)
        
        validated = []
        for sig in raw_signals:
            v = validate_signal(sig)
            if v:
                validated.append(v)
        
        return validated
    
    except anthropic.RateLimitError as e:
        print(f"  [분석] 레이트리밋: {e}")
        raise
    except Exception as e:
        print(f"  [분석] 오류 ({video_id}): {e}")
        return []


def analyze_batch(
    channel_name: str,
    videos_with_subs: list[tuple[dict, str]],
    batch_size: int = 5
) -> dict[str, list[dict]]:
    """
    배치로 여러 영상 분석.
    videos_with_subs: [(video_dict, subtitle_text), ...]
    반환: {video_id: [signal, ...]}
    """
    results = {}
    total = len(videos_with_subs)
    
    print(f"[분석] 총 {total}개 영상 신호 분석 시작")
    
    for i, (video, subtitle_text) in enumerate(videos_with_subs):
        video_id = video['video_id']
        title = video.get('title', video_id)[:80]
        
        print(f"  [{i+1}/{total}] {video_id} - {title[:50]}")
        
        try:
            signals = analyze_video(
                channel_name=channel_name,
                video_id=video_id,
                title=title,
                subtitle_text=subtitle_text
            )
            results[video_id] = signals
            print(f"    → 시그널 {len(signals)}개 추출")
        
        except anthropic.RateLimitError:
            print(f"    → 레이트리밋 - 60초 대기 후 재시도")
            time.sleep(60)
            try:
                signals = analyze_video(channel_name, video_id, title, subtitle_text)
                results[video_id] = signals
                print(f"    → 재시도 성공: {len(signals)}개")
            except Exception as e:
                print(f"    → 재시도 실패: {e} (skip)")
                results[video_id] = []
        
        except Exception as e:
            print(f"    → 오류 (skip): {e}")
            results[video_id] = []
        
        # 배치 사이 딜레이 (레이트리밋 방지)
        if (i + 1) % batch_size == 0 and (i + 1) < total:
            print(f"  [분석] {batch_size}개 완료 - 5초 대기...")
            time.sleep(5)
        elif i + 1 < total:
            time.sleep(1)
    
    total_signals = sum(len(v) for v in results.values())
    print(f"[분석] 완료 - 총 시그널: {total_signals}개")
    return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--video-id', required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--subtitle-file', required=True)
    parser.add_argument('--channel-name', default='테스트채널')
    args = parser.parse_args()
    
    with open(args.subtitle_file, 'r', encoding='utf-8') as f:
        subtitle_text = f.read()
    
    signals = analyze_video(args.channel_name, args.video_id, args.title, subtitle_text)
    print(json.dumps(signals, ensure_ascii=False, indent=2))
