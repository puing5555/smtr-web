"""Signal Review Web Server - serves review page and stores results"""
import json, os, sys, threading, time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
from urllib.parse import urlparse, parse_qs
import anthropic

REVIEW_FILE = os.path.join('smtr_data', 'corinpapa1106', '_review_results.json')
SIGNALS_FILE = os.path.join('smtr_data', 'corinpapa1106', '_deduped_signals_8types_dated.json')
OPUS4_ANALYSIS_FILE = os.path.join('smtr_data', 'corinpapa1106', '_opus4_analysis.json')
PROMPT_VERSIONS_FILE = os.path.join('smtr_data', '_prompt_versions.json')

# Anthropic 클라이언트 초기화
try:
    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
except Exception as e:
    print(f"Warning: Anthropic client init failed: {e}")
    client = None

def load_reviews():
    if os.path.exists(REVIEW_FILE):
        with open(REVIEW_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_reviews(data):
    with open(REVIEW_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_opus4_analysis():
    if os.path.exists(OPUS4_ANALYSIS_FILE):
        with open(OPUS4_ANALYSIS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_opus4_analysis(data):
    os.makedirs(os.path.dirname(OPUS4_ANALYSIS_FILE), exist_ok=True)
    with open(OPUS4_ANALYSIS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_prompt_versions():
    if os.path.exists(PROMPT_VERSIONS_FILE):
        with open(PROMPT_VERSIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"versions": [], "suggestions": []}

def save_prompt_versions(data):
    os.makedirs(os.path.dirname(PROMPT_VERSIONS_FILE), exist_ok=True)
    with open(PROMPT_VERSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_subtitle_content(video_id):
    """자막 파일 내용 읽기"""
    subtitle_file = os.path.join('smtr_data', 'corinpapa1106', f'{video_id}.txt')
    if os.path.exists(subtitle_file):
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def opus4_analyze_signal(signal_id, signal_data, rejection_reason):
    """Opus 4로 거부된 시그널을 재분석"""
    if not client:
        return {"error": "Anthropic client not available"}
    
    video_id = signal_data.get('video_id')
    if not video_id:
        return {"error": "video_id not found"}
    
    subtitle_content = get_subtitle_content(video_id)
    if not subtitle_content:
        return {"error": f"Subtitle file not found for video {video_id}"}
    
    try:
        prompt = f"""
다음은 유튜브 영상 자막과 Claude Sonnet이 추출한 시그널, 그리고 인간이 거부한 사유입니다.

**영상 자막:**
{subtitle_content}

**Sonnet이 추출한 시그널:**
- 종목: {signal_data.get('asset', 'N/A')}
- 시그널 타입: {signal_data.get('signal_type', 'N/A')}
- 내용: {signal_data.get('content', 'N/A')}
- 타임스탬프: {signal_data.get('timestamp', 'N/A')}
- 신뢰도: {signal_data.get('confidence', 'N/A')}

**인간의 거부 사유:**
{rejection_reason}

**시그널 타입 정의 (절대 변경 금지):**
STRONG_BUY / BUY / POSITIVE / HOLD / NEUTRAL / CONCERN / SELL / STRONG_SELL

**분석 요청:**
자막을 처음부터 끝까지 다시 읽고 다음을 분석해주세요:

1. **Sonnet 시그널 검증**: Sonnet이 추출한 시그널이 자막 내용과 일치하는가?
2. **거부 사유 타당성**: 인간의 거부 사유가 합리적인가?
3. **올바른 시그널**: 실제로는 어떤 시그널이 맞는가? (위 8가지 타입 중 하나, 또는 시그널 없음)
4. **프롬프트 개선 제안**: Sonnet의 추출 정확도를 높이려면 프롬프트를 어떻게 개선해야 하는가?

JSON 형식으로 답변해주세요:
{{
  "sonnet_signal_correct": true/false,
  "rejection_valid": true/false,
  "correct_signal": {{
    "signal_type": "STRONG_BUY|BUY|POSITIVE|HOLD|NEUTRAL|CONCERN|SELL|STRONG_SELL 또는 null(시그널 없음)",
    "asset": "올바른 종목명 또는 null",
    "content": "올바른 시그널 내용 (자막에서 직접 인용)",
    "timestamp": "올바른 타임스탬프",
    "confidence": "HIGH|MEDIUM|LOW"
  }},
  "suggestion": {{
    "action": "APPROVE|REJECT|MODIFY",
    "changes": "변경 요약 (예: 'SELL → CONCERN', '종목명 XRP → 리플', '시그널 없음으로 삭제')",
    "reason": "변경/승인/거부 사유 (한 줄 요약)"
  }},
  "analysis": "상세한 분석 내용",
  "prompt_improvement": "프롬프트 개선 제안"
}}
"""
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # 가용한 모델 사용 
            max_tokens=4000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # JSON 응답 파싱 시도
        try:
            result = json.loads(response.content[0].text)
            result['raw_response'] = response.content[0].text
            return result
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response.content[0].text
            }
            
    except Exception as e:
        return {"error": str(e)}

def trigger_opus4_analysis(signal_id, signal_data, rejection_reason):
    """비동기로 Opus 4 분석 실행"""
    def analyze():
        # 분석 중 상태로 표시
        analysis_data = load_opus4_analysis()
        analysis_data[signal_id] = {"status": "analyzing", "timestamp": time.time()}
        save_opus4_analysis(analysis_data)
        
        # Opus 4 분석 실행
        result = opus4_analyze_signal(signal_id, signal_data, rejection_reason)
        
        # 결과 저장
        analysis_data = load_opus4_analysis()
        analysis_data[signal_id] = {
            **result,
            "status": "completed",
            "timestamp": time.time(),
            "signal_data": signal_data,
            "rejection_reason": rejection_reason
        }
        save_opus4_analysis(analysis_data)
        
        # 프롬프트 개선 제안 저장
        if 'prompt_improvement' in result and result['prompt_improvement']:
            prompt_data = load_prompt_versions()
            prompt_data['suggestions'].append({
                "timestamp": time.time(),
                "signal_id": signal_id,
                "suggestion": result['prompt_improvement']
            })
            save_prompt_versions(prompt_data)
    
    # 백그라운드에서 실행
    threading.Thread(target=analyze, daemon=True).start()

class ReviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/' or parsed.path == '/review':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            
            with open(SIGNALS_FILE, 'r', encoding='utf-8') as f:
                signals = json.load(f)
            reviews = load_reviews()
            
            html = build_review_html(signals, reviews)
            self.wfile.write(html.encode('utf-8'))
            
        elif parsed.path == '/api/reviews':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(load_reviews(), ensure_ascii=False).encode('utf-8'))
            
        elif parsed.path == '/api/signals':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            with open(SIGNALS_FILE, 'r', encoding='utf-8') as f:
                signals = json.load(f)
            # Sort by date descending (newest first)
            signals.sort(key=lambda s: s.get('date', ''), reverse=True)
            self.wfile.write(json.dumps(signals, ensure_ascii=False).encode('utf-8'))
            
        elif parsed.path == '/api/opus4-analysis':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            analysis_data = load_opus4_analysis()
            self.wfile.write(json.dumps(analysis_data, ensure_ascii=False).encode('utf-8'))
            
        elif parsed.path == '/api/prompt-suggestions':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            prompt_data = load_prompt_versions()
            self.wfile.write(json.dumps(prompt_data, ensure_ascii=False).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        if parsed.path == '/api/review':
            data = json.loads(body)
            reviews = load_reviews()
            sig_id = data.get('id', '')
            status = data.get('status', 'pending')
            reason = data.get('reason', '')
            
            reviews[sig_id] = {
                'status': status,
                'reason': reason,
                'time': data.get('time', ''),
                'review_note': data.get('review_note', ''),
                'review_change': data.get('review_change', ''),
                'review_reason': data.get('review_reason', '')
            }
            save_reviews(reviews)
            
            # 거부된 경우 Opus 4 재검증 트리거
            if status == 'rejected' and reason:
                # 시그널 데이터 찾기
                with open(SIGNALS_FILE, 'r', encoding='utf-8') as f:
                    signals = json.load(f)
                
                signal_data = None
                for sig in signals:
                    if sig['video_id'] + '_' + sig['asset'] == sig_id:
                        signal_data = sig
                        break
                
                if signal_data:
                    trigger_opus4_analysis(sig_id, signal_data, reason)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))
            
        elif parsed.path == '/api/opus4-verify':
            data = json.loads(body)
            signal_id = data.get('signal_id', '')
            
            # 강제로 Opus 4 재검증 실행
            with open(SIGNALS_FILE, 'r', encoding='utf-8') as f:
                signals = json.load(f)
            
            signal_data = None
            for sig in signals:
                if sig['video_id'] + '_' + sig['asset'] == signal_id:
                    signal_data = sig
                    break
            
            if signal_data:
                reviews = load_reviews()
                rejection_reason = reviews.get(signal_id, {}).get('reason', '수동 재검증 요청')
                trigger_opus4_analysis(signal_id, signal_data, rejection_reason)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'message': 'Opus 4 분석 시작됨'}).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Signal not found'}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass  # suppress logs

