#!/usr/bin/env python3
"""
인플루언서 투자 시그널 리뷰 페이지 빌드 스크립트
"""
import json
import os
from datetime import datetime
import html

def load_verified_signals(file_path: str):
    """검증된 시그널 데이터 로드"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Verified signals file not found: {file_path}")
        return []

def build_html_page(signals_data: list) -> str:
    """HTML 페이지 생성"""
    
    # 통계 계산
    stats = {
        'total': len(signals_data),
        'confirmed': 0,
        'modified': 0,
        'rejected': 0
    }
    
    for signal in signals_data:
        verdict = signal.get('claude_verification', {}).get('verdict', 'unknown')
        if verdict == '확인됨':
            stats['confirmed'] += 1
        elif verdict == '수정됨':
            stats['modified'] += 1
        elif verdict == '거부됨':
            stats['rejected'] += 1
    
    # 시그널 타입별 통계
    signal_types = {}
    for signal in signals_data:
        sig_type = signal.get('signal_type', 'UNKNOWN')
        signal_types[sig_type] = signal_types.get(sig_type, 0) + 1
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>인플루언서 투자 시그널 리뷰</title>
    <style>
        :root {{
            --primary-color: #2563eb;
            --success-color: #16a34a;
            --warning-color: #d97706;
            --danger-color: #dc2626;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-primary: #0f172a;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary-color), #3b82f6);
            color: white;
            padding: 2rem 1rem;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }}
        
        .header p {{
            margin: 0.5rem 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .confirmed {{ color: var(--success-color); }}
        .modified {{ color: var(--warning-color); }}
        .rejected {{ color: var(--danger-color); }}
        
        .filters {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 0.75rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .filter-row {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}
        
        .filter-group label {{
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-secondary);
        }}
        
        .filter-group select,
        .filter-group input {{
            padding: 0.5rem;
            border: 1px solid var(--border-color);
            border-radius: 0.375rem;
            font-size: 0.875rem;
            min-width: 150px;
        }}
        
        .signals-table {{
            background: var(--card-bg);
            border-radius: 0.75rem;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        th {{
            background: #f1f5f9;
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
        }}
        
        tr:hover {{
            background: #f8fafc;
        }}
        
        .asset-cell {{
            font-weight: 600;
            color: var(--primary-color);
        }}
        
        .signal-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
        }}
        
        .buy {{ background: #dcfce7; color: #166534; }}
        .sell {{ background: #fee2e2; color: #991b1b; }}
        .hold {{ background: #fef3c7; color: #92400e; }}
        .price-target {{ background: #ddd6fe; color: #6b21a8; }}
        .market-view {{ background: #e0f2fe; color: #0c4a6e; }}
        
        .verdict-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        .verdict-confirmed {{
            background: #dcfce7;
            color: #166534;
        }}
        
        .verdict-modified {{
            background: #fef3c7;
            color: #92400e;
        }}
        
        .verdict-rejected {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .confidence-bar {{
            width: 60px;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .confidence-fill {{
            height: 100%;
            background: var(--success-color);
            transition: width 0.3s;
        }}
        
        .video-link {{
            color: var(--primary-color);
            text-decoration: none;
            font-size: 0.875rem;
        }}
        
        .video-link:hover {{
            text-decoration: underline;
        }}
        
        .review-actions {{
            display: flex;
            gap: 0.5rem;
        }}
        
        .review-btn {{
            padding: 0.25rem 0.5rem;
            border: none;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            cursor: pointer;
            font-weight: 500;
        }}
        
        .btn-approve {{
            background: var(--success-color);
            color: white;
        }}
        
        .btn-reject {{
            background: var(--danger-color);
            color: white;
        }}
        
        .btn-modify {{
            background: var(--warning-color);
            color: white;
        }}
        
        .review-status {{
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-weight: 500;
        }}
        
        .status-approved {{
            background: #dcfce7;
            color: #166534;
        }}
        
        .status-rejected {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .status-modified {{
            background: #fef3c7;
            color: #92400e;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.875rem;
            }}
            
            .filter-row {{
                flex-direction: column;
            }}
            
            .signals-table {{
                overflow-x: auto;
            }}
            
            table {{
                min-width: 800px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>인플루언서 투자 시그널 리뷰</h1>
        <p>코린이 아빠 시그널 검증 결과 · 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats['total']}</div>
                <div class="stat-label">전체 시그널</div>
            </div>
            <div class="stat-card">
                <div class="stat-number confirmed">{stats['confirmed']}</div>
                <div class="stat-label">확인됨</div>
            </div>
            <div class="stat-card">
                <div class="stat-number modified">{stats['modified']}</div>
                <div class="stat-label">수정됨</div>
            </div>
            <div class="stat-card">
                <div class="stat-number rejected">{stats['rejected']}</div>
                <div class="stat-label">거부됨</div>
            </div>
        </div>
        
        <div class="filters">
            <div class="filter-row">
                <div class="filter-group">
                    <label>종목 필터</label>
                    <select id="assetFilter">
                        <option value="">모든 종목</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>시그널 타입</label>
                    <select id="signalTypeFilter">
                        <option value="">모든 타입</option>
                        <option value="BUY">매수</option>
                        <option value="SELL">매도</option>
                        <option value="HOLD">보유</option>
                        <option value="PRICE_TARGET">목표가</option>
                        <option value="MARKET_VIEW">시장 전망</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Claude 판정</label>
                    <select id="verdictFilter">
                        <option value="">모든 판정</option>
                        <option value="확인됨">확인됨</option>
                        <option value="수정됨">수정됨</option>
                        <option value="거부됨">거부됨</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>신뢰도 최소</label>
                    <select id="confidenceFilter">
                        <option value="0">모든 신뢰도</option>
                        <option value="0.8">80% 이상</option>
                        <option value="0.9">90% 이상</option>
                        <option value="0.95">95% 이상</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>검색</label>
                    <input type="text" id="searchInput" placeholder="종목명, 내용 검색">
                </div>
            </div>
        </div>
        
        <div class="signals-table">
            <table>
                <thead>
                    <tr>
                        <th>종목 · 인플루언서</th>
                        <th>시그널</th>
                        <th>GPT 추출 내용</th>
                        <th>Claude 검증</th>
                        <th>신뢰도</th>
                        <th>영상</th>
                        <th>인간 검토</th>
                    </tr>
                </thead>
                <tbody id="signalsTable">
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // 시그널 데이터 (JSON으로 내장)
        const signalsData = {json.dumps(signals_data, ensure_ascii=False, indent=8)};
        
        // DOM 요소
        const assetFilter = document.getElementById('assetFilter');
        const signalTypeFilter = document.getElementById('signalTypeFilter');
        const verdictFilter = document.getElementById('verdictFilter');
        const confidenceFilter = document.getElementById('confidenceFilter');
        const searchInput = document.getElementById('searchInput');
        const signalsTable = document.getElementById('signalsTable');
        
        // 로컬스토리지에서 리뷰 상태 로드
        function loadReviewStatus() {{
            const saved = localStorage.getItem('signalReviews');
            return saved ? JSON.parse(saved) : {{}};
        }}
        
        // 로컬스토리지에 리뷰 상태 저장
        function saveReviewStatus(reviews) {{
            localStorage.setItem('signalReviews', JSON.stringify(reviews));
        }}
        
        // 종목 필터 옵션 채우기
        function populateAssetFilter() {{
            const assets = [...new Set(signalsData.map(s => s.asset))].sort();
            assets.forEach(asset => {{
                const option = document.createElement('option');
                option.value = asset;
                option.textContent = asset;
                assetFilter.appendChild(option);
            }});
        }}
        
        // 시그널 타입 표시 함수
        function getSignalBadge(signalType) {{
            const badges = {{
                'BUY': '<span class="signal-badge buy">매수</span>',
                'SELL': '<span class="signal-badge sell">매도</span>',
                'HOLD': '<span class="signal-badge hold">보유</span>',
                'PRICE_TARGET': '<span class="signal-badge price-target">목표가</span>',
                'MARKET_VIEW': '<span class="signal-badge market-view">시장전망</span>'
            }};
            return badges[signalType] || `<span class="signal-badge">${{signalType}}</span>`;
        }}
        
        // 판정 배지 표시 함수
        function getVerdictBadge(verdict) {{
            const badges = {{
                '확인됨': '<span class="verdict-badge verdict-confirmed">확인됨</span>',
                '수정됨': '<span class="verdict-badge verdict-modified">수정됨</span>',
                '거부됨': '<span class="verdict-badge verdict-rejected">거부됨</span>'
            }};
            return badges[verdict] || `<span class="verdict-badge">${{verdict}}</span>`;
        }}
        
        // 신뢰도 바 표시 함수
        function getConfidenceBar(confidence) {{
            const percentage = Math.round(confidence * 100);
            return `
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${{percentage}}%"></div>
                </div>
                <small>${{percentage}}%</small>
            `;
        }}
        
        // 영상 링크 생성 함수
        function getVideoLink(videoId, title) {{
            if (!videoId) return '-';
            const url = `https://youtube.com/watch?v=${{videoId}}`;
            return `<a href="${{url}}" target="_blank" class="video-link" title="${{html.escape(title || '')}}">${{videoId.slice(0, 8)}}...</a>`;
        }}
        
        // 리뷰 액션 버튼 생성
        function getReviewActions(index, currentStatus) {{
            if (currentStatus) {{
                const statusClasses = {{
                    'approved': 'status-approved',
                    'rejected': 'status-rejected',
                    'modified': 'status-modified'
                }};
                const statusTexts = {{
                    'approved': '승인됨',
                    'rejected': '거부됨',
                    'modified': '수정됨'
                }};
                return `<span class="review-status ${{statusClasses[currentStatus] || ''}}">${{statusTexts[currentStatus] || currentStatus}}</span>`;
            }}
            
            return `
                <div class="review-actions">
                    <button class="review-btn btn-approve" onclick="setReview(${{index}}, 'approved')">승인</button>
                    <button class="review-btn btn-reject" onclick="setReview(${{index}}, 'rejected')">거부</button>
                    <button class="review-btn btn-modify" onclick="setReview(${{index}}, 'modified')">수정</button>
                </div>
            `;
        }}
        
        // 리뷰 상태 설정
        function setReview(index, status) {{
            const reviews = loadReviewStatus();
            const signal = signalsData[index];
            const key = `${{signal.video_id}}-${{signal.asset}}-${{signal.signal_type}}`;
            reviews[key] = status;
            saveReviewStatus(reviews);
            renderTable();
        }}
        
        // 테이블 렌더링
        function renderTable() {{
            const reviews = loadReviewStatus();
            let filteredSignals = signalsData.slice();
            
            // 필터 적용
            if (assetFilter.value) {{
                filteredSignals = filteredSignals.filter(s => s.asset === assetFilter.value);
            }}
            
            if (signalTypeFilter.value) {{
                filteredSignals = filteredSignals.filter(s => s.signal_type === signalTypeFilter.value);
            }}
            
            if (verdictFilter.value) {{
                filteredSignals = filteredSignals.filter(s => 
                    s.claude_verification && s.claude_verification.verdict === verdictFilter.value
                );
            }}
            
            if (confidenceFilter.value !== '0') {{
                const minConf = parseFloat(confidenceFilter.value);
                filteredSignals = filteredSignals.filter(s => 
                    s.claude_verification && s.claude_verification.confidence >= minConf
                );
            }}
            
            if (searchInput.value) {{
                const search = searchInput.value.toLowerCase();
                filteredSignals = filteredSignals.filter(s => 
                    s.asset.toLowerCase().includes(search) ||
                    (s.content && s.content.toLowerCase().includes(search))
                );
            }}
            
            // 최신순 정렬 (임시로 인덱스 기준)
            filteredSignals.sort((a, b) => signalsData.indexOf(b) - signalsData.indexOf(a));
            
            // 테이블 렌더링
            signalsTable.innerHTML = filteredSignals.map((signal, i) => {{
                const originalIndex = signalsData.indexOf(signal);
                const key = `${{signal.video_id}}-${{signal.asset}}-${{signal.signal_type}}`;
                const reviewStatus = reviews[key];
                const verification = signal.claude_verification || {{}};
                
                return `
                    <tr>
                        <td class="asset-cell">
                            <strong>${{signal.asset}} · 코린이 아빠</strong>
                        </td>
                        <td>${{getSignalBadge(signal.signal_type)}}</td>
                        <td>
                            <div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">
                                ${{html.escape(signal.content || '')}}
                            </div>
                            <small style="color: var(--text-secondary);">
                                신뢰도: ${{signal.confidence || 'N/A'}}
                            </small>
                        </td>
                        <td>
                            ${{getVerdictBadge(verification.verdict || 'unknown')}}
                            <br>
                            <small>${{html.escape(verification.reason || '')}}</small>
                        </td>
                        <td>
                            ${{getConfidenceBar(verification.confidence || 0)}}
                        </td>
                        <td>
                            ${{getVideoLink(signal.video_id, signal.title)}}
                        </td>
                        <td>
                            ${{getReviewActions(originalIndex, reviewStatus)}}
                        </td>
                    </tr>
                `;
            }}).join('');
        }}
        
        // 이벤트 리스너
        assetFilter.addEventListener('change', renderTable);
        signalTypeFilter.addEventListener('change', renderTable);
        verdictFilter.addEventListener('change', renderTable);
        confidenceFilter.addEventListener('change', renderTable);
        searchInput.addEventListener('input', renderTable);
        
        // 초기화
        populateAssetFilter();
        renderTable();
    </script>
</body>
</html>
    """
    
    return html_content

