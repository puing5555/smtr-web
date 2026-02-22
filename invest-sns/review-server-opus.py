"""Signal Review Web Server - OPUS 4 version for comparison"""
import json, os, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

REVIEW_FILE = os.path.join('smtr_data', 'corinpapa1106', '_opus4_review_results.json')
SIGNALS_FILE = os.path.join('smtr_data', 'corinpapa1106', '_opus4_deduped_signals.json')

def load_reviews():
    if os.path.exists(REVIEW_FILE):
        with open(REVIEW_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_reviews(data):
    with open(REVIEW_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
            signals.sort(key=lambda s: s.get('date', ''), reverse=True)
            self.wfile.write(json.dumps(signals, ensure_ascii=False).encode('utf-8'))
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
            reviews[sig_id] = {
                'status': data.get('status', 'pending'),
                'reason': data.get('reason', ''),
                'time': data.get('time', '')
            }
            save_reviews(reviews)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))
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
        pass

def build_review_html(signals, reviews):
    return '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 OPUS 4 시그널 검증 리뷰</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f0f23; color: #e2e8f0; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); color: white; padding: 30px; border-radius: 16px; margin-bottom: 24px; }
        .header h1 { font-size: 24px; margin-bottom: 8px; }
        .header p { opacity: 0.9; font-size: 14px; }
        .model-badge { display: inline-block; background: rgba(0,0,0,0.3); padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-top: 8px; }
        .stats { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
        .stat-card { background: #1a1a2e; border-radius: 12px; padding: 16px 20px; flex: 1; min-width: 120px; text-align: center; border: 1px solid #2d2d44; }
        .stat-number { font-size: 28px; font-weight: 700; color: #f59e0b; }
        .stat-label { font-size: 12px; color: #888; margin-top: 4px; }
        .filters { background: #1a1a2e; border-radius: 12px; padding: 20px; margin-bottom: 24px; border: 1px solid #2d2d44; }
        .filter-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: end; }
        .filter-group { display: flex; flex-direction: column; gap: 4px; }
        .filter-label { font-size: 12px; font-weight: 600; color: #888; }
        .filter-select, .filter-input { padding: 8px 12px; border: 1px solid #2d2d44; border-radius: 8px; font-size: 14px; background: #0f0f23; color: #e2e8f0; }
        .signals-grid { display: flex; flex-direction: column; gap: 16px; }
        .signal-card { background: #1a1a2e; border-radius: 12px; padding: 20px; border: 1px solid #2d2d44; border-left: 4px solid #444; transition: opacity 0.3s; }
        .signal-card[data-signal="STRONG_BUY"] { border-left-color: #10b981; }
        .signal-card[data-signal="BUY"] { border-left-color: #86efac; }
        .signal-card[data-signal="POSITIVE"] { border-left-color: #60a5fa; }
        .signal-card[data-signal="HOLD"] { border-left-color: #06b6d4; }
        .signal-card[data-signal="NEUTRAL"] { border-left-color: #94a3b8; }
        .signal-card[data-signal="CONCERN"] { border-left-color: #fdba74; }
        .signal-card[data-signal="SELL"] { border-left-color: #fb923c; }
        .signal-card[data-signal="STRONG_SELL"] { border-left-color: #f87171; }
        .signal-card.reviewed { opacity: 0.5; }
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
        .quote { background: #0f0f23; padding: 12px 16px; border-radius: 8px; margin: 12px 0; font-style: italic; color: #ccc; border-left: 3px solid #f59e0b; }
        .meta { display: flex; gap: 16px; font-size: 13px; color: #888; margin-top: 8px; flex-wrap: wrap; }
        .meta a { color: #ef4444; text-decoration: none; }
        .meta a:hover { text-decoration: underline; }
        .signal-actions { display: flex; gap: 8px; align-items: center; }
        .btn { padding: 8px 16px; border-radius: 8px; border: 1px solid #2d2d44; background: #1a1a2e; cursor: pointer; font-size: 16px; color: #e2e8f0; }
        .btn:hover { background: #2d2d44; }
        .btn.active-approve { background: #065f46; border-color: #10b981; }
        .btn.active-reject { background: #7f1d1d; border-color: #ef4444; }
        .review-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
        .review-badge.pending { background: #422006; color: #f59e0b; }
        .review-badge.approved { background: #052e16; color: #4ade80; }
        .review-badge.rejected { background: #450a0a; color: #fca5a5; }
        .confidence { font-size: 12px; padding: 2px 8px; border-radius: 10px; }
        .confidence.HIGH { background: #052e16; color: #4ade80; }
        .confidence.MEDIUM { background: #422006; color: #f59e0b; }
        .confidence.LOW { background: #450a0a; color: #fca5a5; }
        .date-badge { font-size: 13px; color: #666; }
        .reject-input { margin-top: 8px; display: none; }
        .reject-input.show { display: flex; gap: 8px; align-items: center; }
        .reject-input input { flex: 1; padding: 6px 10px; border: 1px solid #2d2d44; border-radius: 6px; font-size: 13px; background: #0f0f23; color: #e2e8f0; }
        .reject-input button { padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }
        .saving { position: fixed; top: 20px; right: 20px; background: #f59e0b; color: black; padding: 8px 16px; border-radius: 8px; display: none; z-index: 999; font-weight: 600; }
    </style>
</head>
<body>
    <div class="saving" id="saving-indicator">저장중..</div>
    <div class="container">
        <div class="header">
            <h1>🧠 OPUS 4 시그널 검증 리뷰</h1>
            <p>Claude Opus 4 (claude-opus-4-20250514) 추출 결과 | Sonnet 결과와 비교용</p>
            <div class="model-badge">🔥 claude-opus-4-20250514 | 129 signals | $22.65</div>
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
                        <option value="pending">검토대기</option>
                        <option value="approved">승인</option>
                        <option value="rejected">거절</option>
                    </select>
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
        
        async function loadData() {
            const [sigRes, revRes] = await Promise.all([
                fetch('/api/signals').then(r => r.json()),
                fetch('/api/reviews').then(r => r.json())
            ]);
            SIGNALS_DATA = sigRes;
            REVIEWS = revRes;
            initFilters();
            render();
        }
        
        loadData();
        
        const SIGNAL_LABELS = {
            'STRONG_BUY': '강력매수', 'BUY': '매수', 'POSITIVE': '긍정',
            'HOLD': '보유', 'NEUTRAL': '중립', 'CONCERN': '우려',
            'SELL': '매도', 'STRONG_SELL': '강력매도'
        };
        
        function getReview(id) { return REVIEWS[id] || { status: 'pending' }; }
        
        async function setReview(id, status, reason) {
            const time = new Date().toLocaleString('ko-KR');
            REVIEWS[id] = { status, reason: reason || '', time };
            
            document.getElementById('saving-indicator').style.display = 'block';
            try {
                await fetch('/api/review', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id, status, reason: reason || '', time })
                });
            } catch(e) { console.error('Save failed:', e); }
            document.getElementById('saving-indicator').style.display = 'none';
            render();
        }
        
        function escHtml(s) {
            if (!s) return '';
            return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
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
            
            const statusLabel = {pending:'검토대기',approved:'승인',rejected:'거절'}[review.status] || review.status;
            
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
                    '<span>🎬 <a href="' + escHtml(tsUrl) + '" target="_blank">' + escHtml((sig.title || sig.video_id).substring(0, 50)) + ' ▶️</a></span>' +
                    '<span>⏱️ ' + escHtml(sig.timestamp || 'N/A') + '</span>' +
                    '<span>🎙️ ' + escHtml(sig.channel || '코린이 아빠') + '</span>' +
                '</div>' +
                (sig.context ? '<div style="margin-top:8px;font-size:13px;color:#888;">💡 ' + escHtml(sig.context) + '</div>' : '') +
                (review.status === 'rejected' && review.reason ? '<div style="margin-top:8px;font-size:13px;color:#fca5a5;">⛔ 거절 사유: ' + escHtml(review.reason) + '</div>' : '') +
                '<div class="reject-input">' +
                    '<input type="text" placeholder="거절 사유 입력...">' +
                    '<button class="reject-submit-btn">거절</button>' +
                '</div>';
            
            card.querySelector('.approve-btn').addEventListener('click', () => setReview(id, 'approved'));
            card.querySelector('.reject-btn').addEventListener('click', () => {
                const ri = card.querySelector('.reject-input');
                ri.classList.toggle('show');
                if (ri.classList.contains('show')) ri.querySelector('input').focus();
            });
            card.querySelector('.reject-submit-btn').addEventListener('click', () => {
                const reason = card.querySelector('.reject-input input').value;
                setReview(id, 'rejected', reason);
            });
            card.querySelector('.reject-input input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') setReview(id, 'rejected', e.target.value);
            });
            
            return card;
        }
        
        function render() {
            const container = document.getElementById('signals-container');
            const assetF = document.getElementById('asset-filter').value;
            const signalF = document.getElementById('signal-filter').value;
            const reviewF = document.getElementById('review-filter').value;
            const searchF = document.getElementById('search-input').value.toLowerCase();
            
            container.innerHTML = '';
            let shown = 0, approved = 0, rejected = 0;
            
            SIGNALS_DATA.forEach(sig => {
                const id = sig.video_id + '_' + sig.asset;
                const review = getReview(id);
                
                if (review.status === 'approved') approved++;
                if (review.status === 'rejected') rejected++;
                
                if (assetF && sig.asset !== assetF) return;
                if (signalF && sig.signal_type !== signalF) return;
                if (reviewF && review.status !== reviewF) return;
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
                { n: SIGNALS_DATA.length - approved - rejected, l: '검토대기' },
                { n: approved, l: '승인' },
                { n: rejected, l: '거절' },
                { n: shown, l: '현재 표시' }
            ].map(s => '<div class="stat-card"><div class="stat-number">' + s.n + '</div><div class="stat-label">' + s.l + '</div></div>').join('');
            document.getElementById('stats-container').innerHTML = statsHtml;
        }
        
        function initFilters() {
            const assets = [...new Set(SIGNALS_DATA.map(s => s.asset))].sort();
            const af = document.getElementById('asset-filter');
            assets.forEach(a => { const o = document.createElement('option'); o.value = a; o.textContent = a; af.appendChild(o); });
            
            ['asset-filter','signal-filter','review-filter'].forEach(id => 
                document.getElementById(id).addEventListener('change', render));
            document.getElementById('search-input').addEventListener('input', render);
        }
    </script>
</body>
</html>'''

if __name__ == '__main__':
    port = 8900
    server = HTTPServer(('0.0.0.0', port), ReviewHandler)
    print(f'OPUS 4 Review server running on http://localhost:{port}', flush=True)
    server.serve_forever()