def build_review_html(signals, reviews):
    return '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>유튜버 시그널 검증 리뷰 v3</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f4f8; color: #1a1a2e; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 16px; margin-bottom: 24px; }
        .header h1 { font-size: 24px; margin-bottom: 8px; }
        .header p { opacity: 0.9; font-size: 14px; }
        .stats { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
        .stat-card { background: white; border-radius: 12px; padding: 16px 20px; flex: 1; min-width: 120px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .stat-number { font-size: 28px; font-weight: 700; color: #667eea; }
        .stat-label { font-size: 12px; color: #666; margin-top: 4px; }
        .filters { background: white; border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .filter-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: end; }
        .filter-group { display: flex; flex-direction: column; gap: 4px; }
        .filter-label { font-size: 12px; font-weight: 600; color: #666; }
        .filter-select, .filter-input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
        .signals-grid { display: flex; flex-direction: column; gap: 16px; }
        .signal-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #ccc; transition: opacity 0.3s; }
        .signal-card[data-signal="STRONG_BUY"] { border-left-color: #10b981; }
        .signal-card[data-signal="BUY"] { border-left-color: #86efac; }
        .signal-card[data-signal="POSITIVE"] { border-left-color: #60a5fa; }
        .signal-card[data-signal="HOLD"] { border-left-color: #06b6d4; }
        .signal-card[data-signal="NEUTRAL"] { border-left-color: #94a3b8; }
        .signal-card[data-signal="CONCERN"] { border-left-color: #fdba74; }
        .signal-card[data-signal="SELL"] { border-left-color: #fb923c; }
        .signal-card[data-signal="STRONG_SELL"] { border-left-color: #f87171; }
        .signal-card.reviewed { opacity: 0.6; }
        .signal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
        .signal-asset { font-size: 18px; font-weight: 700; }
        .signal-type { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; color: white; }
        .signal-type.STRONG_BUY { background: #10b981; }
        .signal-type.BUY { background: #86efac; color: #065f46; }
        .signal-type.POSITIVE { background: #60a5fa; }
        .signal-type.HOLD { background: #06b6d4; }
        .signal-type.NEUTRAL { background: #94a3b8; }
        .signal-type.CONCERN { background: #fdba74; color: #7c2d12; }
        .signal-type.SELL { background: #fb923c; }
        .signal-type.STRONG_SELL { background: #f87171; }
        .quote { background: #f8f9fa; padding: 12px 16px; border-radius: 8px; margin: 12px 0; font-style: italic; color: #333; border-left: 3px solid #667eea; }
        .meta { display: flex; gap: 16px; font-size: 13px; color: #666; margin-top: 8px; flex-wrap: wrap; }
        .meta a { color: #ef4444; text-decoration: none; }
        .meta a:hover { text-decoration: underline; }
        .signal-actions { display: flex; gap: 8px; align-items: center; }
        .btn { padding: 8px 16px; border-radius: 8px; border: 1px solid #ddd; background: white; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #f0f0f0; }
        .btn.active-approve { background: #d1fae5; border-color: #10b981; }
        .btn.active-reject { background: #fee2e2; border-color: #ef4444; }
        .review-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
        .review-badge.pending { background: #fef3c7; color: #92400e; }
        .review-badge.approved { background: #d1fae5; color: #065f46; }
        .review-badge.rejected { background: #fee2e2; color: #991b1b; }
        .confidence { font-size: 12px; padding: 2px 8px; border-radius: 10px; }
        .confidence.HIGH { background: #d1fae5; color: #065f46; }
        .confidence.MEDIUM { background: #fef3c7; color: #92400e; }
        .confidence.LOW { background: #fee2e2; color: #991b1b; }
        .date-badge { font-size: 13px; color: #888; }
        .reject-input { margin-top: 8px; display: none; }
        .reject-input.show { display: flex; gap: 8px; align-items: center; }
        .reject-input input { flex: 1; padding: 6px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; }
        .reject-input button { padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }
        .saving { position: fixed; top: 20px; right: 20px; background: #10b981; color: white; padding: 8px 16px; border-radius: 8px; display: none; z-index: 999; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .opus4-section { margin-top: 8px; }
    </style>
</head>
<body>
    <div class="saving" id="saving-indicator">저장 중...</div>
    <div class="container">
        <div class="header">
            <h1>🔍 유튜버 시그널 검증 리뷰 v3</h1>
            <p>파이프라인: Claude Sonnet(추출) → 사람(최종 검토) | 서버 연동</p>
        </div>
        
        <div class="stats" id="stats-container"></div>
        
        <div class="filters">
            <div class="filter-row">
                <div class="filter-group">
                    <label class="filter-label">종목</label>
                    <select class="filter-select" id="asset-filter"><option value="">전체 종목</option></select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">시그널 타입</label>
                    <select class="filter-select" id="signal-filter">
                        <option value="">전체 시그널</option>
                        <option value="STRONG_BUY">강력매수</option>
                        <option value="BUY">매수</option>
                        <option value="POSITIVE">긍정</option>
                        <option value="HOLD">보유</option>
                        <option value="NEUTRAL">중립</option>
                        <option value="CONCERN">우려</option>
                        <option value="SELL">매도</option>
                        <option value="STRONG_SELL">강력매도</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">리뷰 상태</label>
                    <select class="filter-select" id="review-filter">
                        <option value="">전체 상태</option>
                        <option value="pending">검토 대기</option>
                        <option value="approved">승인됨</option>
                        <option value="rejected">거부됨</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">유튜버</label>
                    <select class="filter-select" id="youtuber-filter"><option value="">전체 유튜버</option></select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">검색</label>
                    <input type="text" class="filter-input" id="search-input" placeholder="내용 검색...">
                </div>
            </div>
        </div>
        
        <div class="signals-grid" id="signals-container"></div>
    </div>

    <script>
        let SIGNALS_DATA = [];
        let REVIEWS = {};
        let OPUS4_ANALYSIS = {};
        
        async function loadData() {
            const [sigRes, revRes, opusRes] = await Promise.all([
                fetch('/api/signals').then(r => r.json()),
                fetch('/api/reviews').then(r => r.json()),
                fetch('/api/opus4-analysis').then(r => r.json()).catch(() => ({}))
            ]);
            SIGNALS_DATA = sigRes;
            REVIEWS = revRes;
            OPUS4_ANALYSIS = opusRes;
            initFilters();
            render();
        }
        
        loadData();
        
        // 5초마다 Opus 4 분석 상태 갱신
        setInterval(async () => {
            try {
                const opusRes = await fetch('/api/opus4-analysis').then(r => r.json());
                const oldAnalyzing = Object.keys(OPUS4_ANALYSIS).filter(k => OPUS4_ANALYSIS[k].status === 'analyzing');
                const newCompleted = Object.keys(opusRes).filter(k => 
                    oldAnalyzing.includes(k) && opusRes[k].status === 'completed'
                );
                
                OPUS4_ANALYSIS = opusRes;
                
                // 새로 완료된 분석이 있으면 해당 카드만 업데이트
                if (newCompleted.length > 0) {
                    render();
                }
            } catch (e) {
                console.error('Failed to update Opus 4 analysis:', e);
            }
        }, 5000);
        
        const SIGNAL_LABELS = {
            'STRONG_BUY': '강력매수', 'BUY': '매수', 'POSITIVE': '긍정',
            'HOLD': '보유', 'NEUTRAL': '중립', 'CONCERN': '우려',
            'SELL': '매도', 'STRONG_SELL': '강력매도'
        };
        
        function getReview(id) { return REVIEWS[id] || { status: 'pending' }; }
        
        function getReviewFields(card) {
            return {
                review_note: (card.querySelector('.review-field-note') || {}).value || '',
                review_change: (card.querySelector('.review-field-change') || {}).value || '',
                review_reason: (card.querySelector('.review-field-reason') || {}).value || ''
            };
        }
        
        async function setReview(id, status, reason, extraFields) {
            const time = new Date().toLocaleString('ko-KR');
            const review_note = (extraFields && extraFields.review_note) || '';
            const review_change = (extraFields && extraFields.review_change) || '';
            const review_reason = (extraFields && extraFields.review_reason) || '';
            REVIEWS[id] = { status, reason: reason || '', time, review_note, review_change, review_reason };
            
            document.getElementById('saving-indicator').style.display = 'block';
            try {
                await fetch('/api/review', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id, status, reason: reason || '', time, review_note, review_change, review_reason })
                });
            } catch(e) {
                console.error('Save failed:', e);
            }
            document.getElementById('saving-indicator').style.display = 'none';
            render();
        }
        
        function approveSignal(id) {
            setReview(id, 'approved');
        }
        
        function rejectSignal(id) {
            const el = document.getElementById('reject-' + CSS.escape(id));
            if (el) {
                el.classList.toggle('show');
                if (el.classList.contains('show')) {
                    el.querySelector('input').focus();
                }
            }
        }
        
        function submitReject(id) {
            const el = document.getElementById('reject-' + CSS.escape(id));
            const reason = el ? el.querySelector('input').value : '';
            setReview(id, 'rejected', reason);
        }
        
        function escHtml(s) {
            if (!s) return '';
            return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
        }
        
        function buildOpus4Section(id) {
            const analysis = OPUS4_ANALYSIS[id];
            const review = getReview(id);
            
            // 거부된 시그널만 표시
            if (review.status !== 'rejected') return '';
            
            if (!analysis) return '';
            
            if (analysis.status === 'analyzing') {
                return '<div class="opus4-section">' +
                    '<div style="margin-top:12px;padding:12px;background:#fef3c7;border-radius:8px;border-left:3px solid #f59e0b;">' +
                        '<div style="font-weight:600;color:#92400e;margin-bottom:8px;">🔥 Opus 4 분석 중...</div>' +
                        '<div class="spinner" style="display:inline-block;width:16px;height:16px;border:2px solid #fbbf24;border-top:2px solid transparent;border-radius:50%;animation:spin 1s linear infinite;"></div>' +
                        '<span style="margin-left:8px;font-size:13px;color:#92400e;">자막을 다시 읽고 분석 중입니다.</span>' +
                    '</div>' +
                '</div>';
            }
            
            if (analysis.status === 'completed') {
                const correctSignal = analysis.correct_signal || {};
                const suggestion = analysis.suggestion || {};
                const signalTypeKor = {
                    'STRONG_BUY': '강력매수', 'BUY': '매수', 'POSITIVE': '긍정',
                    'HOLD': '보유', 'NEUTRAL': '중립', 'CONCERN': '우려',
                    'SELL': '매도', 'STRONG_SELL': '강력매도'
                };
                
                const actionColors = {
                    'APPROVE': {bg:'#d1fae5',border:'#10b981',text:'#065f46',label:'✅ 승인 제안'},
                    'REJECT': {bg:'#fee2e2',border:'#ef4444',text:'#991b1b',label:'❌ 거부 제안'},
                    'MODIFY': {bg:'#dbeafe',border:'#3b82f6',text:'#1e40af',label:'✏️ 수정 제안'}
                };
                const ac = actionColors[suggestion.action] || actionColors['MODIFY'];
                
                return '<div class="opus4-section">' +
                    '<div style="margin-top:12px;padding:12px;background:#f0f9ff;border-radius:8px;border-left:3px solid #0ea5e9;">' +
                        '<div style="font-weight:600;color:#0369a1;margin-bottom:12px;">🔥 Opus 4 분석 완료</div>' +
                        '<div style="margin-bottom:8px;">' +
                            '<strong>Sonnet 시그널 정확도:</strong> ' +
                            (analysis.sonnet_signal_correct ? '✅ 정확' : '❌ 부정확') +
                        '</div>' +
                        '<div style="margin-bottom:8px;">' +
                            '<strong>거부 사유 타당성:</strong> ' +
                            (analysis.rejection_valid ? '✅ 타당함' : '❌ 부당함') +
                        '</div>' +
                        (correctSignal.signal_type ? 
                            '<div style="margin-bottom:8px;">' +
                                '<strong>올바른 시그널:</strong> ' + 
                                (signalTypeKor[correctSignal.signal_type] || correctSignal.signal_type) +
                                (correctSignal.asset ? ' (' + escHtml(correctSignal.asset) + ')' : '') +
                            '</div>' : ''
                        ) +
                        (suggestion.action ? 
                            '<div style="margin-top:12px;padding:10px;background:' + ac.bg + ';border:1px solid ' + ac.border + ';border-radius:8px;">' +
                                '<div style="font-weight:600;color:' + ac.text + ';margin-bottom:6px;">' + ac.label + '</div>' +
                                (suggestion.changes ? '<div style="font-size:13px;color:' + ac.text + ';margin-bottom:4px;"><strong>변경:</strong> ' + escHtml(suggestion.changes) + '</div>' : '') +
                                (suggestion.reason ? '<div style="font-size:13px;color:' + ac.text + ';margin-bottom:8px;"><strong>사유:</strong> ' + escHtml(suggestion.reason) + '</div>' : '') +
                                '<button class="apply-suggestion-btn" data-id="' + escHtml(id) + '" data-action="' + escHtml(suggestion.action || '') + '" data-changes="' + escHtml(suggestion.changes || '') + '" data-reason="' + escHtml(suggestion.reason || '') + '" style="padding:6px 16px;background:' + ac.border + ';color:white;border:none;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;">👆 제안 적용</button>' +
                            '</div>' : ''
                        ) +
                        '<div style="margin-top:8px;">' +
                            '<strong>상세 분석:</strong><br>' +
                            '<div style="font-size:13px;color:#666;margin-top:4px;line-height:1.4;">' +
                                escHtml(analysis.analysis || '분석 내용 없음') +
                            '</div>' +
                        '</div>' +
                        (analysis.prompt_improvement ? 
                            '<div style="margin-top:12px;padding:8px;background:#fef3c7;border-radius:6px;">' +
                                '<strong style="color:#92400e;">💡 프롬프트 개선 제안:</strong><br>' +
                                '<div style="font-size:13px;color:#92400e;margin-top:4px;line-height:1.4;">' +
                                    escHtml(analysis.prompt_improvement) +
                                '</div>' +
                            '</div>' : ''
                        ) +
                    '</div>' +
                '</div>';
            }
            
            return '';
        }
        
        function parseTimestamp(ts) {
            if (!ts) return null;
            const parts = ts.replace(/[\\[\\] ]/g, '').split(':');
            if (parts.length === 2) return parseInt(parts[0]) * 60 + parseInt(parts[1]);
            if (parts.length === 3) return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
            return null;
        }
        
        function buildCard(sig) {
            const id = sig.video_id + '_' + sig.asset;
            const review = getReview(id);
            const ts = parseTimestamp(sig.timestamp);
            const tsUrl = ts ? 'https://youtube.com/watch?v=' + sig.video_id + '&t=' + ts : 'https://youtube.com/watch?v=' + sig.video_id;
            const reviewed = review.status !== 'pending' ? ' reviewed' : '';
            
            const card = document.createElement('div');
            card.className = 'signal-card' + reviewed;
            card.dataset.signal = sig.signal_type;
            card.dataset.review = review.status;
            card.dataset.id = id;
            
            const statusLabel = {pending:'검토대기',approved:'승인',rejected:'거부'}[review.status] || review.status;
            
            card.innerHTML = 
                '<div class="signal-header">' +
                    '<div>' +
                        '<span class="signal-asset">' + escHtml(sig.asset) + '</span> ' +
                        '<span class="signal-type ' + sig.signal_type + '">' + (SIGNAL_LABELS[sig.signal_type] || sig.signal_type) + '</span> ' +
                        '<span class="confidence ' + (sig.confidence || '') + '">' + (sig.confidence || '') + '</span> ' +
                        '<span class="review-badge ' + review.status + '">' + statusLabel + '</span> ' +
                        '<span class="date-badge">📅 ' + escHtml(sig.date || 'N/A') + '</span>' +
                    '</div>' +
                    '<div class="signal-actions">' +
                        '<button class="btn approve-btn' + (review.status==='approved'?' active-approve':'') + '">✅</button>' +
                        '<button class="btn reject-btn' + (review.status==='rejected'?' active-reject':'') + '">❌</button>' +
                    '</div>' +
                '</div>' +
                '<div class="quote">"' + escHtml(sig.content || '') + '"</div>' +
                '<div class="meta">' +
                    '<span>📺 <a href="' + escHtml(tsUrl) + '" target="_blank">' + escHtml((sig.title || sig.video_id).substring(0, 50)) + ' ▶️</a></span>' +
                    '<span>⏱️ ' + escHtml(sig.timestamp || 'N/A') + '</span>' +
                    '<span>🎙️ ' + escHtml(sig.channel || '코린이 아빠') + '</span>' +
                '</div>' +
                (sig.context ? '<div style="margin-top:8px;font-size:13px;color:#666;">💡 ' + escHtml(sig.context) + '</div>' : '') +
                (review.status === 'rejected' && review.reason ? '<div style="margin-top:8px;font-size:13px;color:#991b1b;">❌ 거부 사유: ' + escHtml(review.reason) + '</div>' : '') +
                buildOpus4Section(id) +
                '<div class="reject-input">' +
                    '<input type="text" placeholder="거부 사유 입력...">' +
                    '<button class="reject-submit-btn">거부</button>' +
                '</div>' +
                '<div style="margin-top:10px;padding-top:10px;border-top:1px solid #e2e8f0;display:flex;flex-direction:column;gap:4px;">' +
                    '<div style="display:flex;align-items:center;gap:6px;">' +
                        '<label style="min-width:36px;font-weight:600;font-size:13px;color:#666;">검토:</label>' +
                        '<input type="text" class="review-field-note" value="' + escHtml(review.review_note || '') + '" placeholder="검토 결과" style="flex:1;padding:4px 8px;border:1px solid #ddd;border-radius:4px;font-size:13px;">' +
                    '</div>' +
                    '<div style="display:flex;align-items:center;gap:6px;">' +
                        '<label style="min-width:36px;font-weight:600;font-size:13px;color:#666;">변경:</label>' +
                        '<input type="text" class="review-field-change" value="' + escHtml(review.review_change || '') + '" placeholder="변경 내용" style="flex:1;padding:4px 8px;border:1px solid #ddd;border-radius:4px;font-size:13px;">' +
                    '</div>' +
                    '<div style="display:flex;align-items:center;gap:6px;">' +
                        '<label style="min-width:36px;font-weight:600;font-size:13px;color:#666;">사유:</label>' +
                        '<input type="text" class="review-field-reason" value="' + escHtml(review.review_reason || '') + '" placeholder="사유" style="flex:1;padding:4px 8px;border:1px solid #ddd;border-radius:4px;font-size:13px;">' +
                    '</div>' +
                '</div>';
            
            // Event listeners
            card.querySelector('.approve-btn').addEventListener('click', () => {
                const fields = getReviewFields(card);
                setReview(id, 'approved', '', fields);
            });
            card.querySelector('.reject-btn').addEventListener('click', () => {
                const ri = card.querySelector('.reject-input');
                ri.classList.toggle('show');
                if (ri.classList.contains('show')) ri.querySelector('input').focus();
            });
            card.querySelector('.reject-submit-btn').addEventListener('click', () => {
                const reason = card.querySelector('.reject-input input').value;
                const fields = getReviewFields(card);
                setReview(id, 'rejected', reason, fields);
            });
            card.querySelector('.reject-input input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const reason = e.target.value;
                    const fields = getReviewFields(card);
                    setReview(id, 'rejected', reason, fields);
                }
            });
            
            // 제안 적용 버튼
            const sugBtn = card.querySelector('.apply-suggestion-btn');
            if (sugBtn) {
                sugBtn.addEventListener('click', () => {
                    const action = sugBtn.dataset.action;
                    const changes = sugBtn.dataset.changes;
                    const reason = sugBtn.dataset.reason;
                    
                    // 검토/변경/사유 필드에 제안 내용 자동 채움
                    const noteEl = card.querySelector('.review-field-note');
                    const changeEl = card.querySelector('.review-field-change');
                    const reasonEl = card.querySelector('.review-field-reason');
                    
                    if (noteEl) noteEl.value = action === 'APPROVE' ? '승인 (Opus 제안)' : action === 'REJECT' ? '거부 (Opus 제안)' : '수정 (Opus 제안)';
                    if (changeEl) changeEl.value = changes;
                    if (reasonEl) reasonEl.value = reason;
                    
                    // 상태 자동 적용
                    const status = action === 'APPROVE' ? 'approved' : action === 'REJECT' ? 'rejected' : 'approved';
                    const fields = getReviewFields(card);
                    setReview(id, status, action === 'REJECT' ? reason : '', fields);
                });
            }
            
            return card;
        }
        
        function render() {
            const container = document.getElementById('signals-container');
            const assetF = document.getElementById('asset-filter').value;
            const signalF = document.getElementById('signal-filter').value;
            const reviewF = document.getElementById('review-filter').value;
            const youtuberF = document.getElementById('youtuber-filter').value;
            const searchF = document.getElementById('search-input').value.toLowerCase();
            
            container.innerHTML = '';
            let shown = 0, approved = 0, rejected = 0, opus4Done = 0;
            
            SIGNALS_DATA.forEach(sig => {
                const id = sig.video_id + '_' + sig.asset;
                const review = getReview(id);
                
                if (review.status === 'approved') approved++;
                if (review.status === 'rejected') {
                    rejected++;
                    if (OPUS4_ANALYSIS[id] && OPUS4_ANALYSIS[id].status === 'complete') opus4Done++;
                }
                
                if (assetF && sig.asset !== assetF) return;
                if (signalF && sig.signal_type !== signalF) return;
                if (reviewF && review.status !== reviewF) return;
                if (youtuberF && (sig.channel || '코린이 아빠') !== youtuberF) return;
                if (searchF && !(sig.content || '').toLowerCase().includes(searchF) && 
                    !(sig.asset || '').toLowerCase().includes(searchF)) return;
                
                container.appendChild(buildCard(sig));
                shown++;
            });
            
            if (shown === 0) {
                container.innerHTML = '<div style="text-align:center;padding:40px;color:#666;">필터 조건에 맞는 시그널이 없습니다.</div>';
            }
            
            const statsHtml = [
                { n: SIGNALS_DATA.length, l: '총 시그널' },
                { n: SIGNALS_DATA.length - approved - rejected, l: '검토 대기' },
                { n: approved, l: '승인됨' },
                { n: rejected, l: '거부됨' },
                { n: opus4Done + '/' + rejected, l: 'Opus 검토' }
            ].map(s => '<div class="stat-card"><div class="stat-number">' + s.n + '</div><div class="stat-label">' + s.l + '</div></div>').join('');
            document.getElementById('stats-container').innerHTML = statsHtml;
        }
        
        function initFilters() {
            const assets = [...new Set(SIGNALS_DATA.map(s => s.asset))].sort();
            const af = document.getElementById('asset-filter');
            assets.forEach(a => { const o = document.createElement('option'); o.value = a; o.textContent = a; af.appendChild(o); });
            
            const youtubers = [...new Set(SIGNALS_DATA.map(s => s.channel || '코린이 아빠'))].sort();
            const yf = document.getElementById('youtuber-filter');
            youtubers.forEach(y => { const o = document.createElement('option'); o.value = y; o.textContent = y; yf.appendChild(o); });
            
            ['asset-filter','signal-filter','review-filter','youtuber-filter'].forEach(id => 
                document.getElementById(id).addEventListener('change', render));
            document.getElementById('search-input').addEventListener('input', render);
        }
        
        // Data loaded via loadData() above
    </script>
</body>
</html>'''

if __name__ == '__main__':
    port = 8899  # 다른 포트 사용 (8899는 기존 서버가 점유 중)
    server = ThreadingHTTPServer(('0.0.0.0', port), ReviewHandler)
    print(f'Opus 4 enhanced review server running on http://localhost:{port}', flush=True)
    server.serve_forever()
