#!/usr/bin/env python3
"""
Claude 검증 테스트 (처음 5개 시그널만)
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
                    content = f.read()
                    return content[:5000]  # 테스트용으로 처음 5000자만
            except Exception as e:
                print(f"자막 파일 로드 오류 {path}: {e}")
                continue
    
    return None

def create_verification_prompt(signal, subtitle_content):
    """Claude 검증용 프롬프트 생성"""
    prompt = f"""다음은 한국의 주식/코인 투자 유튜브 영상에서 추출된 투자 시그널입니다. 
영상의 자막 일부와 함께 이 시그널이 정확한지 검증해주세요.

=== 추출된 시그널 ===
종목: {signal.get('asset', 'N/A')}
신호: {signal.get('signal_type', 'N/A')}
인용구: "{signal.get('content', 'N/A')}"

=== 영상 자막 (일부) ===
{subtitle_content}

=== 검증 요청 ===
위 자막을 바탕으로 추출된 시그널을 검증하고, 다음 중 하나로 분류해주세요:

1. **confirmed**: 시그널이 정확함
2. **corrected**: 시그널에 오류가 있음
3. **rejected**: 해당 내용이 자막에 없거나 시그널이 아님

응답은 반드시 다음 JSON 형식으로 해주세요:
{{
  "judgment": "confirmed|corrected|rejected",
  "confidence": 0.95,
  "reason": "판단 근거를 구체적으로 설명",
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
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
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
        return result
        
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
    
    print("=== Claude 검증 테스트 (처음 5개) ===")
    
    client = setup_anthropic_client()
    if not client:
        return
    
    with open(input_path, 'r', encoding='utf-8') as f:
        signals = json.load(f)
    
    # 처음 5개만 테스트
    test_signals = signals[:5]
    print(f"테스트 시그널: {len(test_signals)}개")
    
    for i, signal in enumerate(test_signals, 1):
        video_id = signal.get('video_id')
        asset = signal.get('asset')
        
        print(f"[{i}/{len(test_signals)}] 테스트: {video_id} - {asset}")
        
        subtitle_content = load_subtitle_content(video_id)
        verification_result = verify_signal_with_claude(client, signal, subtitle_content)
        
        print(f"  -> {verification_result.get('judgment', 'error')} (신뢰도: {verification_result.get('confidence', 0)})")
        print(f"  사유: {verification_result.get('reason', 'N/A')}")
        
        if verification_result.get('correction'):
            print(f"  수정: {verification_result.get('correction')}")
        
        print()
        time.sleep(2)  # API 제한을 위한 대기
    
    print("테스트 완료!")

if __name__ == "__main__":
    main()