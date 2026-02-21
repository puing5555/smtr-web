"""
코린이 아빠 194개 시그널 전체 Claude Opus 검증
- _all_signals_194.json의 모든 시그널을 Claude Opus로 검증
- 타임스탬프 추출도 함께 수행
"""
import json, os, sys, io, re
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

def load_all_signals():
    """194개 전체 시그널 로드"""
    signal_file = 'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\_all_signals_194.json'
    
    try:
        with open(signal_file, 'r', encoding='utf-8') as f:
            signals = json.load(f)
        
        print(f"✅ 로드된 시그널: {len(signals)}개")
        return signals
    except Exception as e:
        print(f"❌ 시그널 파일 로드 실패: {e}")
        return None

def load_subtitle(video_id):
    """특정 비디오의 자막 로드 (두 곳에서 시도)"""
    subtitle_paths = [
        f'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\{video_id}.txt',
        f'C:\\Users\\Mario\\.openclaw\\workspace\\smtr_data\\corinpapa1106\\{video_id}.txt'
    ]
    
    for subtitle_path in subtitle_paths:
        if os.path.exists(subtitle_path):
            try:
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"📄 자막 로드: {subtitle_path}")
                return content
            except Exception as e:
                print(f"⚠️ 자막 읽기 실패: {subtitle_path} - {e}")
                continue
    
    print(f"❌ 자막 파일 없음: {video_id}")
    return None

def extract_timestamp_from_subtitle(subtitle_text, quote_text, margin_chars=100):
    """자막에서 인용문과 매칭되는 타임스탬프 찾기"""
    if not subtitle_text or not quote_text:
        return None
    
    # 인용문 정리 (따옴표, 공백 등 제거)
    clean_quote = re.sub(r'["\'""]', '', quote_text.strip())
    clean_quote = re.sub(r'\s+', ' ', clean_quote)
    
    if len(clean_quote) < 10:  # 너무 짧은 인용문은 스킵
        return None
    
    # 자막에서 타임스탬프 패턴 찾기
    timestamp_pattern = r'(\d{1,2}:\d{2}:\d{2}(?:\.\d{3})?|\d{1,2}:\d{2}(?:\.\d{3})?)'
    
    lines = subtitle_text.split('\n')
    
    # 각 라인에서 인용문과 유사한 텍스트 찾기
    best_match = None
    best_similarity = 0
    
    for i, line in enumerate(lines):
        line_clean = re.sub(r'["\'""]', '', line.strip())
        line_clean = re.sub(r'\s+', ' ', line_clean)
        
        if not line_clean:
            continue
        
        # 간단한 문자열 매칭 (부분 일치)
        if len(clean_quote) > 20:
            # 긴 인용문의 경우 부분 매칭
            words = clean_quote.split()[:5]  # 처음 5단어만 사용
            search_text = ' '.join(words)
        else:
            search_text = clean_quote
        
        if search_text.lower() in line_clean.lower():
            # 해당 라인 주변에서 타임스탬프 찾기
            context_start = max(0, i - 3)
            context_end = min(len(lines), i + 4)
            
            for j in range(context_start, context_end):
                timestamps = re.findall(timestamp_pattern, lines[j])
                if timestamps:
                    timestamp_str = timestamps[-1]  # 마지막 타임스탬프 사용
                    return convert_timestamp_to_seconds(timestamp_str)
    
    return None

def convert_timestamp_to_seconds(timestamp_str):
    """타임스탬프 문자열을 초 단위로 변환"""
    try:
        # MM:SS 또는 HH:MM:SS 형식 처리
        parts = timestamp_str.split(':')
        
        if len(parts) == 2:  # MM:SS
            minutes, seconds = parts
            return int(minutes) * 60 + float(seconds)
        elif len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        else:
            return None
    except:
        return None

