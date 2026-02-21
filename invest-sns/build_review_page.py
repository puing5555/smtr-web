"""
코린이 아빠 시그널 리뷰 페이지 빌더
- 4단계 검증 결과를 통합한 HTML 페이지 생성
"""
import json
import os
import sys
import io
from datetime import datetime

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def load_signals_data():
    """모든 검증 데이터 로드"""
    base_path = "C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106"
    
    # 1. 원본 194개 시그널
    with open(f"{base_path}\\_all_signals_194.json", 'r', encoding='utf-8') as f:
        original_signals = json.load(f)
    
    # 2. GPT-4o 검증 결과 (JSONL)
    gpt_results = {}
    gpt_file = "C:\\Users\\Mario\\.openclaw\\workspace\\smtr_data\\corinpapa1106\\_verify_batch_full_result.jsonl"
    
    if os.path.exists(gpt_file):
        with open(gpt_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    result = json.loads(line)
                    video_id = result['custom_id'].replace('verify_corinpapa_', '')
                    gpt_results[video_id] = result
    
    # 3. Claude 검증 결과
    claude_results = {}
    claude_file = f"{base_path}\\_claude_verify_full.json"
    
    if os.path.exists(claude_file):
        with open(claude_file, 'r', encoding='utf-8') as f:
            claude_data = json.load(f)
            for result in claude_data.get('results', []):
                signal_index = result.get('signal_index')
                claude_results[signal_index] = result
    
    # 4. 타임스탬프 포함 시그널
    timestamp_signals = []
    timestamp_file = f"{base_path}\\_signals_with_timestamps.json"
    
    if os.path.exists(timestamp_file):
        with open(timestamp_file, 'r', encoding='utf-8') as f:
            timestamp_signals = json.load(f)
    
    return original_signals, gpt_results, claude_results, timestamp_signals

def get_gpt_verification_for_signal(gpt_results, video_id, signal_index):
    """특정 시그널의 GPT 검증 결과 찾기"""
    if video_id not in gpt_results:
        return None
    
    gpt_data = gpt_results[video_id]
    verifications = gpt_data.get('response', {}).get('body', {}).get('choices', [{}])[0].get('message', {}).get('content', '{}')
    
    try:
        verification_data = json.loads(verifications)
        for verification in verification_data.get('verifications', []):
            if verification.get('signal_index') == signal_index:
                return verification
    except:
        pass
    
    return None

def get_signal_badge_class(signal_type):
    """시그널 타입에 따른 CSS 클래스"""
    type_classes = {
        'STRONG_BUY': 'badge-strong-buy',
        'BUY': 'badge-buy',
        'POSITIVE': 'badge-positive',
        'HOLD': 'badge-hold',
        'NEUTRAL': 'badge-neutral',
        'CONCERN': 'badge-concern',
        'SELL': 'badge-sell',
        'STRONG_SELL': 'badge-strong-sell'
    }
    return type_classes.get(signal_type, 'badge-neutral')

def get_verdict_badge_class(verdict):
    """판정에 따른 CSS 클래스"""
    verdict_classes = {
        'confirmed': 'badge-confirmed',
        'corrected': 'badge-corrected',
        'rejected': 'badge-rejected',
        'error': 'badge-error'
    }
    return verdict_classes.get(verdict, 'badge-neutral')

def create_signal_card_html(signal, signal_index, gpt_verification, claude_result, timestamp_seconds):
    """개별 시그널 카드 HTML 생성"""
    video_id = signal.get('video_id', '')
    video_title = signal.get('title', 'N/A')
    
    # YouTube 링크 (타임스탬프 포함)
    youtube_link = f"https://www.youtube.com/watch?v={video_id}"
    if timestamp_seconds:
        youtube_link += f"&t={int(timestamp_seconds)}"
    
    # 시그널 정보
    asset = signal.get('asset', 'N/A')
    signal_type = signal.get('signal_type', 'NEUTRAL')
    content = signal.get('content', '')
    confidence = signal.get('confidence', 'N/A')
    context = signal.get('context', '')
    
    # GPT 검증 정보
    gpt_html = ""
    if gpt_verification:
        gpt_stock_correct = "✅" if gpt_verification.get('stock_correct', True) else "❌"
        gpt_signal_correct = "✅" if gpt_verification.get('signal_correct', True) else "❌"
        gpt_quote_correct = "✅" if gpt_verification.get('quote_correct', True) else "❌"
        gpt_suggested = gpt_verification.get('suggested_signal', signal_type)
        gpt_explanation = gpt_verification.get('explanation', '')
        
        gpt_html = f"""
        <div class="verification-step">
            <h5>2️⃣ GPT-4o 검증 결과</h5>
            <div class="verification-details">
                <p><strong>종목 정확성:</strong> {gpt_stock_correct}</p>
                <p><strong>시그널 정확성:</strong> {gpt_signal_correct}</p>
                <p><strong>인용 정확성:</strong> {gpt_quote_correct}</p>
                <p><strong>제안 시그널:</strong> <span class="badge {get_signal_badge_class(gpt_suggested)}">{gpt_suggested}</span></p>
                <p><strong>설명:</strong> {gpt_explanation}</p>
            </div>
        </div>
        """
    else:
        gpt_html = """
        <div class="verification-step">
            <h5>2️⃣ GPT-4o 검증 결과</h5>
            <p class="text-muted">검증 결과 없음</p>
        </div>
        """
    
    # Claude 검증 정보
    claude_html = ""
    if claude_result:
        claude_verification = claude_result.get('claude_verification', {})
        verdict = claude_verification.get('verdict', 'error')
        claude_confidence = claude_verification.get('confidence', 0.0)
        reason = claude_verification.get('reason', '')
        corrected_asset = claude_verification.get('corrected_asset', '')
        corrected_signal = claude_verification.get('corrected_signal', '')
        
        claude_html = f"""
        <div class="verification-step">
            <h5>3️⃣ Claude 검증 결과</h5>
            <div class="verification-details">
                <p><strong>판정:</strong> <span class="badge {get_verdict_badge_class(verdict)}">{verdict.upper()}</span></p>
                <p><strong>신뢰도:</strong> {claude_confidence:.2f}</p>
                <p><strong>이유:</strong> {reason}</p>
                {f'<p><strong>수정된 종목:</strong> {corrected_asset}</p>' if corrected_asset else ''}
                {f'<p><strong>수정된 시그널:</strong> {corrected_signal}</p>' if corrected_signal else ''}
            </div>
        </div>
        """
    else:
        claude_html = """
        <div class="verification-step">
            <h5>3️⃣ Claude 검증 결과</h5>
            <p class="text-muted">검증 진행 중...</p>
        </div>
        """
    
    # 타임스탬프 정보
    timestamp_html = ""
    if timestamp_seconds:
        minutes = int(timestamp_seconds // 60)
        seconds = int(timestamp_seconds % 60)
        timestamp_html = f"<small class='text-muted'>📍 {minutes:02d}:{seconds:02d}</small>"
    
    return f"""
    <div class="card mb-4 signal-card" data-signal-index="{signal_index}">
        <div class="card-header d-flex justify-content-between align-items-center">
            <div>
                <h5 class="mb-1">#{signal_index} {asset}</h5>
                <span class="badge {get_signal_badge_class(signal_type)}">{signal_type}</span>
                {timestamp_html}
            </div>
            <div>
                <a href="{youtube_link}" target="_blank" class="btn btn-sm btn-outline-primary">
                    🎥 영상 보기
                </a>
            </div>
        </div>
        
        <div class="card-body">
            <div class="verification-step">
                <h5>1️⃣ GPT-4o-mini 추출 결과</h5>
                <div class="original-signal">
                    <p><strong>내용:</strong> {content}</p>
                    <p><strong>맥락:</strong> {context}</p>
                    <p><strong>신뢰도:</strong> {confidence}</p>
                    <p><strong>영상 제목:</strong> {video_title}</p>
                </div>
            </div>
            
            {gpt_html}
            
            {claude_html}
            
            <div class="verification-step">
                <h5>4️⃣ 인간 최종 검토</h5>
                <div class="human-review-buttons">
                    <button class="btn btn-success btn-sm" onclick="approveSignal({signal_index})">✅ 승인</button>
                    <button class="btn btn-warning btn-sm" onclick="requestEditSignal({signal_index})">✏️ 수정</button>
                    <button class="btn btn-danger btn-sm" onclick="rejectSignal({signal_index})">❌ 거부</button>
                </div>
                <div id="review-status-{signal_index}" class="mt-2"></div>
            </div>
        </div>
    </div>
    """

def generate_html():
    """HTML 페이지 생성"""
    
    original_signals, gpt_results, claude_results, timestamp_signals = load_signals_data()
    
    # 모든 시그널 카드 생성
    signal_cards = []
    
    for i, signal in enumerate(original_signals):
        video_id = signal.get('video_id', '')
        
        # GPT 검증 결과 찾기
        gpt_verification = get_gpt_verification_for_signal(gpt_results, video_id, i)
        
        # Claude 검증 결과 찾기
        claude_result = claude_results.get(i)
        
        # 타임스탬프 정보
        timestamp_seconds = None
        if i < len(timestamp_signals):
            timestamp_seconds = timestamp_signals[i].get('timestamp_seconds')
        
        signal_card = create_signal_card_html(signal, i, gpt_verification, claude_result, timestamp_seconds)
        signal_cards.append(signal_card)
    
    # 통계 계산
    total_signals = len(original_signals)
    gpt_verified = len([r for r in gpt_results.values() if r])
    claude_verified = len([r for r in claude_results.values() if r])
    with_timestamps = len([s for s in timestamp_signals if s.get('timestamp_seconds')])
    
    # 전체 HTML 생성
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>코린이 아빠 시그널 검증 리뷰</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .signal-card {{ border-left: 4px solid #007bff; }}
            .verification-step {{ margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #eee; }}
            .verification-step:last-child {{ border-bottom: none; }}
            .verification-details {{ font-size: 0.9rem; }}
            .human-review-buttons button {{ margin-right: 0.5rem; }}
            
            /* 시그널 타입 배지 */
            .badge-strong-buy {{ background-color: #28a745; }}
            .badge-buy {{ background-color: #20c997; }}
            .badge-positive {{ background-color: #17a2b8; }}
            .badge-hold {{ background-color: #6c757d; }}
            .badge-neutral {{ background-color: #6f42c1; }}
            .badge-concern {{ background-color: #fd7e14; }}
            .badge-sell {{ background-color: #dc3545; }}
            .badge-strong-sell {{ background-color: #721c24; }}
            
            /* 검증 결과 배지 */
            .badge-confirmed {{ background-color: #28a745; }}
            .badge-corrected {{ background-color: #ffc107; color: #000; }}
            .badge-rejected {{ background-color: #dc3545; }}
            .badge-error {{ background-color: #6c757d; }}
            
            .stats-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
            .original-signal {{ background-color: #f8f9fa; padding: 1rem; border-radius: 0.375rem; margin-top: 0.5rem; }}
        </style>
    </head>
    <body>
        <div class="container-fluid py-4">
            <div class="row">
                <div class="col-12">
                    <h1 class="mb-4">🎯 코린이 아빠 시그널 검증 리뷰</h1>
                    <p class="lead">AI 추출 → GPT 검증 → Claude 검증 → 인간 검토 4단계 파이프라인</p>
                    
                    <!-- 통계 카드 -->
                    <div class="row mb-4">
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body text-center">
                                    <h3>{total_signals}</h3>
                                    <p class="mb-0">총 시그널</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body text-center">
                                    <h3>{gpt_verified}</h3>
                                    <p class="mb-0">GPT 검증 완료</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body text-center">
                                    <h3>{claude_verified}</h3>
                                    <p class="mb-0">Claude 검증 완료</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body text-center">
                                    <h3>{with_timestamps}</h3>
                                    <p class="mb-0">타임스탬프 추출</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 필터 버튼 -->
                    <div class="mb-4">
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-outline-primary active" onclick="filterSignals('all')">전체</button>
                            <button type="button" class="btn btn-outline-success" onclick="filterSignals('confirmed')">확인됨</button>
                            <button type="button" class="btn btn-outline-warning" onclick="filterSignals('corrected')">수정됨</button>
                            <button type="button" class="btn btn-outline-danger" onclick="filterSignals('rejected')">거부됨</button>
                            <button type="button" class="btn btn-outline-secondary" onclick="filterSignals('pending')">검토 대기</button>
                        </div>
                    </div>
                    
                    <!-- 시그널 카드들 -->
                    <div id="signal-cards">
                        {''.join(signal_cards)}
                    </div>
                    
                    <!-- 푸터 -->
                    <div class="text-center mt-5 text-muted">
                        <p>생성 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                        <p>데이터 기반: 코린이 아빠 YouTube 채널 194개 시그널</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // 인간 검토 기능
            function approveSignal(signalIndex) {{
                document.getElementById('review-status-' + signalIndex).innerHTML = 
                    '<div class="alert alert-success alert-sm">✅ 승인됨</div>';
                console.log('Signal', signalIndex, 'approved');
            }}
            
            function requestEditSignal(signalIndex) {{
                const newContent = prompt('수정할 내용을 입력하세요:');
                if (newContent) {{
                    document.getElementById('review-status-' + signalIndex).innerHTML = 
                        '<div class="alert alert-warning alert-sm">✏️ 수정 요청: ' + newContent + '</div>';
                    console.log('Signal', signalIndex, 'edit requested:', newContent);
                }}
            }}
            
            function rejectSignal(signalIndex) {{
                const reason = prompt('거부 사유를 입력하세요:');
                if (reason) {{
                    document.getElementById('review-status-' + signalIndex).innerHTML = 
                        '<div class="alert alert-danger alert-sm">❌ 거부됨: ' + reason + '</div>';
                    console.log('Signal', signalIndex, 'rejected:', reason);
                }}
            }}
            
            // 필터 기능
            function filterSignals(type) {{
                const cards = document.querySelectorAll('.signal-card');
                const buttons = document.querySelectorAll('.btn-group button');
                
                // 버튼 상태 업데이트
                buttons.forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                
                cards.forEach(card => {{
                    let show = true;
                    
                    if (type === 'confirmed') {{
                        show = card.innerHTML.includes('badge-confirmed');
                    }} else if (type === 'corrected') {{
                        show = card.innerHTML.includes('badge-corrected');
                    }} else if (type === 'rejected') {{
                        show = card.innerHTML.includes('badge-rejected');
                    }} else if (type === 'pending') {{
                        show = card.innerHTML.includes('검증 진행 중') || card.innerHTML.includes('검증 결과 없음');
                    }}
                    
                    card.style.display = show ? 'block' : 'none';
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    # HTML 파일 저장
    output_file = "C:\\Users\\Mario\\work\\invest-sns\\signal-review.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML 리뷰 페이지 생성 완료: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_html()