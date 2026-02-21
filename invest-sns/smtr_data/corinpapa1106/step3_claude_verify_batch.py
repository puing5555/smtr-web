#!/usr/bin/env python3
"""
Claude 전체 검증 (배치 처리)
- 20개씩 배치로 처리하여 안정성 확보
- 진행 상황을 파일로 저장하여 중단 시 재개 가능
"""
import json
import os
import sys
import io
import time
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

BATCH_SIZE = 20
PROGRESS_FILE = "_claude_progress.json"

def setup_anthropic_client():
    """Anthropic 클라이언트 설정"""
    load_dotenv(os.path.join('C:\\Users\\Mario\\work\\invest-engine', '.env'))
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY가 .env 파일에 없습니다.")
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
    # 자막 내용 길이 제한 (토큰 절약)
    if subtitle_content and len(subtitle_content) > 8000:
        subtitle_content = subtitle_content[:8000] + "...(자막 내용 일부 생략)"
    
    prompt = f"""다음은 한국의 주식/코인 투자 유튜브 영상에서 추출된 투자 시그널입니다. 
영상의 자막과 함께 이 시그널이 정확한지 검증해주세요.

=== 추출된 시그널 ===
종목: {signal.get('asset', 'N/A')}
신호: {signal.get('signal_type', 'N/A')}
인용구: "{signal.get('content', 'N/A')}"

=== 영상 자막 ===
{subtitle_content or '자막을 찾을 수 없습니다.'}

=== 검증 요청 ===
위 자막을 바탕으로 추출된 시그널을 검증하고, 다음 중 하나로 분류해주세요:

1. **confirmed**: 시그널이 정확함
2. **corrected**: 시그널에 오류가 있음 (수정 의견 제시)
3. **rejected**: 해당 내용이 자막에 없거나 시그널이 아님

응답은 반드시 다음 JSON 형식으로 해주세요:
{{
  "judgment": "confirmed|corrected|rejected",
  "confidence": 0.95,
  "reason": "판단 근거를 간결하게 설명",
  "correction": "corrected인 경우에만 수정 의견"
}}
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
            model="claude-3-haiku-20240307",
            max_tokens=500,  # 토큰 절약
            messages=[{
                "role": "user", 
                "content": prompt
            }]
        )
        
        response_text = response.content[0].text
        
        # JSON 부분만 추출
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
        if 'judgment' not in result:
            result['judgment'] = 'error'
        if 'confidence' not in result:
            result['confidence'] = 0.0
        if 'reason' not in result:
            result['reason'] = 'No reason provided'
        
        return result
        
    except Exception as e:
        print(f"Claude API 오류: {e}")
        return {
            "judgment": "error",
            "confidence": 0.0,
            "reason": f"API 오류: {str(e)[:100]}",
            "correction": None
        }

def load_progress():
    """진행 상황 로드"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed": 0, "results": []}

def save_progress(processed_count, results):
    """진행 상황 저장"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"processed": processed_count, "results": results}, f, ensure_ascii=False, indent=2)

def main():
    input_path = "_signals_with_timestamps.json"
    output_path = "_claude_verify_full.json"
    
    print("=== Claude 전체 검증 (배치 처리) ===")
    
    # Claude 클라이언트 설정
    client = setup_anthropic_client()
    if not client:
        return
    
    # 시그널 로드
    with open(input_path, 'r', encoding='utf-8') as f:
        signals = json.load(f)
    
    print(f"총 {len(signals)}개 시그널")
    
    # 진행 상황 로드
    progress = load_progress()
    processed_count = progress["processed"]
    verified_signals = progress["results"]
    
    print(f"이전 진행: {processed_count}/{len(signals)} 처리됨")
    
    # 남은 시그널 처리
    total_cost = 0
    
    for i in range(processed_count, len(signals), BATCH_SIZE):
        batch_end = min(i + BATCH_SIZE, len(signals))
        batch = signals[i:batch_end]
        
        print(f"\n=== 배치 {i//BATCH_SIZE + 1}: {i+1}-{batch_end}/{len(signals)} ===")
        
        for j, signal in enumerate(batch):
            signal_idx = i + j
            video_id = signal.get('video_id')
            asset = signal.get('asset')
            
            print(f"[{signal_idx+1}/{len(signals)}] 검증: {video_id} - {asset}")
            
            # 자막 로드
            subtitle_content = load_subtitle_content(video_id)
            
            # Claude 검증
            verification_result = verify_signal_with_claude(client, signal, subtitle_content)
            
            # 결과 합치기
            verified_signal = signal.copy()
            verified_signal['claude_verification'] = verification_result
            verified_signal['verification_timestamp'] = datetime.now().isoformat()
            
            verified_signals.append(verified_signal)
            
            # 비용 추정
            input_tokens = len(str(subtitle_content or "")[:8000] + str(signal)) // 4
            output_tokens = len(str(verification_result)) // 4
            cost = (input_tokens * 0.00000025) + (output_tokens * 0.00000125)
            total_cost += cost
            
            judgment = verification_result.get('judgment', 'error')
            confidence = verification_result.get('confidence', 0)
            print(f"  -> {judgment} (신뢰도: {confidence})")
            
            # API 제한 대기
            time.sleep(1)
        
        # 배치 완료 후 진행 상황 저장
        processed_count = batch_end
        save_progress(processed_count, verified_signals)
        print(f"배치 완료. 진행상황 저장: {processed_count}/{len(signals)}")
        
        # 중간 결과 저장
        if processed_count % (BATCH_SIZE * 3) == 0 or processed_count == len(signals):
            with open(f"_claude_partial_{processed_count}.json", 'w', encoding='utf-8') as f:
                json.dump(verified_signals, f, ensure_ascii=False, indent=2)
            print(f"중간 결과 저장: _claude_partial_{processed_count}.json")
    
    # 최종 결과 저장
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
    print(f"예상 비용: ${total_cost:.3f}")
    
    print(f"\n판정 분포:")
    for judgment, count in judgment_counts.items():
        percentage = count / len(verified_signals) * 100
        print(f"  {judgment}: {count}개 ({percentage:.1f}%)")
    
    if confidence_count > 0:
        avg_confidence = confidence_sum / confidence_count
        print(f"\n평균 신뢰도: {avg_confidence:.3f}")
    
    print(f"\n최종 결과: {output_path}")
    
    # 진행 상황 파일 삭제
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        print("진행 상황 파일 삭제됨")

if __name__ == "__main__":
    main()