def create_claude_prompt():
    """Claude 검증용 프롬프트"""
    return """당신은 투자 유튜브 영상에서 추출된 투자 시그널을 검증하는 전문가입니다.

## 검증 작업
주어진 자막과 AI가 추출한 시그널을 비교하여 정확성을 판단해주세요.

## 시그널 분류 기준
- **STRONG_BUY**: 매우 강한 매수 추천 ("올인", "지금 당장 사야", "몰빵")
- **BUY**: 명시적 매수 행동/추천 ("사라", "담아라", "매수했다", "비중확대")  
- **POSITIVE**: 긍정적 전망이지만 매수 추천은 아님 ("좋다", "유망하다", "성장할 것")
- **HOLD**: 보유 유지 ("들고가라", "팔지마")
- **NEUTRAL**: 중립적 분석, 방향성 없음
- **CONCERN**: 우려/주의 ("조심해야", "리스크 있다")
- **SELL**: 명시적 매도 ("팔아라", "비중축소")
- **STRONG_SELL**: 매우 강한 매도 ("당장 팔아라", "위험하다 빼라")

## 검증 기준
1. **종목명**: 자막에서 실제로 언급된 정확한 종목명인가?
2. **시그널**: 실제 발언 내용과 시그널 분류가 일치하는가?
3. **인용문**: 자막의 실제 내용과 일치하는가?
4. **존재성**: 자막에 없는 내용을 AI가 만들어내지 않았는가?

## 응답 형식 (JSON만)
```json
{
  "verdict": "confirmed" | "corrected" | "rejected",
  "confidence": 0.0-1.0,
  "reason": "판단 근거를 상세히 설명",
  "corrected_asset": "종목명 수정이 필요한 경우만",
  "corrected_signal": "시그널 수정이 필요한 경우만",
  "corrected_content": "내용 수정이 필요한 경우만"
}
```

## 판정 기준
- **confirmed**: 시그널이 정확하고 자막 내용과 일치
- **corrected**: 부분적으로 틀림, 수정 의견 제시
- **rejected**: 명백히 틀렸거나 자막에 없는 내용

엄격하게 검증하되, 자막 내용만을 기준으로 판단하세요."""

def verify_signal_with_claude(client, signal, subtitle, signal_index):
    """Claude로 개별 시그널 검증"""
    
    prompt = create_claude_prompt()
    
    # 자막이 너무 길면 자르기 (토큰 제한)
    if len(subtitle) > 8000:
        subtitle = subtitle[:8000] + "\n\n[자막이 너무 길어서 일부만 표시]"
    
    user_message = f"""## 원본 자막
{subtitle}

## AI가 추출한 시그널 #{signal_index}
**종목**: {signal.get('asset', 'N/A')}
**시그널**: {signal.get('signal_type', 'N/A')}
**내용**: {signal.get('content', 'N/A')}
**신뢰도**: {signal.get('confidence', 'N/A')}
**맥락**: {signal.get('context', 'N/A')}
**비디오**: {signal.get('video_id', 'N/A')}
**제목**: {signal.get('title', 'N/A')}

위 시그널이 자막 내용과 정확히 일치하는지 검증해주세요."""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # 현재 사용 가능한 모델
            max_tokens=1000,
            temperature=0.1,
            messages=[
                {"role": "user", "content": f"{prompt}\n\n{user_message}"}
            ]
        )
        
        raw = response.content[0].text.strip()
        
        # JSON 추출 시도
        if raw.startswith('{'):
            return json.loads(raw)
        
        # ```json ... ``` 블록 찾기
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # 단순 JSON 블록 찾기
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        raise json.JSONDecodeError("No JSON found", raw, 0)
        
    except json.JSONDecodeError as e:
        print(f"⚠️ Claude 응답 JSON 파싱 실패: {e}")
        raw_text = response.content[0].text if 'response' in locals() else "N/A"
        return {
            "verdict": "error",
            "confidence": 0.0,
            "reason": f"응답 파싱 실패: {str(e)}",
            "raw_response": raw_text[:500]
        }
    
    except Exception as e:
        print(f"⚠️ Claude API 호출 실패: {e}")
        return {
            "verdict": "error", 
            "confidence": 0.0,
            "reason": f"API 호출 실패: {str(e)}"
        }