def main():
    # 파일 경로
    verified_signals_path = r"C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_claude_sonnet_verify.json"
    output_path = r"C:\Users\Mario\work\invest-sns\signal-review.html"
    
    print("Loading verified signals...")
    signals_data = load_verified_signals(verified_signals_path)
    
    if not signals_data:
        print("No signals data found. Make sure Claude verification is completed first.")
        return
    
    print(f"Building HTML page with {len(signals_data)} signals...")
    html_content = build_html_page(signals_data)
    
    print(f"Writing HTML file to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Review page built successfully: {output_path}")
    print(f"📊 Statistics:")
    
    # 통계 출력
    stats = {'confirmed': 0, 'modified': 0, 'rejected': 0}
    for signal in signals_data:
        verdict = signal.get('claude_verification', {}).get('verdict', 'unknown')
        if verdict == '확인됨':
            stats['confirmed'] += 1
        elif verdict == '수정됨':
            stats['modified'] += 1
        elif verdict == '거부됨':
            stats['rejected'] += 1
    
    print(f"  - 전체: {len(signals_data)}")
    print(f"  - 확인됨: {stats['confirmed']}")
    print(f"  - 수정됨: {stats['modified']}")
    print(f"  - 거부됨: {stats['rejected']}")

if __name__ == "__main__":
    main()