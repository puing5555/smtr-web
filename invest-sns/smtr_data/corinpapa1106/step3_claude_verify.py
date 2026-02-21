#!/usr/bin/env python3
"""
Claude Opus 전체 시그널 검증
- 모든 시그널을 Claude Opus로 독립 검증
- 자막과 시그널 정보를 함께 제공하여 정확성 판단
"""
import json
import os
import sys
import io
import glob
import time
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def setup_anthropic_client():
    """Anthropic 클라이언트 설정"""
    # invest-engine/.env에서 API 키 로드
    load_dotenv(os.path.join('C:\\Users\\Mario\\work\\invest-engine', '.env'))
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY가 .env 파일에 없습니다.")
        print("🔑 invest-engine/.env에 다음 라인을 추가해주세요:")
        print("ANTHROPIC_API_KEY=your_api_key_here")
        return None
    
    try:
        client = Anthropic(api_key=api_key)
        print("✅ Claude 클라이언트 설정 완료")
        return client
    except Exception as e:
        print(f"❌ Claude 클라이언트 설정 오류: {e}")
        return None

def load_subtitle_content(video_id):
    """비디오 ID에 해당하는 자막 내용 로드"""
    subtitle_paths = [
        f"C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\{video_id}.txt",
        f"C:\\Users\\Mario\\.openclaw\\workspace\\smtr_data\\corinpapa1106\\{video_id}.txt"
    ]
    
    for path in subtitle_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"자막 파일 로드 오류 {path}: {e}")
                continue
    
    return None

def create_verification_prompt(signal, subtitle_content):
    """Claude 검증용 프롬프트 생성"""
    prompt = f"""다음은 한국의 주식/코인 투자 유튜브 영상에서 추출된 투자 시그널입니다. 
영상의 전체 자막과 함께 이 시그널이 정확한지 검증해주세요.

=== 추출된 시그널 ===
종목: {signal.get('asset', 'N/A')}
신호: {signal.get('signal_type', 'N/A')}
인용구: "{signal.get('content', 'N/A')}"
신뢰도: {signal.get('confidence', 'N/A')}
맥락: {signal.get('context', 'N/A')}

=== 영상 자막 (전체) ===
{subtitle_content}

=== 검증 요청 ===
위 자막을 바탕으로 추출된 시그널을 검증하고, 다음 중 하나로 분류해주세요:

1. **confirmed**: 시그널이 정확함
2. **corrected**: 시그널에 오류가 있음 (수정 의견 제시)
3. **rejected**: 해당 내용이 자막에 없거나 시그널이 아님

응답은 반드시 다음 JSON 형식으로 해주세요:
{{
  "judgment": "confirmed|corrected|rejected",
  "confidence": 0.95,
  "reason": "판단 근거를 구체적으로 설명",
  "correction": "corrected인 경우에만 - 올바른 시그널이나 의견"
}}

특히 주의할 점:
- 단순한 의견이나 분석을 매수/매도 시그널로 잘못 분류하지 않았는지 확인
- 반어법이나 가정적 표현을 실제 투자 권유로 잘못 해석하지 않았는지 확인
- 과거 투자 경험 공유를 현재 투자 시그널로 잘못 분류하지 않았는지 확인
"""
    return prompt

def verify_signal_with_claude(client, signal, subtitle_content):
    """Claude를 사용해 시그널 검증"""
    if not subtitle_content:
        return {
            "judgment": "rejected",
            "confidence": 0.0,
            "reason": "자막 파일을 찾을 수 없음",
            "correction": None
        }
    
    prompt = create_verification_prompt(signal, subtitle_content)
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{
                "role": "user", 
                "content": prompt
            }]
        )
        
        # JSON 응답 파싱
        response_text = response.content[0].text
        
        # JSON 부분만 추출 (마크다운 코드 블록 제거)
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            json_text = response_text[json_start:json_end].strip()
        elif '{' in response_text and '}' in response_text:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_text = response_text[json_start:json_end]
        else:
            json_text = response_text
        
        result = json.loads(json_text)
        
        # 필수 필드 검증
        required_fields = ['judgment', 'confidence', 'reason']
        for field in required_fields:
            if field not in result:
                result[field] = "N/A"
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류: {e}")
        print(f"응답 내용: {response_text}")
        return {
            "judgment": "error",
            "confidence": 0.0,
            "reason": f"JSON 파싱 오류: {e}",
            "correction": None
        }
    except Exception as e:
        print(f"Claude API 오류: {e}")
        return {
            "judgment": "error",
            "confidence": 0.0,
            "reason": f"API 오류: {e}",
            "correction": None
        }

def main():
    input_path = "_signals_with_timestamps.json"
    output_path = "_claude_verify_full.json"
    
    print("=== Claude Opus 전체 시그널 검증 ===")
    
    # Claude 클라이언트 설정
    client = setup_anthropic_client()
    if not client:
        print("❌ Claude 클라이언트 설정 실패")
        return
    
    # 시그널 로드
    print(f"시그널 로드 중: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        signals = json.load(f)
    
    print(f"총 {len(signals)}개 시그널 검증 시작")
    
    # 검증 결과
    verified_signals = []
    total_cost = 0
    
    for i, signal in enumerate(signals, 1):
        video_id = signal.get('video_id')
        asset = signal.get('asset')
        
        print(f"[{i}/{len(signals)}] 검증 중: {video_id} - {asset}")
        
        # 자막 로드
        subtitle_content = load_subtitle_content(video_id)
        
        # Claude 검증
        verification_result = verify_signal_with_claude(client, signal, subtitle_content)
        
        # 결과 합치기
        verified_signal = signal.copy()
        verified_signal['claude_verification'] = verification_result
        verified_signal['verification_timestamp'] = datetime.now().isoformat()
        
        verified_signals.append(verified_signal)
        
        # 비용 추정 (대략적)
        input_tokens = len(str(subtitle_content or "") + str(signal)) // 4  # 대략적 토큰 수
        output_tokens = len(str(verification_result)) // 4
        cost = (input_tokens * 0.000003) + (output_tokens * 0.000015)  # Claude 3.5 Sonnet 가격
        total_cost += cost
        
        print(f"  -> {verification_result.get('judgment', 'error')} (신뢰도: {verification_result.get('confidence', 0)})")
        
        # API 호출 제한을 위한 대기
        time.sleep(1)
    
    # 결과 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(verified_signals, f, ensure_ascii=False, indent=2)
    
    # 통계 출력
    judgment_counts = {}
    confidence_sum = 0
    confidence_count = 0
    
    for signal in verified_signals:
        verification = signal.get('claude_verification', {})
        judgment = verification.get('judgment', 'error')
        judgment_counts[judgment] = judgment_counts.get(judgment, 0) + 1
        
        if isinstance(verification.get('confidence'), (int, float)):
            confidence_sum += verification.get('confidence')
            confidence_count += 1
    
    print(f"\n=== 검증 완료 ===")
    print(f"총 시그널: {len(verified_signals)}")
    print(f"예상 비용: ${total_cost:.2f}")
    
    print(f"\n판정 분포:")
    for judgment, count in judgment_counts.items():
        percentage = count / len(verified_signals) * 100
        print(f"  {judgment}: {count}개 ({percentage:.1f}%)")
    
    if confidence_count > 0:
        avg_confidence = confidence_sum / confidence_count
        print(f"\n평균 신뢰도: {avg_confidence:.3f}")
    
    print(f"\n결과 저장: {output_path}")

if __name__ == "__main__":
    main()