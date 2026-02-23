"""Signal Review Server v4 - Sonnet extraction → Opus verification → Human review"""
import json, os, sys, time, threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

DATA_DIR = os.path.join('smtr_data', 'corinpapa1106')
SIGNALS_FILE = os.path.join(DATA_DIR, '_all_signals_8types.json')
REVIEW_FILE = os.path.join(DATA_DIR, '_review_results_v4.json')
OPUS_REVIEW_FILE = os.path.join(DATA_DIR, '_opus_review_results.json')

# Progress tracking for batch opus review
opus_progress = {"running": False, "total": 0, "done": 0, "errors": 0}

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_signals():
    sigs = load_json(SIGNALS_FILE)
    if isinstance(sigs, list):
        return sigs
    return []

def sig_id(sig):
    return sig.get('video_id','') + '_' + sig.get('asset','')

def call_opus(sig):
    """Call Anthropic API to verify a signal with Opus"""
    import urllib.request
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return {"verdict": "error", "reasoning": "No ANTHROPIC_API_KEY set"}

    prompt = f"""You are verifying a stock/crypto signal extracted from a Korean YouTube video by "코린이 아빠" channel.

Signal: {sig.get('signal_type')} for {sig.get('asset')}
Content: "{sig.get('content','')}"
Context: "{sig.get('context','')}"
Video title: "{sig.get('title','')}"
Video summary: "{sig.get('video_summary','')}"
Confidence: {sig.get('confidence','')}
Timeframe: {sig.get('timeframe','')}
Conditional: {sig.get('conditional',False)}
Skin in game: {sig.get('skin_in_game',False)}

Verify:
1. Does the content actually express a {sig.get('signal_type')} signal for {sig.get('asset')}?
2. Is the confidence level ({sig.get('confidence','')}) appropriate given the content?
3. Is this a genuine actionable trading signal or just general commentary?
4. Are there any issues with the extraction?

Valid signal types: STRONG_BUY, BUY, POSITIVE, HOLD, NEUTRAL, CONCERN, SELL, STRONG_SELL

Reply in JSON only (no markdown): {{"verdict": "approve"|"reject"|"modify", "correct_signal_type": "...", "correct_confidence": "HIGH|MEDIUM|LOW", "reasoning": "Korean explanation of your verdict", "is_actionable": true|false}}"""

    body = json.dumps({
        "model": "claude-opus-4-20250514",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}]
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=body,
        headers={
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            text = result['content'][0]['text']
            # Try parse JSON from response
            text = text.strip()
            if text.startswith('```'): 
                text = text.split('\n',1)[1].rsplit('```',1)[0].strip()
            return json.loads(text)
    except Exception as e:
        return {"verdict": "error", "reasoning": str(e)}

def run_opus_batch(signal_ids=None):
    """Run Opus review on signals. If signal_ids is None, review all pending."""
    global opus_progress
    signals = load_signals()
    opus_reviews = load_json(OPUS_REVIEW_FILE) if os.path.exists(OPUS_REVIEW_FILE) else {}

    if signal_ids:
        to_review = [s for s in signals if sig_id(s) in signal_ids]
    else:
        to_review = [s for s in signals if sig_id(s) not in opus_reviews]

    opus_progress = {"running": True, "total": len(to_review), "done": 0, "errors": 0}

    def review_one(sig):
        global opus_progress
        sid = sig_id(sig)
        result = call_opus(sig)
        result['reviewed_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        opus_reviews[sid] = result
        save_json(OPUS_REVIEW_FILE, opus_reviews)
        opus_progress["done"] += 1
        if result.get("verdict") == "error":
            opus_progress["errors"] += 1

    # Sequential to avoid rate limits, but in a background thread
    for sig in to_review:
        review_one(sig)
        time.sleep(0.5)  # Rate limit buffer

    opus_progress["running"] = False

class ReviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path in ('/', '/review'):
            self._send_html(build_html())
        elif parsed.path == '/api/signals':
            sigs = load_signals()
            sigs.sort(key=lambda s: s.get('title',''), reverse=True)
            self._send_json(sigs)
        elif parsed.path == '/api/reviews':
            self._send_json(load_json(REVIEW_FILE))
        elif parsed.path == '/api/opus-reviews':
            self._send_json(load_json(OPUS_REVIEW_FILE) if os.path.exists(OPUS_REVIEW_FILE) else {})
        elif parsed.path == '/api/opus-progress':
            self._send_json(opus_progress)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        body = self.rfile.read(int(self.headers.get('Content-Length', 0))).decode('utf-8')
        data = json.loads(body) if body else {}

        if parsed.path == '/api/review':
            reviews = load_json(REVIEW_FILE)
            sid = data.get('id','')
            reviews[sid] = {
                'status': data.get('status','pending'),
                'reason': data.get('reason',''),
                'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            save_json(REVIEW_FILE, reviews)
            self._send_json({'ok': True})

        elif parsed.path == '/api/opus-review-all':
            if opus_progress.get("running"):
                self._send_json({"ok": False, "error": "Already running"})
                return
            ids = data.get('signal_ids', None)
            t = threading.Thread(target=run_opus_batch, args=(ids,), daemon=True)
            t.start()
            self._send_json({"ok": True, "message": "Opus batch review started"})
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')

    def _send_json(self, obj):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))

    def _send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self._cors()
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        pass

def build_html():
    return '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🔍 코린이 아빠 시그널 검증</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f0f23;color:#e2e8f0}
.container{max-width:1200px;margin:0 auto;padding:20px}
.header{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:30px;border-radius:16px;margin-bottom:24px}
.header h1{font-size:24px;margin-bottom:8px}
.header p{opacity:.9;font-size:14px}
.opus-bar{display:flex;gap:12px;align-items:center;margin-top:12px}
.opus-btn{background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.4);color:#fff;padding:8px 20px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600}
.opus-btn:hover{background:rgba(255,255,255,.3)}
.opus-btn:disabled{opacity:.5;cursor:not-allowed}
.progress-bar{flex:1;height:8px;background:rgba(255,255,255,.2);border-radius:4px;overflow:hidden;display:none}
.progress-fill{height:100%;background:#4ade80;transition:width .3s}
.progress-text{font-size:13px;opacity:.9;display:none}
.stats{display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap}
.stat-card{background:#1a1a2e;border-radius:12px;padding:16px 20px;flex:1;min-width:100px;text-align:center;border:1px solid #2d2d44}
.stat-number{font-size:28px;font-weight:700;color:#667eea}
.stat-label{font-size:12px;color:#888;margin-top:4px}
.filters{background:#1a1a2e;border-radius:12px;padding:20px;margin-bottom:24px;border:1px solid #2d2d44}
.filter-row{display:flex;gap:12px;flex-wrap:wrap;align-items:end}
.filter-group{display:flex;flex-direction:column;gap:4px}
.filter-label{font-size:12px;font-weight:600;color:#888}
.filter-select,.filter-input{padding:8px 12px;border:1px solid #2d2d44;border-radius:8px;font-size:14px;background:#0f0f23;color:#e2e8f0}
.signals-grid{display:flex;flex-direction:column;gap:16px}
.signal-card{background:#1a1a2e;border-radius:12px;padding:20px;border:1px solid #2d2d44;border-left:4px solid #444;transition:all .3s}
.signal-card[data-signal="STRONG_BUY"]{border-left-color:#10b981}
.signal-card[data-signal="BUY"]{border-left-color:#86efac}
.signal-card[data-signal="POSITIVE"]{border-left-color:#60a5fa}
.signal-card[data-signal="HOLD"]{border-left-color:#06b6d4}
.signal-card[data-signal="NEUTRAL"]{border-left-color:#94a3b8}
.signal-card[data-signal="CONCERN"]{border-left-color:#fdba74}
.signal-card[data-signal="SELL"]{border-left-color:#fb923c}
.signal-card[data-signal="STRONG_SELL"]{border-left-color:#f87171}
.signal-card.human-done{opacity:.6}
.signal-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px}
.signal-asset{font-size:18px;font-weight:700}
.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;color:#fff}
.badge.STRONG_BUY{background:#10b981}.badge.BUY{background:#86efac;color:#065f46}.badge.POSITIVE{background:#60a5fa}
.badge.HOLD{background:#06b6d4}.badge.NEUTRAL{background:#94a3b8}.badge.CONCERN{background:#fdba74;color:#7c2d12}
.badge.SELL{background:#fb923c}.badge.STRONG_SELL{background:#f87171}
.badge.conf-HIGH{background:#052e16;color:#4ade80}.badge.conf-MEDIUM{background:#422006;color:#f59e0b}.badge.conf-LOW{background:#450a0a;color:#fca5a5}
.badge.pending{background:#422006;color:#f59e0b}.badge.approved{background:#052e16;color:#4ade80}.badge.rejected{background:#450a0a;color:#fca5a5}
.badge.opus-approve{background:#052e16;color:#4ade80}.badge.opus-reject{background:#450a0a;color:#fca5a5}.badge.opus-modify{background:#422006;color:#f59e0b}
.quote{background:#0f0f23;padding:12px 16px;border-radius:8px;margin:12px 0;font-style:italic;color:#ccc;border-left:3px solid #667eea;font-size:14px;line-height:1.6}
.meta{display:flex;gap:16px;font-size:13px;color:#888;margin-top:8px;flex-wrap:wrap}
.meta a{color:#ef4444;text-decoration:none}.meta a:hover{text-decoration:underline}
.tags{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}
.tag{font-size:11px;padding:2px 8px;border-radius:10px;background:#2d2d44;color:#94a3b8}
.tag.active{background:#1e3a5f;color:#60a5fa}
.opus-result{background:#1e1e3a;border:1px solid #3d3d5c;border-radius:8px;padding:12px;margin-top:10px;font-size:13px}
.opus-result .verdict{font-weight:700;margin-bottom:4px}
.opus-result .reasoning{color:#aaa;line-height:1.5}
.summary-toggle{cursor:pointer;color:#667eea;font-size:13px;margin-top:6px}
.summary-content{display:none;margin-top:8px;font-size:13px;color:#999;line-height:1.6;padding:10px;background:#0f0f23;border-radius:6px}
.summary-content.show{display:block}
.actions{display:flex;gap:8px;align-items:center;margin-top:12px}
.btn{padding:8px 16px;border-radius:8px;border:1px solid #2d2d44;background:#1a1a2e;cursor:pointer;font-size:14px;color:#e2e8f0}
.btn:hover{background:#2d2d44}
.btn.active-approve{background:#065f46;border-color:#10b981}
.btn.active-reject{background:#7f1d1d;border-color:#ef4444}
.reject-input{display:none;margin-top:8px}
.reject-input.show{display:flex;gap:8px}
.reject-input input{flex:1;padding:6px 10px;border:1px solid #2d2d44;border-radius:6px;font-size:13px;background:#0f0f23;color:#e2e8f0}
.reject-input button{padding:6px 12px;background:#ef4444;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:13px}
.saving{position:fixed;top:20px;right:20px;background:#667eea;color:#fff;padding:8px 16px;border-radius:8px;display:none;z-index:999;font-weight:600}
.cost-est{font-size:12px;color:#aaa;margin-left:8px}
</style>
</head>
<body>
<div class="saving" id="saving">저장중...</div>
<div class="container">
<div class="header">
<h1>🔍 코린이 아빠 시그널 검증</h1>
<p>파이프라인: Claude Sonnet(추출) → Opus(검증) → 사람(최종)</p>
<div class="opus-bar">
<button class="opus-btn" id="opus-btn" onclick="startOpusBatch()">🧠 Opus 전체 검토</button>
<span class="cost-est" id="cost-est"></span>
<div class="progress-bar" id="prog-bar"><div class="progress-fill" id="prog-fill"></div></div>
<span class="progress-text" id="prog-text"></span>
</div>
</div>
<div class="stats" id="stats"></div>
<div class="filters">
<div class="filter-row">
<div class="filter-group"><label class="filter-label">종목</label><select class="filter-select" id="f-asset"><option value="">전체</option></select></div>
<div class="filter-group"><label class="filter-label">시그널</label><select class="filter-select" id="f-signal">
<option value="">전체</option><option value="STRONG_BUY">강력매수</option><option value="BUY">매수</option><option value="POSITIVE">긍정</option><option value="HOLD">보유</option><option value="NEUTRAL">중립</option><option value="CONCERN">우려</option><option value="SELL">매도</option><option value="STRONG_SELL">강력매도</option>
</select></div>
<div class="filter-group"><label class="filter-label">Opus 결과</label><select class="filter-select" id="f-opus">
<option value="">전체</option><option value="approve">승인</option><option value="reject">거절</option><option value="modify">수정필요</option><option value="none">미검토</option>
</select></div>
<div class="filter-group"><label class="filter-label">사람 리뷰</label><select class="filter-select" id="f-human">
<option value="">전체</option><option value="pending">대기</option><option value="approved">승인</option><option value="rejected">거절</option>
</select></div>
<div class="filter-group"><label class="filter-label">검색</label><input class="filter-input" id="f-search" placeholder="종목/내용 검색..."></div>
</div>
</div>
<div class="signals-grid" id="grid"></div>
</div>
<script>
let SIGS=[],REVIEWS={},OPUS={};
const SL={'STRONG_BUY':'강력매수','BUY':'매수','POSITIVE':'긍정','HOLD':'보유','NEUTRAL':'중립','CONCERN':'우려','SELL':'매도','STRONG_SELL':'강력매도'};
const VL={'approve':'✅ 승인','reject':'❌ 거절','modify':'⚠️ 수정필요','error':'💥 에러'};

async function init(){
const[s,r,o]=await Promise.all([
fetch('/api/signals').then(r=>r.json()),
fetch('/api/reviews').then(r=>r.json()),
fetch('/api/opus-reviews').then(r=>r.json())
]);
SIGS=s;REVIEWS=r;OPUS=o;
initFilters();render();
const pending=SIGS.filter(s=>!OPUS[sid(s)]).length;
document.getElementById('cost-est').textContent=pending>0?`미검토 ${pending}개 · 예상비용 ~$${(pending*0.08).toFixed(1)}`:'전체 검토 완료';
}
init();

function sid(s){return s.video_id+'_'+s.asset}
function esc(s){return s?s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'):''}

function parseTs(ts){
if(!ts)return null;
const p=ts.replace(/[\\[\\] ]/g,'').split(':');
if(p.length===2)return parseInt(p[0])*60+parseInt(p[1]);
if(p.length===3)return parseInt(p[0])*3600+parseInt(p[1])*60+parseInt(p[2]);
return null;
}

function initFilters(){
const assets=[...new Set(SIGS.map(s=>s.asset))].sort();
const af=document.getElementById('f-asset');
assets.forEach(a=>{const o=document.createElement('option');o.value=a;o.textContent=a;af.appendChild(o)});
['f-asset','f-signal','f-opus','f-human'].forEach(id=>document.getElementById(id).addEventListener('change',render));
document.getElementById('f-search').addEventListener('input',render);
}

function render(){
const grid=document.getElementById('grid');
const fA=document.getElementById('f-asset').value;
const fS=document.getElementById('f-signal').value;
const fO=document.getElementById('f-opus').value;
const fH=document.getElementById('f-human').value;
const fQ=document.getElementById('f-search').value.toLowerCase();
grid.innerHTML='';
let shown=0,opusApprove=0,opusReject=0,humanApprove=0,humanReject=0;

SIGS.forEach(sig=>{
const id=sid(sig);
const rev=REVIEWS[id]||{status:'pending'};
const opus=OPUS[id];
if(opus){if(opus.verdict==='approve')opusApprove++;else if(opus.verdict==='reject')opusReject++;}
if(rev.status==='approved')humanApprove++;
if(rev.status==='rejected')humanReject++;

if(fA&&sig.asset!==fA)return;
if(fS&&sig.signal_type!==fS)return;
if(fO==='none'&&opus)return;
if(fO&&fO!=='none'&&(!opus||opus.verdict!==fO))return;
if(fH&&rev.status!==(fH==='pending'?'pending':fH==='approved'?'approved':'rejected'))return;
if(fQ&&!(sig.content||'').toLowerCase().includes(fQ)&&!(sig.asset||'').toLowerCase().includes(fQ)&&!(sig.title||'').toLowerCase().includes(fQ))return;

grid.appendChild(buildCard(sig,id,rev,opus));
shown++;
});

const pending=SIGS.length-humanApprove-humanReject;
document.getElementById('stats').innerHTML=[
{n:SIGS.length,l:'총 시그널',c:'#667eea'},
{n:pending,l:'사람 대기',c:'#f59e0b'},
{n:opusApprove,l:'Opus 승인',c:'#4ade80'},
{n:opusReject,l:'Opus 거절',c:'#f87171'},
{n:humanApprove,l:'사람 승인',c:'#10b981'},
{n:humanReject,l:'사람 거절',c:'#ef4444'},
{n:shown,l:'현재 표시',c:'#94a3b8'}
].map(s=>`<div class="stat-card"><div class="stat-number" style="color:${s.c}">${s.n}</div><div class="stat-label">${s.l}</div></div>`).join('');
}

function buildCard(sig,id,rev,opus){
const card=document.createElement('div');
card.className='signal-card'+(rev.status!=='pending'?' human-done':'');
card.dataset.signal=sig.signal_type;
const ts=parseTs(sig.timestamp);
const url=ts?`https://youtube.com/watch?v=${sig.video_id}&t=${ts}`:`https://youtube.com/watch?v=${sig.video_id}`;
const revLabel={pending:'검토대기',approved:'승인',rejected:'거절'}[rev.status];

let opusHtml='';
if(opus){
const vc=opus.verdict==='approve'?'opus-approve':opus.verdict==='reject'?'opus-reject':'opus-modify';
opusHtml=`<div class="opus-result"><div class="verdict"><span class="badge ${vc}">${VL[opus.verdict]||opus.verdict}</span>
${opus.correct_signal_type&&opus.correct_signal_type!==sig.signal_type?` → <span class="badge ${opus.correct_signal_type}">${SL[opus.correct_signal_type]||opus.correct_signal_type}</span>`:''} 
${opus.is_actionable===false?'<span class="tag">비실행적</span>':''}</div>
<div class="reasoning">${esc(opus.reasoning||'')}</div></div>`;
}

const tags=[];
if(sig.conditional)tags.push('조건부');
if(sig.skin_in_game)tags.push('본인투자');
if(sig.hedged)tags.push('헷지');
if(sig.timeframe)tags.push(sig.timeframe);

card.innerHTML=`
<div class="signal-header">
<div>
<span class="signal-asset">${esc(sig.asset)}</span>
<span class="badge ${sig.signal_type}">${SL[sig.signal_type]||sig.signal_type}</span>
<span class="badge conf-${sig.confidence||''}">${sig.confidence||''}</span>
<span class="badge ${rev.status}">${revLabel}</span>
</div>
<div style="font-size:12px;color:#666">⏱ ${esc(sig.timestamp||'')}</div>
</div>
<div class="quote">"${esc(sig.content)}"</div>
${sig.context?`<div style="margin-top:6px;font-size:13px;color:#888">💡 ${esc(sig.context)}</div>`:''}
<div class="meta">
<span>🎬 <a href="${esc(url)}" target="_blank">${esc((sig.title||sig.video_id).substring(0,60))} ▶️</a></span>
<span>🎙️ ${esc(sig.channel||'코린이 아빠')}</span>
</div>
${tags.length?`<div class="tags">${tags.map(t=>`<span class="tag active">${t}</span>`).join('')}</div>`:''}
${sig.video_summary?`<div class="summary-toggle" onclick="this.nextElementSibling.classList.toggle('show')">📋 영상요약 보기/접기</div><div class="summary-content">${esc(sig.video_summary)}</div>`:''}
${opusHtml}
<div class="actions">
<button class="btn${rev.status==='approved'?' active-approve':''}" onclick="doReview('${id}','approved',this)">✅ 승인</button>
<button class="btn${rev.status==='rejected'?' active-reject':''}" onclick="showReject(this)">❌ 거절</button>
${rev.status==='rejected'&&rev.reason?`<span style="color:#fca5a5;font-size:13px">⛔ ${esc(rev.reason)}</span>`:''}
</div>
<div class="reject-input">
<input placeholder="거절 사유...">
<button onclick="submitReject('${id}',this)">거절</button>
</div>`;
return card;
}

function showReject(btn){
const ri=btn.closest('.signal-card').querySelector('.reject-input');
ri.classList.toggle('show');
if(ri.classList.contains('show'))ri.querySelector('input').focus();
}

async function doReview(id,status,btn){
document.getElementById('saving').style.display='block';
await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,status})});
REVIEWS[id]={status,time:new Date().toISOString()};
document.getElementById('saving').style.display='none';
render();
}

async function submitReject(id,btn){
const input=btn.previousElementSibling;
const reason=input.value;
document.getElementById('saving').style.display='block';
await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,status:'rejected',reason})});
REVIEWS[id]={status:'rejected',reason,time:new Date().toISOString()};
document.getElementById('saving').style.display='none';
render();
}

async function startOpusBatch(){
const btn=document.getElementById('opus-btn');
const bar=document.getElementById('prog-bar');
const fill=document.getElementById('prog-fill');
const txt=document.getElementById('prog-text');
if(!confirm('Opus 전체 검토를 시작할까요? (미검토 시그널만 처리)'))return;
btn.disabled=true;bar.style.display='block';txt.style.display='inline';
await fetch('/api/opus-review-all',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});

const poll=setInterval(async()=>{
const p=await fetch('/api/opus-progress').then(r=>r.json());
const pct=p.total>0?Math.round(p.done/p.total*100):0;
fill.style.width=pct+'%';
txt.textContent=`${p.done}/${p.total} (${pct}%)${p.errors?' ⚠️'+p.errors+'에러':''}`;
if(!p.running){
clearInterval(poll);
btn.disabled=false;
txt.textContent='완료!';
const o=await fetch('/api/opus-reviews').then(r=>r.json());
OPUS=o;render();
document.getElementById('cost-est').textContent='전체 검토 완료';
}
},2000);
}
</script>
</body>
</html>'''

if __name__ == '__main__':
    port = 8900
    print(f'Signal Review v4 server: http://localhost:{port}', flush=True)
    HTTPServer(('0.0.0.0', port), ReviewHandler).serve_forever()
