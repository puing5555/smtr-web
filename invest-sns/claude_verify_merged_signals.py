"""
합친 시그널 161개에 대한 Claude 검증
- 1영상 1종목 1시그널로 합친 결과 검증
- 타임스탬프 추출 포함
"""
import json
import os
import sys
import io
import re
from datetime import datetime
from anthropic import Anthropic

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def setup_anthropic_client():
    """Anthropic 클라이언트 설정"""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY 환경변수가 없습니다.")
        return None
    
    try:
        client = Anthropic(api_key=api_key)
        print("✅ Anthropic 클라이언트 초기화 완료")
        return client
    except Exception as e:
        print(f"❌ Anthropic 클라이언트 초기화 실패: {e}")
        return None

def load_merged_signals():
    """합친 시그널 로드"""
    signal_file = 'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\_merged_signals_only.json'
    
    try:
        with open(signal_file, 'r', encoding='utf-8') as f:
            signals = json.load(f)
        
        print(f"✅ 합친 시그널 로드: {len(signals)}개")
        return signals
    except Exception as e:
        print(f"❌ 합친 시그널 로드 실패: {e}")
        return None

def load_subtitle(video_id):
    """특정 비디오의 자막 로드"""
    subtitle_paths = [
        f'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\{video_id}.txt',
        f'C:\\Users\\Mario\\.openclaw\\workspace\\smtr_data\\corinpapa1106\\{video_id}.txt'
    ]
    
    for subtitle_path in subtitle_paths:
        if os.path.exists(subtitle_path):
            try:
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
            except Exception as e:
                continue
    
    return None

def extract_timestamp_from_subtitle(subtitle_text, quote_text):
    """자막에서 인용문에 해당하는 타임스탬프 찾기"""
    if not subtitle_text or not quote_text:
        return None
    
    # 간단한 문자열 매칭으로 타임스탬프 찾기
    quote_words = quote_text.split()[:5]  # 처음 5단어로 검색
    search_text = ' '.join(quote_words)
    
    # 타임스탬프 패턴
    timestamp_pattern = r'(\d{1,2}:\d{2}(?::\d{2})?)'
    lines = subtitle_text.split('\n')
    
    for i, line in enumerate(lines):
        if search_text in line:
            # 주변 라인에서 타임스탬프 찾기
            for j in range(max(0, i-3), min(len(lines), i+4)):
                timestamps = re.findall(timestamp_pattern, lines[j])
                if timestamps:
                    return convert_timestamp_to_seconds(timestamps[-1])
    
    return None

def convert_timestamp_to_seconds(timestamp_str):
    """타임스탬프를 초로 변환"""
    try:
        parts = timestamp_str.split(':')
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        pass
    return None

def create_claude_prompt():
    """Claude 검증용 프롬프트"""
    return """당신은 투자 유튜브 영상에서 추출된 투자 시그널을 검증하는 전문가입니다.

## 중요: 이 시그널은 여러 중복 시그널을 합친 결과입니다
- 1영상 1종목 1시그널 원칙으로 통합됨
- 여러 시그널이 하나로 합쳐져서 복합적일 수 있음
- 최종 결정된 시그널 타입과 대표 인용구 확인 필요

## 시그널 분류 기준
- **STRONG_BUY**: 매우 강한 매수 추천
- **BUY**: 명시적 매수 행동/추천
- **POSITIVE**: 긍정적 전망 (매수 추천은 아님)
- **HOLD**: 보유 유지
- **NEUTRAL**: 중립적 분석
- **CONCERN**: 우려/주의
- **SELL**: 명시적 매도
- **STRONG_SELL**: 매우 강한 매도

## 검증 기준
1. **종목명**: 자막에서 실제 언급되는가?
2. **시그널**: 합친 최종 시그널이 자막 전체 맥락과 일치하는가?
3. **인용문**: 선택된 대표 인용구가 적절한가?
4. **일관성**: 합친 결과가 전체적으로 일관성 있는가?

## 응답 형식 (JSON만)
```json
{
  "verdict": "confirmed" | "corrected" | "rejected",
  "confidence": 0.0-1.0,
  "reason": "판단 근거를 상세히 설명",
  "corrected_asset": "종목명 수정이 필요한 경우만",
  "corrected_signal": "시그널 수정이 필요한 경우만",
  "merge_assessment": "합치기 결과가 적절한지 평가"
}
```

자막 내용과 합친 시그널의 일치성을 중심으로 검증해주세요."""

