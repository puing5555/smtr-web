const fs = require('fs');

// Read 194 signals
const signals = JSON.parse(fs.readFileSync('invest-sns/smtr_data/corinpapa1106/_all_signals_194.json', 'utf8'));

// Map to display format
const mapped = signals.map((s, i) => ({
  id: i + 1,
  video_id: s.video_id || '',
  stock: s.asset || 'N/A',
  signal: (s.signal_type || '').toUpperCase(),
  quote: s.content || '',
  detail: s.context || '',
  confidence: s.confidence || '',
  influencer: '코린이 아빠',
  title: s.title || ''
}));

const html = `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>시그널 검증 리뷰 (194개)</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f7fa;color:#333;line-height:1.6}
.container{max-width:1000px;margin:0 auto;padding:20px}
.header{background:#fff;padding:24px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:20px}
.header h1{font-size:24px;color:#1a1a2e;margin-bottom:8px}
.header p{color:#666;font-size:14px}
.stats{display:flex;gap:16px;flex-wrap:wrap;margin:16px 0;padding:16px;background:#f0f4ff;border-radius:8px}
.stat{text-align:center;min-width:80px}
.stat .num{font-size:28px;font-weight:900;color:#3b82f6}
.stat .lbl{font-size:11px;color:#666}
.pipeline{display:flex;align-items:center;justify-content:center;gap:8px;margin:16px 0;flex-wrap:wrap}
.pipe-step{background:#3b82f6;color:#fff;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
.pipe-label{font-size:12px;color:#666;text-align:center}
.pipe-arrow{color:#ccc;font-size:18px}
.filters{display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap;align-items:center}
.filters select{padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:14px;background:#fff}
.filters input{padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:14px;flex:1;min-width:200px}
.signal-card{background:#fff;border-radius:12px;padding:20px;margin-bottom:12px;box-shadow:0 1px 4px rgba(0,0,0,.06);border-left:4px solid #ddd}
.signal-card.BUY{border-left-color:#10b981}
.signal-card.SELL{border-left-color:#ef4444}
.signal-card.HOLD{border-left-color:#f59e0b}
.signal-card.PRICE_TARGET{border-left-color:#3b82f6}
.signal-card.MARKET_VIEW{border-left-color:#8b5cf6}
.card-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:8px}
.card-stock{font-size:18px;font-weight:700}
.card-signal{padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700;color:#fff}
.card-signal.BUY{background:#10b981}
.card-signal.SELL{background:#ef4444}
.card-signal.HOLD{background:#f59e0b}
.card-signal.PRICE_TARGET{background:#3b82f6}
.card-signal.MARKET_VIEW{background:#8b5cf6}
.card-quote{background:#f8f9fa;padding:12px;border-radius:8px;font-size:14px;color:#555;margin:8px 0;border-left:3px solid #ddd;font-style:italic}
.card-detail{font-size:13px;color:#777;margin-bottom:12px}
.card-meta{font-size:12px;color:#999;display:flex;gap:16px;flex-wrap:wrap}
.card-actions{display:flex;gap:8px;margin-top:12px}
.btn{padding:8px 20px;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;transition:.2s}
.btn-approve{background:#d1fae5;color:#065f46}.btn-approve:hover{background:#10b981;color:#fff}
.btn-reject{background:#fee2e2;color:#991b1b}.btn-reject:hover{background:#ef4444;color:#fff}
.btn-modify{background:#fef3c7;color:#92400e}.btn-modify:hover{background:#f59e0b;color:#fff}
.btn-approve.active{background:#10b981;color:#fff}
.btn-reject.active{background:#ef4444;color:#fff}
.btn-modify.active{background:#f59e0b;color:#fff}
.confidence{font-size:11px;padding:2px 8px;border-radius:10px;background:#e0e7ff;color:#3730a3}
.export-btn{padding:10px 20px;background:#3b82f6;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:14px}
.export-btn:hover{background:#2563eb}
.yt-link{color:#f00;text-decoration:none;font-size:12px;font-weight:600}
.yt-link:hover{text-decoration:underline}
@media(max-width:640px){.stats{gap:8px}.stat .num{font-size:20px}.card-actions{flex-direction:column}}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📊 신호 검증 리뷰 시스템</h1>
    <p>인플루언서 시그널의 검증 결과를 사람이 최종 검토합니다.</p>
    <div class="pipeline">
      <div><div class="pipe-step">1</div><div class="pipe-label">GPT-4o-mini<br>시그널 추출</div></div>
      <div class="pipe-arrow">→</div>
      <div><div class="pipe-step">2</div><div class="pipe-label">GPT-4o<br>정확도 검증</div></div>
      <div class="pipe-arrow">→</div>
      <div><div class="pipe-step">3</div><div class="pipe-label">Claude Opus<br>독립 검증</div></div>
      <div class="pipe-arrow">→</div>
      <div><div class="pipe-step">4</div><div class="pipe-label">사람<br>최종 승인</div></div>
    </div>
    <div class="stats" id="stats"></div>
    <div style="margin-top:12px;display:flex;gap:8px">
      <button class="export-btn" onclick="exportResults()">📥 결과 내보내기</button>
    </div>
  </div>
  <div class="filters">
    <select id="filterSignal" onchange="render()">
      <option value="">전체 신호</option>
      <option value="BUY">매수 (BUY)</option>
      <option value="SELL">매도 (SELL)</option>
      <option value="HOLD">보유 (HOLD)</option>
      <option value="PRICE_TARGET">목표가</option>
      <option value="MARKET_VIEW">시장전망</option>
    </select>
    <select id="filterStatus" onchange="render()">
      <option value="">전체 상태</option>
      <option value="pending">검토 대기</option>
      <option value="approved">승인됨</option>
      <option value="rejected">거부됨</option>
      <option value="modified">수정됨</option>
    </select>
    <input type="text" id="filterSearch" placeholder="종목명 검색..." oninput="render()">
  </div>
  <div id="list"></div>
</div>
<script>
const DATA = ${JSON.stringify(mapped)};
const reviews = JSON.parse(localStorage.getItem('signalReviews2') || '{}');

function getStatus(id) { return (reviews[id] || {}).status || 'pending'; }

function review(id, status) {
  reviews[id] = { status, timestamp: new Date().toISOString() };
  localStorage.setItem('signalReviews2', JSON.stringify(reviews));
  render();
}

function render() {
  const sigFilter = document.getElementById('filterSignal').value;
  const statFilter = document.getElementById('filterStatus').value;
  const search = document.getElementById('filterSearch').value.toLowerCase();
  
  let filtered = DATA.filter(s => {
    if (sigFilter && s.signal !== sigFilter) return false;
    if (statFilter && getStatus(s.id) !== statFilter) return false;
    if (search && !s.stock.toLowerCase().includes(search)) return false;
    return true;
  });

  // Stats
  const total = DATA.length;
  const approved = Object.values(reviews).filter(r => r.status === 'approved').length;
  const rejected = Object.values(reviews).filter(r => r.status === 'rejected').length;
  const modified = Object.values(reviews).filter(r => r.status === 'modified').length;
  const pending = total - approved - rejected - modified;
  
  document.getElementById('stats').innerHTML = [
    ['총 시그널', total, '#3b82f6'],
    ['검토 대기', pending, '#666'],
    ['승인', approved, '#10b981'],
    ['거부', rejected, '#ef4444'],
    ['수정', modified, '#f59e0b']
  ].map(([l,n,c]) => '<div class="stat"><div class="num" style="color:'+c+'">'+n+'</div><div class="lbl">'+l+'</div></div>').join('');

  document.getElementById('list').innerHTML = filtered.map(s => {
    const st = getStatus(s.id);
    return '<div class="signal-card ' + s.signal + '">' +
      '<div class="card-top">' +
        '<span class="card-stock">' + s.stock + '</span>' +
        '<span>' +
          '<span class="card-signal ' + s.signal + '">' + s.signal + '</span> ' +
          (s.confidence ? '<span class="confidence">' + s.confidence + '</span>' : '') +
        '</span>' +
      '</div>' +
      '<div class="card-quote">"' + s.quote + '"</div>' +
      '<div class="card-detail">' + s.detail + '</div>' +
      '<div class="card-meta">' +
        '<span>👤 ' + s.influencer + '</span>' +
        '<span>🎬 <a class="yt-link" href="https://youtube.com/watch?v=' + s.video_id + '" target="_blank">' + (s.title||s.video_id) + '</a></span>' +
      '</div>' +
      '<div class="card-actions">' +
        '<button class="btn btn-approve' + (st==='approved'?' active':'') + '" onclick="review('+s.id+',\\'approved\\')">✅ 승인</button>' +
        '<button class="btn btn-reject' + (st==='rejected'?' active':'') + '" onclick="review('+s.id+',\\'rejected\\')">❌ 거부</button>' +
        '<button class="btn btn-modify' + (st==='modified'?' active':'') + '" onclick="review('+s.id+',\\'modified\\')">🔄 수정</button>' +
      '</div>' +
    '</div>';
  }).join('');
}

function exportResults() {
  const blob = new Blob([JSON.stringify({reviews, total: DATA.length, date: new Date().toISOString()}, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'signal-reviews-' + new Date().toISOString().split('T')[0] + '.json';
  a.click();
}

render();
</script>
</body>
</html>`;

fs.writeFileSync('invest-sns/signal-review.html', html);
console.log('Built fresh! Signals:', mapped.length);
