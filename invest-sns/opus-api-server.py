"""Lightweight Opus API server - only handles rejected signal analysis"""
import json, os, time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse
import anthropic

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

client = None
try:
    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
except:
    print("Warning: Anthropic client init failed")

def get_subtitle(video_id):
    path = f'smtr_data/corinpapa1106/{video_id}.txt'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def opus_review(signal, reason):
    if not client:
        return {"error": "No API client"}
    
    subtitle = get_subtitle(signal.get('video_id', ''))
    sub_text = subtitle[:6000] if subtitle else '(자막 없음)'
    
    prompt = f"""유튜브 영상에서 Claude Sonnet이 추출한 시그널을 인간이 거부했습니다. 분석해주세요.

**Sonnet 추출 시그널:**
- 종목: {signal.get('asset', 'N/A')}
- 시그널: {signal.get('signal_type', 'N/A')}  
- 내용: {signal.get('content', 'N/A')}
- 타임스탬프: {signal.get('timestamp', 'N/A')}
- 신뢰도: {signal.get('confidence', 'N/A')}
- 영상: {signal.get('title', 'N/A')}

**인간 거부 사유:** {reason or '(미기재)'}

**영상 자막:**
{sub_text}

**분석 요청:**
1. 인간의 거부가 타당한지
2. Sonnet이 왜 이걸 잘못 추출했는지
3. 추출 프롬프트 개선 제안

JSON으로 답변:
{{
  "agree_with_rejection": true/false,
  "reasoning": "상세 분석 (한국어)",
  "extraction_error": "Sonnet의 오류 원인 (한국어)",  
  "prompt_fix": "프롬프트에 추가할 규칙 (한국어)",
  "pattern": "오류 패턴 (예: 일반논평_시그널화, 조건부_무시, 종목_오인식)"
}}"""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        try:
            return json.loads(resp.content[0].text)
        except:
            # Try to extract JSON from response
            text = resp.content[0].text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return {"reasoning": text, "error": "JSON parse failed"}
    except Exception as e:
        return {"error": str(e)}

class Handler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if urlparse(self.path).path == '/api/opus-review':
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
            signal = body.get('signal', {})
            reason = body.get('reason', '')
            
            print(f"Opus reviewing: {signal.get('asset')} ({signal.get('signal_type')})")
            result = opus_review(signal, reason)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[{time.strftime('%H:%M:%S')}] {args[0] if args else ''}")

if __name__ == '__main__':
    port = 8901
    print(f'Opus API server: http://localhost:{port}')
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()