def verify_merged_signal_with_claude(client, signal, signal_index):
    """Claude로 합친 시그널 검증"""
    
    prompt = create_claude_prompt()
    video_id = signal.get('video_id', '')
    
    # 자막 로드
    subtitle = load_subtitle(video_id)
    if not subtitle:
        return {
            "verdict": "error",
            "confidence": 0.0,
            "reason": "자막 파일 없음",
            "merge_assessment": "자막이 없어서 평가 불가"
        }
    
    # 자막 길이 제한
    if len(subtitle) > 8000:
        subtitle = subtitle[:8000] + "\n\n[자막 일부만 표시]"
    
    # 합친 시그널 정보 구성
    merge_info = ""
    if signal.get('merged_from_count', 1) > 1:
        original_signals = signal.get('original_signals', [])
        merge_info = f"""
## 합치기 정보
- **합쳐진 개수**: {signal.get('merged_from_count')}개
- **원본 시그널들**: {', '.join([s.get('signal_type', 'N/A') for s in original_signals])}
- **최종 선택**: {signal.get('signal_type')}
"""
    
    user_message = f"""## 원본 자막
{subtitle}

{merge_info}

## 최종 합친 시그널 #{signal_index}
**종목**: {signal.get('asset', 'N/A')}
**시그널**: {signal.get('signal_type', 'N/A')}
**신뢰도**: {signal.get('confidence', 'N/A')}
**대표 인용**: "{signal.get('content', 'N/A')}"
**종합 맥락**: {signal.get('context', 'N/A')}
**비디오**: {video_id}
**제목**: {signal.get('title', 'N/A')}

위 합친 시그널이 자막 내용과 일치하는지, 합치기 결과가 적절한지 검증해주세요."""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.1,
            messages=[
                {"role": "user", "content": f"{prompt}\n\n{user_message}"}
            ]
        )
        
        raw = response.content[0].text.strip()
        
        # JSON 추출
        if raw.startswith('{'):
            return json.loads(raw)
        
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        raise json.JSONDecodeError("No JSON found", raw, 0)
        
    except json.JSONDecodeError as e:
        raw_text = response.content[0].text if 'response' in locals() else "N/A"
        return {
            "verdict": "error",
            "confidence": 0.0,
            "reason": f"JSON 파싱 실패: {str(e)}",
            "raw_response": raw_text[:500],
            "merge_assessment": "파싱 오류로 평가 불가"
        }
    
    except Exception as e:
        return {
            "verdict": "error", 
            "confidence": 0.0,
            "reason": f"API 호출 실패: {str(e)}",
            "merge_assessment": "API 오류로 평가 불가"
        }

def run_merged_verification(signals, client):
    """합친 시그널 전체 검증"""
    print(f"🤖 Claude 합친 시그널 검증 시작: {len(signals)}개")
    
    results = []
    
    for i, signal in enumerate(signals):
        video_id = signal.get('video_id', '')
        asset = signal.get('asset', 'N/A')
        merged_count = signal.get('merged_from_count', 1)
        merge_indicator = f"(합친 {merged_count}개)" if merged_count > 1 else "(단일)"
        
        print(f"\n📝 검증 중 ({i+1}/{len(signals)}): {video_id} - {asset} {merge_indicator}")
        
        # Claude 검증
        claude_result = verify_merged_signal_with_claude(client, signal, i)
        
        # 타임스탬프 추출
        content_text = signal.get('content', '')
        subtitle = load_subtitle(video_id)
        timestamp_seconds = extract_timestamp_from_subtitle(subtitle, content_text) if subtitle else None
        
        result_entry = {
            'signal_index': i,
            'video_id': video_id,
            'merged_signal': signal,
            'claude_verification': claude_result,
            'timestamp_seconds': timestamp_seconds
        }
        
        results.append(result_entry)
        
        # 결과 미리보기
        verdict = claude_result.get('verdict', 'unknown')
        confidence = claude_result.get('confidence', 0)
        timestamp_info = f"@{timestamp_seconds}s" if timestamp_seconds else "no timestamp"
        print(f"   🎯 Claude: {verdict} (신뢰도: {confidence:.2f}) {timestamp_info}")
        
        if merged_count > 1:
            merge_assessment = claude_result.get('merge_assessment', 'N/A')
            print(f"   🔀 합치기 평가: {merge_assessment[:50]}...")
        
        # API 제한 대기
        import time
        time.sleep(1.5)
    
    return results

