#!/usr/bin/env python3

import os
import re
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_vtt(vtt_path):
    """VTT 파일에서 텍스트 추출"""
    text_lines = []
    
    try:
        with open(vtt_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        with open(vtt_path, 'r', encoding='cp949', errors='ignore') as f:
            content = f.read()
    
    lines = content.split('\n')
    capturing = False
    
    for line in lines:
        line = line.strip()
        
        if '-->' in line:
            capturing = True
            continue
        
        if not line or line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
            capturing = False
            continue
            
        if capturing and line:
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_line = re.sub(r'align:start position:\d+%', '', clean_line) 
            clean_line = clean_line.replace('?', '').replace('�', '').strip()
            
            if clean_line and len(clean_line) > 3:
                text_lines.append(clean_line)
    
    return ' '.join(text_lines)

def analyze_single_video(video_id, title):
    """단일 영상 분석"""
    
    # VTT 파일 찾기
    subs_dir = Path(__file__).parent / 'subs'
    vtt_files = list(subs_dir.glob(f"wsaj_{video_id}*.ko.vtt"))
    
    if not vtt_files:
        return {"error": f"VTT file not found for {video_id}"}
    
    # 자막 추출
    subtitle_text = extract_text_from_vtt(vtt_files[0])
    
    if len(subtitle_text) < 100:
        return {"error": "Subtitle too short"}
    
    # Claude 분석
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': os.getenv('ANTHROPIC_API_KEY', ''),
        'anthropic-version': '2023-06-01'
    }
    
    prompt = f"""
투자 인플루언서 YouTube 영상 분석:

=== 영상 정보 ===
제목: {title}
채널: 월가아재 (wsaj)

=== 자막 ===
{subtitle_text[:5000]}

다음 JSON 형태로만 응답:
{{
  "signals": [
    {{
      "stock": "종목명",
      "ticker": "종목코드",  
      "signal_type": "매수|긍정|중립|경계|매도",
      "key_quote": "핵심 발언 (15자 이상)",
      "reasoning": "근거 (20자 이상)",
      "timestamp": "MM:SS",
      "confidence": 7
    }}
  ]
}}
"""
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        
        if response.status_code == 200:
            content = response.json()['content'][0]['text']
            
            # JSON 추출
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                return json.loads(content[start:end].strip())
            elif '{' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                return json.loads(content[start:end])
                
        return {"error": f"API error: {response.status_code}"}
        
    except Exception as e:
        return {"error": str(e)}

# 테스트 실행
if __name__ == "__main__":
    # 엔비디아 실적 서프라이즈 분석
    result = analyze_single_video("liP35sqr9aU", "엔비디아 실적 서프라이즈")
    print(json.dumps(result, ensure_ascii=False, indent=2))