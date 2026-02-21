#!/usr/bin/env python3
"""
리뷰 페이지 HTML 빌드
- 모든 데이터를 HTML에 내장 (서버 불필요)
- 4단계 검증 결과를 카드 형태로 표시
- 필터링 및 통계 대시보드 포함
"""
import json
import os
import sys
import io
from datetime import datetime

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def load_gpt4o_verifications():
    """GPT-4o 검증 결과 로드"""
    gpt4o_path = "C:\\Users\\Mario\\.openclaw\\workspace\\smtr_data\\corinpapa1106\\_verify_batch_full_result.jsonl"
    
    if not os.path.exists(gpt4o_path):
        print(f"GPT-4o 검증 파일을 찾을 수 없음: {gpt4o_path}")
        return {}
    
    gpt4o_results = {}
    
    with open(gpt4o_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                video_id = data.get('custom_id', '').replace('verify_corinpapa_', '')
                if video_id and 'response' in data:
                    body = data['response']['body']
                    if 'choices' in body and body['choices']:
                        content = body['choices'][0]['message']['content']
                        verification_data = json.loads(content)
                        gpt4o_results[video_id] = verification_data
            except Exception as e:
                print(f"GPT-4o 검증 데이터 파싱 오류: {e}")
                continue
    
    print(f"GPT-4o 검증 결과 로드: {len(gpt4o_results)}개 영상")
    return gpt4o_results

def create_html_template():
    """HTML 템플릿 생성"""
    html_template = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>코린이 아빠 시그널 검증 리뷰</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Malgun Gothic', sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.08);
        }
        
        .title {
            font-size: 32px;
            font-weight: 800;
            color: #1a202c;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 16px;
            color: #666;
            margin-bottom: 20px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }
        
        .stat-number {
            font-size: 28px;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 14px;
            color: #666;
        }
        
        .filters {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.08);
        }
        
        .filter-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            align-items: end;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
        }
        
        .filter-label {
            font-size: 14px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 5px;
        }
        
        .filter-select, .filter-input {
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
        }
        
        .signals-grid {
            display: grid;
            gap: 20px;
        }
        
        .signal-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.08);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .signal-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 30px rgba(0,0,0,0.12);
        }
        
        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 20px;
        }
        
        .signal-meta {
            flex: 1;
        }
        
        .signal-asset {
            font-size: 20px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 5px;
        }
        
        .signal-type {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .signal-type.BUY { background: #dcfce7; color: #166534; }
        .signal-type.SELL { background: #fecaca; color: #dc2626; }
        .signal-type.HOLD { background: #fef3c7; color: #a16207; }
        .signal-type.CONCERN { background: #e0e7ff; color: #3730a3; }
        
        .signal-actions {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        
        .btn-approve { background: #10b981; color: white; }
        .btn-reject { background: #ef4444; color: white; }
        .btn-edit { background: #6366f1; color: white; }
        
        .btn:hover {
            opacity: 0.9;
        }
        
        .verification-stages {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .stage {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px;
        }
        
        .stage-title {
            font-size: 14px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 10px;
        }
        
        .stage-content {
            font-size: 13px;
            line-height: 1.5;
        }
        
        .quote {
            background: #f1f5f9;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
            font-style: italic;
            color: #475569;
        }
        
        .timestamp {
            display: inline-block;
            background: #e0e7ff;
            color: #3730a3;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin-left: 10px;
        }
        
        .youtube-link {
            color: #dc2626;
            text-decoration: none;
            font-weight: 600;
        }
        
        .youtube-link:hover {
            text-decoration: underline;
        }
        
        .confidence-bar {
            width: 100%;
            height: 6px;
            background: #e5e7eb;
            border-radius: 3px;
            overflow: hidden;
            margin: 8px 0;
        }
        
        .confidence-fill {
            height: 100%;
            background: #10b981;
            transition: width 0.3s ease;
        }
        
        .hide { display: none !important; }
        
        .review-status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            margin-left: 10px;
        }
        
        .status-pending { background: #fef3c7; color: #a16207; }
        .status-approved { background: #dcfce7; color: #166534; }
        .status-rejected { background: #fecaca; color: #dc2626; }
        .status-modified { background: #e0e7ff; color: #3730a3; }
        
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .verification-stages { grid-template-columns: 1fr; }
            .filter-row { grid-template-columns: 1fr; }
            .signal-header { flex-direction: column; gap: 15px; }
            .signal-actions { justify-content: flex-start; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🔍 코린이 아빠 시그널 검증 리뷰</h1>
            <p class="subtitle">3단계 검증 파이프라인: GPT-4o-mini 추출 → Claude 검증 → 인간 최종 리뷰</p>
            
            <div class="stats" id="stats">
                <div class="stat-card">
                    <div class="stat-number" id="total-signals">0</div>
                    <div class="stat-label">총 시그널</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="pending-review">0</div>
                    <div class="stat-label">검토 대기</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="approved-count">0</div>
                    <div class="stat-label">승인됨</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="rejected-count">0</div>
                    <div class="stat-label">거부됨</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="claude-accuracy">0%</div>
                    <div class="stat-label">Claude 검증 정확도</div>
                </div>
            </div>
        </div>
        
        <div class="filters">
            <div class="filter-row">
                <div class="filter-group">
                    <label class="filter-label">종목 필터</label>
                    <select class="filter-select" id="asset-filter">
                        <option value="">전체 종목</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">시그널 타입</label>
                    <select class="filter-select" id="signal-filter">
                        <option value="">전체 시그널</option>
                        <option value="BUY">매수</option>
                        <option value="SELL">매도</option>
                        <option value="HOLD">보유</option>
                        <option value="CONCERN">우려</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">리뷰 상태</label>
                    <select class="filter-select" id="review-filter">
                        <option value="">전체 상태</option>
                        <option value="pending">검토 대기</option>
                        <option value="approved">승인됨</option>
                        <option value="rejected">거부됨</option>
                        <option value="modified">수정됨</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">Claude 판정</label>
                    <select class="filter-select" id="claude-filter">
                        <option value="">전체 판정</option>
                        <option value="confirmed">확인됨</option>
                        <option value="corrected">수정됨</option>
                        <option value="rejected">거부됨</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">검색</label>
                    <input type="text" class="filter-input" id="search-input" placeholder="내용 검색...">
                </div>
            </div>
        </div>
        
        <div class="signals-grid" id="signals-container">
            <!-- 시그널 카드들이 여기에 동적으로 추가됩니다 -->
        </div>
    </div>

    <script>
        // 데이터는 여기에 삽입됩니다
        const SIGNALS_DATA = /*SIGNALS_DATA_PLACEHOLDER*/;
        const GPT4O_DATA = /*GPT4O_DATA_PLACEHOLDER*/;
        
        // 로컬 스토리지에서 리뷰 상태 로드
        function loadReviewStatus() {
            const saved = localStorage.getItem('signal-reviews');
            return saved ? JSON.parse(saved) : {};
        }
        
        // 리뷰 상태 저장
        function saveReviewStatus(reviews) {
            localStorage.setItem('signal-reviews', JSON.stringify(reviews));
        }
        
        // 시그널 카드 생성
        function createSignalCard(signal, index) {
            const reviews = loadReviewStatus();
            const signalId = `${signal.video_id}_${signal.asset}`;
            const reviewStatus = reviews[signalId] || 'pending';
            
            const claude = signal.claude_verification || {};
            const gpt4oVideo = GPT4O_DATA[signal.video_id] || {};
            const gpt4oVerifications = gpt4oVideo.verifications || [];
            
            const timestampHtml = signal.timestamp_seconds ? 
                `<a href="https://youtube.com/watch?v=${signal.video_id}&t=${signal.timestamp_seconds}" 
                   target="_blank" class="youtube-link">
                   ${signal.timestamp} ▶️
                 </a>` : '타임스탬프 없음';
            
            return `
                <div class="signal-card" data-asset="${signal.asset}" data-signal="${signal.signal_type}" 
                     data-review="${reviewStatus}" data-claude="${claude.judgment || 'none'}" data-index="${index}">
                    <div class="signal-header">
                        <div class="signal-meta">
                            <div class="signal-asset">${signal.asset}</div>
                            <span class="signal-type ${signal.signal_type}">${signal.signal_type}</span>
                            <span class="review-status status-${reviewStatus}">${getStatusLabel(reviewStatus)}</span>
                            <div style="margin-top: 8px;">${timestampHtml}</div>
                        </div>
                        <div class="signal-actions">
                            <button class="btn btn-approve" onclick="setReviewStatus('${signalId}', 'approved')">✅ 승인</button>
                            <button class="btn btn-reject" onclick="setReviewStatus('${signalId}', 'rejected')">❌ 거부</button>
                            <button class="btn btn-edit" onclick="setReviewStatus('${signalId}', 'modified')">✏️ 수정</button>
                        </div>
                    </div>
                    
                    <div class="quote">
                        "${signal.content}"
                    </div>
                    
                    <div class="verification-stages">
                        <div class="stage">
                            <div class="stage-title">📝 1차: GPT-4o-mini 추출</div>
                            <div class="stage-content">
                                <strong>종목:</strong> ${signal.asset}<br>
                                <strong>시그널:</strong> ${signal.signal_type}<br>
                                <strong>신뢰도:</strong> ${signal.confidence}<br>
                                <strong>맥락:</strong> ${signal.context || 'N/A'}
                            </div>
                        </div>
                        
                        <div class="stage">
                            <div class="stage-title">🔍 2차: Claude 검증</div>
                            <div class="stage-content">
                                <strong>판정:</strong> ${claude.judgment || 'N/A'}<br>
                                <strong>사유:</strong> ${claude.reason || 'N/A'}<br>
                                ${claude.correction ? `<strong>수정의견:</strong> ${claude.correction}<br>` : ''}
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: ${(claude.confidence || 0) * 100}%"></div>
                                </div>
                                <small>신뢰도: ${((claude.confidence || 0) * 100).toFixed(0)}%</small>
                            </div>
                        </div>
                        
                        <div class="stage">
                            <div class="stage-title">👤 3차: 인간 검토</div>
                            <div class="stage-content">
                                <strong>상태:</strong> ${getStatusLabel(reviewStatus)}<br>
                                <small>마지막 수정: ${reviews[signalId + '_timestamp'] || '없음'}</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        function formatGpt4oVerification(verifications, signal) {
            if (!verifications.length) return 'GPT-4o 검증 데이터 없음';
            
            // 해당 시그널과 매칭되는 검증 찾기 (종목 기준)
            const matching = verifications.find(v => 
                signal.content.includes(v.explanation) || 
                v.explanation.includes(signal.content.substring(0, 20))
            );
            
            if (matching) {
                return `
                    <strong>종목 정확도:</strong> ${matching.stock_correct ? '✅' : '❌'}<br>
                    <strong>시그널 정확도:</strong> ${matching.signal_correct ? '✅' : '❌'}<br>
                    <strong>제안 시그널:</strong> ${matching.suggested_signal}<br>
                    <strong>설명:</strong> ${matching.explanation}
                `;
            }
            
            return `GPT-4o 검증: ${verifications.length}개 검증됨`;
        }
        
        function getStatusLabel(status) {
            const labels = {
                'pending': '검토 대기',
                'approved': '승인됨', 
                'rejected': '거부됨',
                'modified': '수정됨'
            };
            return labels[status] || status;
        }
        
        function setReviewStatus(signalId, status) {
            const reviews = loadReviewStatus();
            reviews[signalId] = status;
            reviews[signalId + '_timestamp'] = new Date().toLocaleString('ko-KR');
            saveReviewStatus(reviews);
            
            // UI 업데이트
            const card = document.querySelector(`[data-index]`);  // 실제로는 더 정확한 선택자 사용
            updateStats();
            applyFilters();
        }
        
        function updateStats() {
            const reviews = loadReviewStatus();
            const total = SIGNALS_DATA.length;
            let approved = 0, rejected = 0, modified = 0;
            let claudeCorrect = 0;
            
            SIGNALS_DATA.forEach((signal, index) => {
                const signalId = `${signal.video_id}_${signal.asset}`;
                const status = reviews[signalId] || 'pending';
                
                if (status === 'approved') approved++;
                else if (status === 'rejected') rejected++;
                else if (status === 'modified') modified++;
                
                if (signal.claude_verification && signal.claude_verification.judgment === 'confirmed') {
                    claudeCorrect++;
                }
            });
            
            document.getElementById('total-signals').textContent = total;
            document.getElementById('pending-review').textContent = total - approved - rejected - modified;
            document.getElementById('approved-count').textContent = approved;
            document.getElementById('rejected-count').textContent = rejected;
            document.getElementById('claude-accuracy').textContent = 
                Math.round((claudeCorrect / total) * 100) + '%';
        }
        
        function applyFilters() {
            const assetFilter = document.getElementById('asset-filter').value;
            const signalFilter = document.getElementById('signal-filter').value;
            const reviewFilter = document.getElementById('review-filter').value;
            const claudeFilter = document.getElementById('claude-filter').value;
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            
            const cards = document.querySelectorAll('.signal-card');
            
            cards.forEach(card => {
                const asset = card.dataset.asset;
                const signal = card.dataset.signal;
                const review = card.dataset.review;
                const claude = card.dataset.claude;
                const content = card.textContent.toLowerCase();
                
                const matchAsset = !assetFilter || asset === assetFilter;
                const matchSignal = !signalFilter || signal === signalFilter;
                const matchReview = !reviewFilter || review === reviewFilter;
                const matchClaude = !claudeFilter || claude === claudeFilter;
                const matchSearch = !searchTerm || content.includes(searchTerm);
                
                if (matchAsset && matchSignal && matchReview && matchClaude && matchSearch) {
                    card.classList.remove('hide');
                } else {
                    card.classList.add('hide');
                }
            });
        }
        
        function initializeFilters() {
            // 종목 필터 옵션 생성
            const assets = [...new Set(SIGNALS_DATA.map(s => s.asset))].sort();
            const assetFilter = document.getElementById('asset-filter');
            assets.forEach(asset => {
                const option = document.createElement('option');
                option.value = asset;
                option.textContent = asset;
                assetFilter.appendChild(option);
            });
            
            // 필터 이벤트 리스너
            document.getElementById('asset-filter').addEventListener('change', applyFilters);
            document.getElementById('signal-filter').addEventListener('change', applyFilters);
            document.getElementById('review-filter').addEventListener('change', applyFilters);
            document.getElementById('claude-filter').addEventListener('change', applyFilters);
            document.getElementById('search-input').addEventListener('input', applyFilters);
        }
        
        function renderSignals() {
            const container = document.getElementById('signals-container');
            container.innerHTML = SIGNALS_DATA.map((signal, index) => 
                createSignalCard(signal, index)
            ).join('');
        }
        
        // 초기화
        document.addEventListener('DOMContentLoaded', function() {
            renderSignals();
            initializeFilters();
            updateStats();
        });
    </script>
</body>
</html>'''
    
    return html_template

def main():
    print("=== 리뷰 페이지 HTML 빌드 ===")
    
    # Claude 검증 결과 확인
    claude_path = "_claude_verify_full.json"
    if not os.path.exists(claude_path):
        print("❌ Claude 검증 결과를 찾을 수 없습니다.")
        print("   Claude 검증이 완료된 후 다시 실행해주세요.")
        return
    
    # 데이터 로드
    print("데이터 로드 중...")
    
    with open(claude_path, 'r', encoding='utf-8') as f:
        signals_data = json.load(f)
    
    gpt4o_data = load_gpt4o_verifications()
    
    print(f"시그널 데이터: {len(signals_data)}개")
    print(f"GPT-4o 데이터: {len(gpt4o_data)}개")
    
    # HTML 생성
    html_template = create_html_template()
    
    # 데이터 삽입
    html_content = html_template.replace(
        '/*SIGNALS_DATA_PLACEHOLDER*/', 
        json.dumps(signals_data, ensure_ascii=False)
    ).replace(
        '/*GPT4O_DATA_PLACEHOLDER*/', 
        json.dumps(gpt4o_data, ensure_ascii=False)
    )
    
    # 파일 저장
    output_path = "C:\\Users\\Mario\\work\\invest-sns\\signal-review.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 리뷰 페이지 생성 완료: {output_path}")
    print(f"   파일 크기: {len(html_content):,} bytes")
    print(f"   브라우저에서 파일을 열어서 리뷰를 시작하세요!")

if __name__ == "__main__":
    main()