def save_merged_verification_results(results):
    """합친 시그널 검증 결과 저장"""
    claude_result_file = 'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\_claude_verify_merged.json'
    timestamp_result_file = 'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\_merged_signals_with_timestamps.json'
    
    # 통계 계산
    summary = {
        'total_verified': len(results),
        'confirmed': 0,
        'corrected': 0,
        'rejected': 0,
        'errors': 0,
        'with_timestamps': 0,
        'merged_signals': 0,
        'average_confidence': 0.0,
        'timestamp': str(datetime.now())
    }
    
    total_confidence = 0
    signals_with_timestamps = []
    
    for result in results:
        claude_verification = result['claude_verification']
        merged_signal = result['merged_signal']
        
        verdict = claude_verification.get('verdict', 'error')
        confidence = claude_verification.get('confidence', 0)
        
        if verdict in summary:
            summary[verdict] += 1
        else:
            summary['errors'] += 1
        
        total_confidence += confidence
        
        if result.get('timestamp_seconds'):
            summary['with_timestamps'] += 1
        
        if merged_signal.get('merged_from_count', 1) > 1:
            summary['merged_signals'] += 1
        
        # 타임스탬프 포함 시그널 준비
        signal_with_timestamp = merged_signal.copy()
        signal_with_timestamp['timestamp_seconds'] = result.get('timestamp_seconds')
        signal_with_timestamp['claude_verdict'] = verdict
        signal_with_timestamp['claude_confidence'] = confidence
        signals_with_timestamps.append(signal_with_timestamp)
    
    if len(results) > 0:
        summary['average_confidence'] = total_confidence / len(results)
    
    # Claude 검증 결과 저장
    claude_output = {
        'metadata': {
            'timestamp': str(datetime.now()),
            'model_used': 'claude-3-haiku-20240307',
            'total_signals': len(results),
            'signal_type': 'merged_signals'
        },
        'summary': summary,
        'results': results
    }
    
    with open(claude_result_file, 'w', encoding='utf-8') as f:
        json.dump(claude_output, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Claude 검증 결과 저장: {claude_result_file}")
    
    # 타임스탬프 포함 시그널 저장
    with open(timestamp_result_file, 'w', encoding='utf-8') as f:
        json.dump(signals_with_timestamps, f, indent=2, ensure_ascii=False)
    
    print(f"💾 타임스탬프 시그널 저장: {timestamp_result_file}")
    
    return summary

def print_verification_summary(summary):
    """검증 결과 요약 출력"""
    print(f"\n{'='*60}")
    print(f"🤖 Claude 합친 시그널 검증 완료")
    print(f"{'='*60}")
    
    print(f"📊 검증 통계:")
    print(f"   - 총 시그널: {summary['total_verified']}개")
    print(f"   - ✅ 확인됨: {summary['confirmed']}개 ({summary['confirmed']/summary['total_verified']*100:.1f}%)")
    print(f"   - 🔧 수정됨: {summary['corrected']}개 ({summary['corrected']/summary['total_verified']*100:.1f}%)")
    print(f"   - ❌ 거부됨: {summary['rejected']}개 ({summary['rejected']/summary['total_verified']*100:.1f}%)")
    print(f"   - ⚠️ 오류: {summary['errors']}개")
    print(f"   - ⏰ 타임스탬프: {summary['with_timestamps']}개 ({summary['with_timestamps']/summary['total_verified']*100:.1f}%)")
    print(f"   - 🔀 합쳐진 것: {summary['merged_signals']}개")
    print(f"   - 평균 신뢰도: {summary['average_confidence']:.3f}")

def main():
    try:
        print("🚀 코린이 아빠 합친 시그널 Claude 검증 시작")
        
        # 1. Anthropic 클라이언트 설정
        client = setup_anthropic_client()
        if not client:
            return
        
        # 2. 합친 시그널 로드
        signals = load_merged_signals()
        if not signals:
            return
        
        # 3. 검증 실행
        results = run_merged_verification(signals, client)
        
        # 4. 결과 저장 및 요약
        summary = save_merged_verification_results(results)
        print_verification_summary(summary)
        
        print(f"\n✅ 합친 시그널 검증 완료!")
        print(f"📁 결과 파일:")
        print(f"   - Claude 검증: _claude_verify_merged.json")
        print(f"   - 타임스탬프: _merged_signals_with_timestamps.json")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()