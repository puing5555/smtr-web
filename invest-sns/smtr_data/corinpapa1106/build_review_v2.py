#!/usr/bin/env python3
"""Build signal review HTML v2 - 8 signal types, Claude-only pipeline"""
import json
import os

with open('_deduped_signals_8types_dated.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

# Load video metadata
videos_meta = {}
if os.path.exists('_all_videos.json'):
    with open('_all_videos.json', 'r', encoding='utf-8') as f:
        for v in json.load(f):
            vid = v.get('video_id') or v.get('id', '')
            videos_meta[vid] = v

# Enrich signals with video metadata
for sig in signals:
    vid = sig.get('video_id', '')
    meta = videos_meta.get(vid, {})
    if not sig.get('title'):
        sig['title'] = meta.get('title', vid)
    if not sig.get('channel'):
        sig['channel'] = meta.get('channel', '코린이 아빠')

# Convert timestamp string to seconds
def parse_timestamp(ts_str):
    if not ts_str:
        return None
    ts_str = ts_str.strip('[] ')
    parts = ts_str.split(':')
    try:
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        pass
    return None

for sig in signals:
    ts = sig.get('timestamp', '')
    sig['timestamp_seconds'] = parse_timestamp(ts)

# Normalize date field
for sig in signals:
    if not sig.get('date') and sig.get('upload_date'):
        sig['date'] = sig['upload_date']

# Sort by date (newest first)
signals.sort(key=lambda s: s.get('date', ''), reverse=True)

from collections import Counter
types = Counter(s['signal_type'] for s in signals)
print(f'Building HTML with {len(signals)} signals')
print(f'Types: {dict(types)}')

html = '''<!DOCTYPE html>
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
        .signal-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #ccc; }
        .signal-card[data-signal="STRONG_BUY"] { border-left-color: #dc2626; }
        .signal-card[data-signal="BUY"] { border-left-color: #ef4444; }
        .signal-card[data-signal="POSITIVE"] { border-left-color: #f97316; }
        .signal-card[data-signal="HOLD"] { border-left-color: #eab308; }
        .signal-card[data-signal="NEUTRAL"] { border-left-color: #6b7280; }
        .signal-card[data-signal="CONCERN"] { border-left-color: #8b5cf6; }
        .signal-card[data-signal="SELL"] { border-left-color: #3b82f6; }
        .signal-card[data-signal="STRONG_SELL"] { border-left-color: #1d4ed8; }
        .signal-card.hide { display: none; }
        .signal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
        .signal-asset { font-size: 18px; font-weight: 700; }
        .signal-type { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; color: white; }
        .signal-type.STRONG_BUY { background: #dc2626; }
        .signal-type.BUY { background: #ef4444; }
        .signal-type.POSITIVE { background: #f97316; }
        .signal-type.HOLD { background: #eab308; }
        .signal-type.NEUTRAL { background: #6b7280; }
        .signal-type.CONCERN { background: #8b5cf6; }
        .signal-type.SELL { background: #3b82f6; }
        .signal-type.STRONG_SELL { background: #1d4ed8; }
        .quote { background: #f8f9fa; padding: 12px 16px; border-radius: 8px; margin: 12px 0; font-style: italic; color: #333; border-left: 3px solid #667eea; }
        .meta { display: flex; gap: 16px; font-size: 13px; color: #666; margin-top: 8px; flex-wrap: wrap; }
        .meta a { color: #ef4444; text-decoration: none; }
        .meta a:hover { text-decoration: underline; }
        .signal-actions { display: flex; gap: 8px; }
        .btn { padding: 6px 14px; border-radius: 8px; border: 1px solid #ddd; background: white; cursor: pointer; font-size: 13px; }
        .btn:hover { background: #f0f0f0; }
        .btn-submit { background: #667eea; color: white; padding: 12px 24px; border-radius: 12px; border: none; cursor: pointer; font-size: 16px; font-weight: 600; }
        .btn-submit:hover { background: #5a6fd6; }
        .submit-bar { background: white; border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); display: flex; gap: 12px; align-items: center; justify-content: space-between; flex-wrap: wrap; }
        .reject-reason { display: none; margin-top: 8px; }
        .reject-reason textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 8px; font-size: 13px; resize: vertical; min-height: 40px; }
        .reject-reason.show { display: block; }
        .review-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
        .review-badge.pending { background: #fef3c7; color: #92400e; }
        .review-badge.approved { background: #d1fae5; color: #065f46; }
        .review-badge.rejected { background: #fee2e2; color: #991b1b; }
        .confidence { font-size: 12px; padding: 2px 8px; border-radius: 10px; }
        .confidence.HIGH { background: #d1fae5; color: #065f46; }
        .confidence.MEDIUM { background: #fef3c7; color: #92400e; }
        .confidence.LOW { background: #fee2e2; color: #991b1b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 유튜버 시그널 검증 리뷰 v3</h1>
            <p>파이프라인: Claude Sonnet(추출) → 사람(최종 검토)</p>
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
        
<!-- submit bar removed -->
        
        <div class="signals-grid" id="signals-container"></div>
    </div>

    <script>
''' + f'        const SIGNALS_DATA = {json.dumps(signals, ensure_ascii=False)};\n' + '''
        function esc(s){if(!s)return '';return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
        const SIGNAL_LABELS = {
            'STRONG_BUY': '강력매수', 'BUY': '매수', 'POSITIVE': '긍정',
            'HOLD': '보유', 'NEUTRAL': '중립', 'CONCERN': '우려',
            'SELL': '매도', 'STRONG_SELL': '강력매도'
        };
        
        function loadReviews() {
            try { return JSON.parse(localStorage.getItem('signal-reviews-v2') || '{}'); }
            catch(e) { return {}; }
        }
        function saveReviews(r) {
            try { localStorage.setItem('signal-reviews-v2', JSON.stringify(r)); }
            catch(e) {}
        }
        
        function setReview(id, status) {
            const r = loadReviews();
            if (status === 'rejected') {
                const reason = prompt('거부 사유를 입력하세요 (선택사항):');
                r[id] = { status, time: new Date().toLocaleString('ko-KR'), reason: reason || '' };
            } else {
                r[id] = { status, time: new Date().toLocaleString('ko-KR') };
            }
            saveReviews(r);
            render();
        }
        
        function exportResults() {
            const reviews = loadReviews();
            const results = { approved: [], rejected: [], pending: [] };
            SIGNALS_DATA.forEach(sig => {
                const id = sig.video_id + '_' + sig.asset;
                const review = reviews[id] || {};
                const entry = { asset: sig.asset, signal_type: sig.signal_type, video_id: sig.video_id, date: sig.date || '' };
                if (review.status === 'approved') results.approved.push(entry);
                else if (review.status === 'rejected') results.rejected.push({ ...entry, reason: review.reason || '' });
                else results.pending.push(entry);
            });
            const summary = '=== 리뷰 결과 ===\\n' +
                '승인: ' + results.approved.length + '개\\n' +
                '거부: ' + results.rejected.length + '개\\n' +
                '대기: ' + results.pending.length + '개\\n\\n' +
                '--- 거부 목록 ---\\n' +
                results.rejected.map(r => r.asset + ' (' + r.signal_type + ') [' + r.video_id + '] 사유: ' + (r.reason || '없음')).join('\\n');
            
            navigator.clipboard.writeText(summary).then(() => {
                alert('클립보드에 복사됨! 텔레그램에 붙여넣기 하세요.');
            }).catch(() => {
                const ta = document.createElement('textarea');
                ta.value = summary;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                alert('클립보드에 복사됨!');
            });
        }
        
        function downloadResults() {
            const reviews = loadReviews();
            const results = SIGNALS_DATA.map(sig => {
                const id = sig.video_id + '_' + sig.asset;
                const review = reviews[id] || { status: 'pending' };
                return {
                    asset: sig.asset,
                    signal_type: sig.signal_type,
                    content: sig.content,
                    video_id: sig.video_id,
                    date: sig.date || '',
                    review_status: review.status,
                    review_reason: review.reason || '',
                    review_time: review.time || ''
                };
            });
            const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'signal-review-results.json';
            a.click();
            URL.revokeObjectURL(url);
        }
        
        function buildCard(sig, idx) {
            const id = sig.video_id + '_' + sig.asset;
            const reviews = loadReviews();
            const review = reviews[id] || { status: 'pending' };
            const tsUrl = sig.timestamp_seconds ? 
                'https://youtube.com/watch?v=' + sig.video_id + '&t=' + sig.timestamp_seconds : 
                'https://youtube.com/watch?v=' + sig.video_id;
            
            var safeId = id.replace(/'/g,"\\\\'");
            return '<div class="signal-card" data-signal="' + sig.signal_type + '" data-asset="' + esc(sig.asset) + '" data-review="' + review.status + '" data-youtuber="' + esc(sig.channel || '') + '" data-index="' + idx + '">' +
                '<div class="signal-header">' +
                    '<div>' +
                        '<span class="signal-asset">' + esc(sig.asset) + '</span> ' +
                        '<span class="signal-type ' + sig.signal_type + '">' + (SIGNAL_LABELS[sig.signal_type] || sig.signal_type) + '</span> ' +
                        '<span class="confidence ' + (sig.confidence || '') + '">' + (sig.confidence || '') + '</span> ' +
                        '<span class="review-badge ' + review.status + '">' + ({pending:'검토대기',approved:'승인',rejected:'거부'}[review.status] || review.status) + '</span> ' +
                        '<span style="font-size:13px;color:#888;">📅 ' + esc(sig.upload_date || sig.date || 'N/A') + '</span>' +
                    '</div>' +
                    '<div class="signal-actions">' +
                        '<label style="cursor:pointer;display:flex;align-items:center;gap:4px;font-size:13px;color:#666;"><input type="checkbox" ' + (review.status==='approved'?'checked':'') + ' onchange="setReview(\\'' + safeId + '\\', this.checked?\\'approved\\':\\'pending\\')"> 승인</label>' +
                        '<label style="cursor:pointer;display:flex;align-items:center;gap:4px;font-size:13px;color:#666;"><input type="checkbox" ' + (review.status==='rejected'?'checked':'') + ' onchange="setReview(\\'' + safeId + '\\', this.checked?\\'rejected\\':\\'pending\\')"> 거부</label>' +
                    '</div>' +
                '</div>' +
                '<div class="quote">"' + esc(sig.content || '') + '"</div>' +
                '<div class="meta">' +
                    '<span>📺 <a href="' + esc(tsUrl) + '" target="_blank">' + esc((sig.title || sig.video_id).substring(0, 50)) + ' ▶️</a></span>' +
                    '<span>⏱️ ' + esc(sig.timestamp || 'N/A') + '</span>' +
                    '<span>🎙️ ' + esc(sig.channel || '코린이 아빠') + '</span>' +
                '</div>' +
                (sig.context ? '<div style="margin-top:8px;font-size:13px;color:#666;">💡 ' + esc(sig.context) + '</div>' : '') +
                (sig.video_summary ? '<div style="margin-top:8px;font-size:12px;color:#999;cursor:pointer;" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display===\\'none\\'?\\'block\\':\\'none\\'">📋 영상요약 보기/접기</div><div style="display:none;margin-top:4px;font-size:12px;color:#888;background:#f5f5f5;padding:8px;border-radius:6px;">' + esc(sig.video_summary) + '</div>' : '') +
            '</div>';
        }
        
        function render() {
            const container = document.getElementById('signals-container');
            const assetF = document.getElementById('asset-filter').value;
            const signalF = document.getElementById('signal-filter').value;
            const reviewF = document.getElementById('review-filter').value;
            const youtuberF = document.getElementById('youtuber-filter').value;
            const searchF = document.getElementById('search-input').value.toLowerCase();
            
            const reviews = loadReviews();
            let html = '';
            let shown = 0;
            
            SIGNALS_DATA.forEach((sig, idx) => {
                const id = sig.video_id + '_' + sig.asset;
                const review = (reviews[id] || {}).status || 'pending';
                
                if (assetF && sig.asset !== assetF) return;
                if (signalF && sig.signal_type !== signalF) return;
                if (reviewF && review !== reviewF) return;
                if (youtuberF && (sig.channel || '') !== youtuberF) return;
                if (searchF && !(sig.content || '').toLowerCase().includes(searchF) && 
                    !(sig.asset || '').toLowerCase().includes(searchF) &&
                    !(sig.context || '').toLowerCase().includes(searchF)) return;
                
                html += buildCard(sig, idx);
                shown++;
            });
            
            container.innerHTML = html || '<div style="text-align:center;padding:40px;color:#666;">필터 조건에 맞는 시그널이 없습니다.</div>';
            
            // Update stats
            const reviews2 = loadReviews();
            let approved = 0, rejected = 0;
            SIGNALS_DATA.forEach(sig => {
                const r = (reviews2[sig.video_id + '_' + sig.asset] || {}).status;
                if (r === 'approved') approved++;
                if (r === 'rejected') rejected++;
            });
            
            const statsHtml = [
                { n: SIGNALS_DATA.length, l: '총 시그널' },
                { n: SIGNALS_DATA.length - approved - rejected, l: '검토 대기' },
                { n: approved, l: '승인됨' },
                { n: rejected, l: '거부됨' },
                { n: shown, l: '현재 표시' }
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
        
        document.addEventListener('DOMContentLoaded', function() {
            initFilters();
            render();
        });
    </script>
</body>
</html>'''

output_path = os.path.join('..', '..', 'signal-review-v3.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Saved to {output_path}')
