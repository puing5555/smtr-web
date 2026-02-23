"""Signal Review Web Server v5 - with Opus Review Integration"""
import json, os, sys, threading, time, re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
import anthropic
from datetime import datetime

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

# 파일 경로들
SIGNALS_FILE = 'smtr_data/corinpapa1106/_deduped_signals_8types_dated.json'
REVIEW_FILE = '_review_results_v5.json'
OPUS_REVIEW_FILE = '_opus_review_results.json'

# Anthropic 클라이언트 초기화
try:
    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
except Exception as e:
    print(f"Warning: Anthropic client init failed: {e}")
    client = None

# 전역 상태
opus_progress = {"current": 0, "total": 0, "status": "idle"}

def load_signals():
    """시그널 데이터 로드"""
    try:
        with open(SIGNALS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading signals: {e}")
        return []

def load_reviews():
    """리뷰 결과 로드"""
    if os.path.exists(REVIEW_FILE):
        try:
            with open(REVIEW_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_reviews(data):
    """리뷰 결과 저장"""
    with open(REVIEW_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_opus_reviews():
    """Opus 리뷰 결과 로드"""
    if os.path.exists(OPUS_REVIEW_FILE):
        try:
            with open(OPUS_REVIEW_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_opus_reviews(data):
    """Opus 리뷰 결과 저장"""
    with open(OPUS_REVIEW_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_subtitle_content(video_id):
    """자막 파일 내용 읽기"""
    subtitle_file = f'smtr_data/corinpapa1106/{video_id}.txt'
    if os.path.exists(subtitle_file):
        try:
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    return None

def opus_analyze_signal(signal):
    """Opus로 시그널 분석"""
    if not client:
        return {"error": "Anthropic client not available"}
    
    video_id = signal.get('video_id')
    if not video_id:
        return {"error": "video_id not found"}
    
    subtitle_content = get_subtitle_content(video_id)
    if not subtitle_content:
        return {"error": f"Subtitle file not found for video {video_id}"}
    
    try:
        prompt = f"""다음은 유튜브 영상 자막과 Claude Sonnet이 추출한 시그널입니다.

**영상 자막:**
{subtitle_content}

**Sonnet이 추출한 시그널:**
- 종목: {signal.get('asset', 'N/A')}
- 시그널 타입: {signal.get('signal_type', 'N/A')}
- 내용: {signal.get('content', 'N/A')}
- 타임스탬프: {signal.get('timestamp', 'N/A')}
- 신뢰도: {signal.get('confidence', 'N/A')}

**시그널 타입 정의 (절대 변경 금지):**
STRONG_BUY / BUY / POSITIVE / HOLD / NEUTRAL / CONCERN / SELL / STRONG_SELL

**분석 요청:**
자막을 처음부터 끝까지 읽고 다음을 분석해주세요:

1. Sonnet이 추출한 시그널이 자막 내용과 일치하는지 검증
2. 시그널의 정확성과 타당성 평가
3. 승인/거부/수정 권고

JSON 형식으로 답변:
{{
  "verdict": "approve|reject|modify",
  "confidence": "HIGH|MEDIUM|LOW",
  "reasoning": "상세한 분석 내용 (한국어)",
  "suggested_changes": {{
    "signal_type": "수정된 시그널 타입 (필요시)",
    "asset": "수정된 종목명 (필요시)",
    "content": "수정된 내용 (필요시)",
    "timestamp": "수정된 타임스탬프 (필요시)"
  }}
}}
"""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # JSON 응답 파싱
        try:
            result = json.loads(response.content[0].text)
            result['analysis_timestamp'] = datetime.now().isoformat()
            return result
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response.content[0].text
            }
            
    except Exception as e:
        return {"error": str(e)}

def opus_analyze_all_signals():
    """모든 시그널에 대해 Opus 분석 실행"""
    def analyze_all():
        global opus_progress
        signals = load_signals()
        opus_reviews = load_opus_reviews()
        
        opus_progress = {"current": 0, "total": len(signals), "status": "running"}
        
        for i, signal in enumerate(signals):
            signal_id = f"{signal.get('video_id', '')}_{signal.get('asset', '')}_{i}"
            
            # 이미 분석된 것은 건너뛰기
            if signal_id in opus_reviews:
                opus_progress["current"] = i + 1
                continue
            
            opus_progress["current"] = i + 1
            
            # Opus 분석 실행
            result = opus_analyze_signal(signal)
            
            # 결과 저장
            opus_reviews[signal_id] = {
                **result,
                "signal_data": signal,
                "timestamp": datetime.now().isoformat()
            }
            save_opus_reviews(opus_reviews)
            
            # 0.5초 딜레이 (API 제한 고려)
            time.sleep(0.5)
        
        opus_progress["status"] = "completed"
    
    # 백그라운드에서 실행
    threading.Thread(target=analyze_all, daemon=True).start()

def build_html():
    """HTML 페이지 생성"""
    signals = load_signals()
    reviews = load_reviews()
    opus_reviews = load_opus_reviews()
    
    # 통계 계산
    total_signals = len(signals)
    reviewed_count = len([k for k, v in reviews.items() if v.get('status') in ['approved', 'rejected']])
    approved_count = len([k for k, v in reviews.items() if v.get('status') == 'approved'])
    rejected_count = len([k for k, v in reviews.items() if v.get('status') == 'rejected'])
    pending_count = total_signals - reviewed_count
    opus_approved = len([k for k, v in opus_reviews.items() if v.get('verdict') == 'approve'])
    opus_rejected = len([k for k, v in opus_reviews.items() if v.get('verdict') == 'reject'])
    
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>시그널 리뷰 v5 - Opus 통합</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f4f8; color: #1a1a2e; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 16px; margin-bottom: 24px; position: relative; }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .header p {{ opacity: 0.9; font-size: 14px; margin-bottom: 16px; }}
        .opus-btn {{ position: absolute; top: 20px; right: 20px; background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 10px 16px; border-radius: 8px; cursor: pointer; font-size: 14px; transition: all 0.3s; }}
        .opus-btn:hover {{ background: rgba(255,255,255,0.3); }}
        .opus-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}
        .progress-container {{ margin-top: 12px; }}
        .progress-bar {{ width: 100%; height: 6px; background: rgba(255,255,255,0.2); border-radius: 3px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: #4ade80; transition: width 0.3s; }}
        .stats {{ display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }}
        .stat-card {{ background: white; border-radius: 12px; padding: 16px 20px; flex: 1; min-width: 120px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .stat-number {{ font-size: 28px; font-weight: 700; color: #667eea; }}
        .stat-label {{ font-size: 12px; color: #666; margin-top: 4px; }}
        .opus-stats {{ display: flex; gap: 8px; margin-top: 8px; }}
        .opus-stat {{ font-size: 11px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }}
        .filters {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .filter-row {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: end; }}
        .filter-group {{ display: flex; flex-direction: column; gap: 4px; }}
        .filter-label {{ font-size: 12px; font-weight: 600; color: #666; }}
        .filter-select, .filter-input {{ padding: 8px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }}
        .signals-grid {{ display: flex; flex-direction: column; gap: 16px; }}
        .signal-card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #ccc; }}
        .signal-card[data-signal="STRONG_BUY"] {{ border-left-color: #dc2626; }}
        .signal-card[data-signal="BUY"] {{ border-left-color: #ef4444; }}
        .signal-card[data-signal="POSITIVE"] {{ border-left-color: #f97316; }}
        .signal-card[data-signal="HOLD"] {{ border-left-color: #eab308; }}
        .signal-card[data-signal="NEUTRAL"] {{ border-left-color: #6b7280; }}
        .signal-card[data-signal="CONCERN"] {{ border-left-color: #8b5cf6; }}
        .signal-card[data-signal="SELL"] {{ border-left-color: #3b82f6; }}
        .signal-card[data-signal="STRONG_SELL"] {{ border-left-color: #1d4ed8; }}
        .signal-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }}
        .signal-asset {{ font-size: 18px; font-weight: 700; }}
        .signal-type {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; color: white; }}
        .signal-type.STRONG_BUY {{ background: #dc2626; }}
        .signal-type.BUY {{ background: #ef4444; }}
        .signal-type.POSITIVE {{ background: #f97316; }}
        .signal-type.HOLD {{ background: #eab308; }}
        .signal-type.NEUTRAL {{ background: #6b7280; }}
        .signal-type.CONCERN {{ background: #8b5cf6; }}
        .signal-type.SELL {{ background: #3b82f6; }}
        .signal-type.STRONG_SELL {{ background: #1d4ed8; }}
        .quote {{ background: #f8f9fa; padding: 12px 16px; border-radius: 8px; margin: 12px 0; font-style: italic; color: #333; border-left: 3px solid #667eea; }}
        .meta {{ display: flex; gap: 16px; font-size: 13px; color: #666; margin-top: 8px; flex-wrap: wrap; }}
        .meta a {{ color: #ef4444; text-decoration: none; }}
        .meta a:hover {{ text-decoration: underline; }}
        .signal-actions {{ display: flex; gap: 8px; margin-top: 16px; }}
        .btn {{ padding: 6px 14px; border-radius: 8px; border: 1px solid #ddd; background: white; cursor: pointer; font-size: 13px; }}
        .btn-approve {{ background: #10b981; color: white; border-color: #10b981; }}
        .btn-reject {{ background: #ef4444; color: white; border-color: #ef4444; }}
        .review-status {{ padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 600; }}
        .status-approved {{ background: #dcfce7; color: #166534; }}
        .status-rejected {{ background: #fee2e2; color: #991b1b; }}
        .rejection-reason {{ margin-top: 8px; }}
        .rejection-input {{ width: 100%; padding: 6px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; }}
        .opus-review {{ background: #f0f9ff; border-left: 3px solid #0ea5e9; padding: 12px; margin-top: 12px; border-radius: 8px; }}
        .opus-verdict {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; color: white; }}
        .opus-approve {{ background: #10b981; }}
        .opus-reject {{ background: #ef4444; }}
        .opus-modify {{ background: #f59e0b; }}
        .hide {{ display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>시그널 리뷰 v5</h1>
            <p>코린이 아빠 시그널 검증 시스템 - Opus 통합</p>
            <button class="opus-btn" onclick="startOpusReview()" id="opusBtn">
                🧠 Opus 전체 검토
            </button>
            <div class="progress-container" id="progressContainer" style="display: none;">
                <div style="font-size: 12px; margin-bottom: 4px;">
                    <span id="progressText">진행률: 0/0</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill" style="width: 0%;"></div>
                </div>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_signals}</div>
                <div class="stat-label">총 시그널</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{pending_count}</div>
                <div class="stat-label">검토 대기</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{approved_count}</div>
                <div class="stat-label">승인됨</div>
                <div class="opus-stats">
                    <div class="opus-stat">Opus: {opus_approved}</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{rejected_count}</div>
                <div class="stat-label">거부됨</div>
                <div class="opus-stats">
                    <div class="opus-stat">Opus: {opus_rejected}</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="displayedCount">{total_signals}</div>
                <div class="stat-label">현재 표시</div>
            </div>
        </div>

        <div class="filters">
            <div class="filter-row">
                <div class="filter-group">
                    <label class="filter-label">시그널 타입</label>
                    <select class="filter-select" id="signalTypeFilter" onchange="applyFilters()">
                        <option value="">전체</option>
                        <option value="STRONG_BUY">STRONG_BUY</option>
                        <option value="BUY">BUY</option>
                        <option value="POSITIVE">POSITIVE</option>
                        <option value="HOLD">HOLD</option>
                        <option value="NEUTRAL">NEUTRAL</option>
                        <option value="CONCERN">CONCERN</option>
                        <option value="SELL">SELL</option>
                        <option value="STRONG_SELL">STRONG_SELL</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">검토 상태</label>
                    <select class="filter-select" id="reviewStatusFilter" onchange="applyFilters()">
                        <option value="">전체</option>
                        <option value="pending">검토 대기</option>
                        <option value="approved">승인됨</option>
                        <option value="rejected">거부됨</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">종목명</label>
                    <input type="text" class="filter-input" id="assetFilter" placeholder="종목 검색..." onkeyup="applyFilters()">
                </div>
                <div class="filter-group">
                    <label class="filter-label">Opus 검토</label>
                    <select class="filter-select" id="opusFilter" onchange="applyFilters()">
                        <option value="">전체</option>
                        <option value="approve">Opus 승인</option>
                        <option value="reject">Opus 거부</option>
                        <option value="modify">Opus 수정</option>
                        <option value="none">Opus 미검토</option>
                    </select>
                </div>
            </div>
        </div>

        <div class="signals-grid" id="signalsGrid">"""

    # 시그널 카드들 생성
    for i, signal in enumerate(signals):
        signal_id = f"{signal.get('video_id', '')}_{signal.get('asset', '')}_{i}"
        review = reviews.get(signal_id, {})
        opus_review = opus_reviews.get(signal_id, {})
        
        # 검토 상태
        review_status = review.get('status', 'pending')
        status_class = f"status-{review_status}" if review_status != 'pending' else ""
        
        # Opus 검토 결과
        opus_verdict = opus_review.get('verdict', '')
        opus_html = ""
        if opus_verdict:
            opus_class = f"opus-{opus_verdict}"
            opus_text = {"approve": "승인", "reject": "거부", "modify": "수정"}.get(opus_verdict, opus_verdict)
            opus_reasoning = opus_review.get('reasoning', '')
            opus_html = f"""
            <div class="opus-review">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span class="opus-verdict {opus_class}">{opus_text}</span>
                    <span style="font-size: 11px; color: #666;">Opus 검토</span>
                </div>
                <div style="font-size: 12px; color: #333;">{opus_reasoning}</div>
            </div>"""
        
        # 영상 날짜
        upload_date = signal.get('upload_date', '')
        date_display = f" ({upload_date})" if upload_date else ""
        
        html += f"""
            <div class="signal-card" data-signal="{signal.get('signal_type', '')}" data-signal-id="{signal_id}" data-review-status="{review_status}" data-opus-verdict="{opus_verdict}">
                <div class="signal-header">
                    <div class="signal-asset">{signal.get('asset', 'N/A')}</div>
                    <div class="signal-type {signal.get('signal_type', '')}">{signal.get('signal_type', 'N/A')}</div>
                </div>
                <div class="quote">{signal.get('content', 'N/A')}</div>
                <div class="meta">
                    <span>⏱️ {signal.get('timestamp', 'N/A')}</span>
                    <span>📊 {signal.get('confidence', 'N/A')}</span>
                    <a href="https://youtube.com/watch?v={signal.get('video_id', '')}" target="_blank">🎥 영상 보기</a>
                    <span>📅 {signal.get('title', 'N/A')}{date_display}</span>
                </div>
                
                {opus_html}
                
                <div class="signal-actions">
                    {"<span class='review-status " + status_class + "'>" + ("승인됨" if review_status == "approved" else "거부됨" if review_status == "rejected" else "검토 대기") + "</span>" if review_status != 'pending' else ""}
                    <button class="btn btn-approve" onclick="reviewSignal('{signal_id}', 'approved', '')">✅ 승인</button>
                    <button class="btn btn-reject" onclick="showRejectReason('{signal_id}')">❌ 거부</button>
                </div>
                
                <div class="rejection-reason" id="reject-{signal_id}" style="display: none;">
                    <input type="text" class="rejection-input" placeholder="거부 사유를 입력하세요..." onkeypress="handleRejectKeypress(event, '{signal_id}')">
                    <div style="margin-top: 6px;">
                        <button class="btn btn-reject" onclick="submitReject('{signal_id}')">거부 확정</button>
                        <button class="btn" onclick="hideRejectReason('{signal_id}')">취소</button>
                    </div>
                </div>
                
                {"<div style='margin-top: 8px; font-size: 12px; color: #666;'><strong>거부 사유:</strong> " + review.get('reason', '') + "</div>" if review_status == 'rejected' and review.get('reason') else ""}
            </div>"""
    
    html += f"""
        </div>
    </div>

    <script>
        let allSignals = {json.dumps(signals, ensure_ascii=False)};
        let reviews = {json.dumps(reviews, ensure_ascii=False)};
        let opusReviews = {json.dumps(opus_reviews, ensure_ascii=False)};

        function applyFilters() {{
            const signalType = document.getElementById('signalTypeFilter').value;
            const reviewStatus = document.getElementById('reviewStatusFilter').value;
            const assetFilter = document.getElementById('assetFilter').value.toLowerCase();
            const opusFilter = document.getElementById('opusFilter').value;
            
            const cards = document.querySelectorAll('.signal-card');
            let visibleCount = 0;
            
            cards.forEach(card => {{
                let show = true;
                
                if (signalType && card.dataset.signal !== signalType) {{
                    show = false;
                }}
                
                if (reviewStatus && card.dataset.reviewStatus !== reviewStatus) {{
                    show = false;
                }}
                
                if (assetFilter) {{
                    const asset = card.querySelector('.signal-asset').textContent.toLowerCase();
                    if (!asset.includes(assetFilter)) {{
                        show = false;
                    }}
                }}
                
                if (opusFilter) {{
                    const opusVerdict = card.dataset.opusVerdict;
                    if (opusFilter === 'none' && opusVerdict) {{
                        show = false;
                    }} else if (opusFilter !== 'none' && opusVerdict !== opusFilter) {{
                        show = false;
                    }}
                }}
                
                card.style.display = show ? 'block' : 'none';
                if (show) visibleCount++;
            }});
            
            document.getElementById('displayedCount').textContent = visibleCount;
        }}

        function reviewSignal(signalId, status, reason) {{
            fetch('/api/review', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ signal_id: signalId, status: status, reason: reason }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    location.reload();
                }} else {{
                    alert('리뷰 저장 실패: ' + (data.error || '알 수 없는 오류'));
                }}
            }});
        }}

        function showRejectReason(signalId) {{
            document.getElementById('reject-' + signalId).style.display = 'block';
        }}

        function hideRejectReason(signalId) {{
            document.getElementById('reject-' + signalId).style.display = 'none';
        }}

        function handleRejectKeypress(event, signalId) {{
            if (event.key === 'Enter') {{
                submitReject(signalId);
            }}
        }}

        function submitReject(signalId) {{
            const reasonInput = document.querySelector('#reject-' + signalId + ' input');
            const reason = reasonInput.value.trim();
            if (!reason) {{
                alert('거부 사유를 입력해주세요.');
                return;
            }}
            reviewSignal(signalId, 'rejected', reason);
        }}

        function startOpusReview() {{
            if (confirm('모든 시그널에 대해 Opus 검토를 시작하시겠습니까? 시간이 오래 걸릴 수 있습니다.')) {{
                const btn = document.getElementById('opusBtn');
                btn.disabled = true;
                btn.textContent = '🧠 검토 중...';
                
                document.getElementById('progressContainer').style.display = 'block';
                
                fetch('/api/opus-review-all', {{ method: 'POST' }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        pollOpusProgress();
                    }} else {{
                        alert('Opus 검토 시작 실패: ' + (data.error || '알 수 없는 오류'));
                        btn.disabled = false;
                        btn.textContent = '🧠 Opus 전체 검토';
                    }}
                }});
            }}
        }}

        function pollOpusProgress() {{
            fetch('/api/opus-progress')
            .then(response => response.json())
            .then(data => {{
                const current = data.current || 0;
                const total = data.total || 1;
                const status = data.status || 'idle';
                
                const progress = total > 0 ? (current / total) * 100 : 0;
                document.getElementById('progressFill').style.width = progress + '%';
                document.getElementById('progressText').textContent = `진행률: ${{current}}/${{total}}`;
                
                if (status === 'completed') {{
                    setTimeout(() => {{
                        location.reload();
                    }}, 1000);
                }} else if (status === 'running') {{
                    setTimeout(pollOpusProgress, 2000);
                }}
            }});
        }}
    </script>
</body>
</html>"""
    
    return html

class ReviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """GET 요청 처리"""
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        
        if path == '/':
            # 메인 HTML 페이지
            html = build_html()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        elif path == '/api/signals':
            # 시그널 데이터 API
            signals = load_signals()
            self.send_json_response(signals)
            
        elif path == '/api/reviews':
            # 리뷰 데이터 API
            reviews = load_reviews()
            self.send_json_response(reviews)
            
        elif path == '/api/opus-reviews':
            # Opus 리뷰 데이터 API
            opus_reviews = load_opus_reviews()
            self.send_json_response(opus_reviews)
            
        elif path == '/api/opus-progress':
            # Opus 진행률 API
            self.send_json_response(opus_progress)
            
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_POST(self):
        """POST 요청 처리"""
        path = urlparse(self.path).path
        
        if path == '/api/review':
            # 개별 시그널 리뷰
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                signal_id = data.get('signal_id')
                status = data.get('status')
                reason = data.get('reason', '')
                
                if not signal_id or not status:
                    self.send_json_response({"success": False, "error": "Missing required fields"})
                    return
                
                reviews = load_reviews()
                reviews[signal_id] = {
                    "status": status,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                }
                save_reviews(reviews)
                
                self.send_json_response({"success": True})
                
            except Exception as e:
                self.send_json_response({"success": False, "error": str(e)})
                
        elif path == '/api/opus-review-all':
            # 전체 Opus 검토 시작
            try:
                opus_analyze_all_signals()
                self.send_json_response({"success": True})
            except Exception as e:
                self.send_json_response({"success": False, "error": str(e)})
                
        else:
            self.send_response(404)
            self.end_headers()
            
    def send_json_response(self, data):
        """JSON 응답 전송"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))

def main():
    """서버 시작"""
    port = 8900
    server = ThreadingHTTPServer(('', port), ReviewHandler)
    print(f"리뷰 서버 v5 시작됨: http://localhost:{port}")
    print(f"작업 디렉토리: {os.getcwd()}")
    print(f"시그널 파일: {SIGNALS_FILE}")
    print(f"리뷰 결과: {REVIEW_FILE}")
    print(f"Opus 결과: {OPUS_REVIEW_FILE}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\n서버 중지됨")

if __name__ == '__main__':
    main()