def run_full_verification(signals, client):
    """194개 시그널 전체 검증"""
    print(f"🤖 Claude 전체 검증 시작: {len(signals)}개 시그널")
    
    results = []
    processed_videos = set()
    
    for i, signal in enumerate(signals):
        video_id = signal.get('video_id', '')
        
        print(f"\n📝 검증 중 ({i+1}/{len(signals)}): {video_id} - {signal.get('asset', 'N/A')}")
        
        # 자막 로드 (비디오별로 한 번만)
        subtitle = None
        if video_id not in processed_videos:
            subtitle = load_subtitle(video_id)
            processed_videos.add(video_id)
        else:
            # 이미 처리된 비디오면 다시 로드
            subtitle = load_subtitle(video_id)
        
        if not subtitle:
            print(f"❌ 자막 없음, 스킵: {video_id}")
            results.append({
                'signal_index': i,
                'video_id': video_id,
                'original_signal': signal,
                'claude_verification': {
                    'verdict': 'error',
                    'confidence': 0.0,
                    'reason': '자막 파일 없음'
                },
                'timestamp_seconds': None
            })
            continue
        
        # Claude 검증 수행
        claude_result = verify_signal_with_claude(client, signal, subtitle, i)
        
        # 타임스탬프 추출
        content_text = signal.get('content', '')
        timestamp_seconds = extract_timestamp_from_subtitle(subtitle, content_text)
        
        result_entry = {
            'signal_index': i,
            'video_id': video_id,
            'original_signal': signal,
            'claude_verification': claude_result,
            'timestamp_seconds': timestamp_seconds
        }
        
        results.append(result_entry)
        
        # 결과 미리보기
        verdict = claude_result.get('verdict', 'unknown')
        confidence = claude_result.get('confidence', 0)
        timestamp_info = f"@{timestamp_seconds}s" if timestamp_seconds else "no timestamp"
        print(f"   🎯 Claude: {verdict} (신뢰도: {confidence:.2f}) {timestamp_info}")
        
        # API 요청 간격 (Rate limiting 방지)
        import time
        time.sleep(1.5)  # 1.5초 대기
    
    return results

def save_results(results):
    """검증 결과 저장"""
    # Claude 검증 결과 저장
    claude_result_file = 'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\_claude_verify_full.json'
    
    # 타임스탬프 포함 시그널 저장
    timestamp_result_file = 'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\_signals_with_timestamps.json'
    
    # 결과 요약 통계
    summary = {
        'total_verified': len(results),
        'confirmed': 0,
        'corrected': 0,
        'rejected': 0,
        'errors': 0,
        'with_timestamps': 0,
        'average_confidence': 0.0,
        'timestamp': str(datetime.now())
    }
    
    total_confidence = 0
    signals_with_timestamps = []
    
    for result in results:
        verdict = result['claude_verification'].get('verdict', 'error')
        confidence = result['claude_verification'].get('confidence', 0)
        
        if verdict in summary:
            summary[verdict] += 1
        else:
            summary['errors'] += 1
        
        total_confidence += confidence
        
        if result.get('timestamp_seconds'):
            summary['with_timestamps'] += 1
        
        # 타임스탬프 포함 시그널 준비
        signal_with_timestamp = result['original_signal'].copy()
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
            'total_signals': len(results)
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

def print_summary(summary):
    """검증 결과 요약 출력"""
    print(f"\n{'='*60}")
    print(f"🤖 Claude 194개 시그널 전체 검증 완료")
    print(f"{'='*60}")
    
    print(f"📊 검증 통계:")
    print(f"   - 총 시그널: {summary['total_verified']}개")
    print(f"   - ✅ 확인됨 (confirmed): {summary['confirmed']}개")
    print(f"   - 🔧 수정됨 (corrected): {summary['corrected']}개")
    print(f"   - ❌ 거부됨 (rejected): {summary['rejected']}개")
    print(f"   - ⚠️  오류: {summary['errors']}개")
    print(f"   - ⏰ 타임스탬프 추출: {summary['with_timestamps']}개")
    print(f"   - 평균 신뢰도: {summary['average_confidence']:.3f}")
    
    # 비율 계산
    total = summary['total_verified']
    if total > 0:
        confirmed_rate = (summary['confirmed'] / total) * 100
        timestamp_rate = (summary['with_timestamps'] / total) * 100
        
        print(f"\n📈 성공률:")
        print(f"   - 검증 통과율: {confirmed_rate:.1f}%")
        print(f"   - 타임스탬프 추출율: {timestamp_rate:.1f}%")

def main():
    try:
        print("🚀 코린이 아빠 194개 시그널 Claude 전체 검증 시작")
        
        # 1. Anthropic 클라이언트 설정
        client = setup_anthropic_client()
        if not client:
            return
        
        # 2. 194개 시그널 로드
        signals = load_all_signals()
        if not signals:
            return
        
        # 3. 전체 검증 실행
        results = run_full_verification(signals, client)
        
        # 4. 결과 저장 및 요약
        summary = save_results(results)
        print_summary(summary)
        
        print(f"\n✅ 모든 작업 완료!")
        print(f"📁 결과 파일:")
        print(f"   - Claude 검증: _claude_verify_full.json")
        print(f"   - 타임스탬프 시그널: _signals_with_timestamps.json")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()