import https from 'https';
import fs from 'fs';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const ANTHROPIC_KEY = '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';

const V11_PROMPT = fs.readFileSync('C:\\Users\\Mario\\work\\invest-sns\\prompts\\pipeline_v11.md', 'utf-8');
const sleep = ms => new Promise(r => setTimeout(r, ms));

function fetchJSON(method, url, headers, body) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const opts = { hostname: u.hostname, path: u.pathname + u.search, method, headers: { ...headers } };
    const req = (u.protocol === 'https:' ? https : require('http')).request(opts, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(d || '[]') }); }
        catch(e) { resolve({ status: res.statusCode, data: d }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(typeof body === 'string' ? body : JSON.stringify(body));
    req.end();
  });
}

const sbHeaders = { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}`, 'Content-Type': 'application/json' };

async function callClaude(userMsg, retries = 3) {
  for (let i = 0; i < retries; i++) {
    const body = JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 4096, system: V11_PROMPT, messages: [{ role: 'user', content: userMsg }] });
    const res = await new Promise((resolve, reject) => {
      const req = https.request({ hostname: 'api.anthropic.com', path: '/v1/messages', method: 'POST', headers: { 'Content-Type': 'application/json', 'x-api-key': ANTHROPIC_KEY, 'anthropic-version': '2023-06-01' } }, res => {
        let d = '';
        res.on('data', c => d += c);
        res.on('end', () => { try { resolve({ status: res.statusCode, data: JSON.parse(d) }); } catch(e) { reject(new Error(d.substring(0,300))); } });
      });
      req.on('error', reject);
      req.write(body);
      req.end();
    });
    if (res.status === 429) { console.log(`  429 hit, waiting 60s... (${i+1}/${retries})`); await sleep(60000); continue; }
    if (res.status !== 200) { console.log(`  API error ${res.status}, retry...`); await sleep(5000); continue; }
    return res.data;
  }
  return null;
}

async function main() {
  console.log('=== V11 Reclassify Remaining + DB UPDATE ===\n');

  // 1. Load previous 50 results
  let prevResults = [];
  const prevPath = 'C:\\Users\\Mario\\work\\data\\research\\v11_reclassify_data.json';
  if (fs.existsSync(prevPath)) {
    prevResults = JSON.parse(fs.readFileSync(prevPath, 'utf-8'));
    console.log(`Loaded ${prevResults.length} previous results`);
  }
  const processedVideoIds = new Set(prevResults.map(r => r.video_id));

  // 2. Get all signals
  const sigRes = await fetchJSON('GET', `${SUPABASE_URL}/rest/v1/influencer_signals?select=id,video_id,stock,signal,key_quote,confidence&limit=1000`, sbHeaders);
  const allSignals = sigRes.data;
  console.log(`Total signals: ${allSignals.length}`);

  // 3. Group by video_id
  const videoGroups = {};
  allSignals.forEach(s => {
    if (!videoGroups[s.video_id]) videoGroups[s.video_id] = [];
    videoGroups[s.video_id].push(s);
  });

  // 4. Filter: not already processed, has enough text
  const remaining = Object.entries(videoGroups)
    .filter(([vid]) => !processedVideoIds.has(vid))
    .filter(([, sigs]) => sigs.map(s => s.key_quote || '').join(' ').length >= 200)
    .map(([vid, sigs]) => ({ video_id: vid, signals: sigs, text: sigs.map(s => s.key_quote || '').join('\n\n') }));

  console.log(`Remaining to process: ${remaining.length}\n`);

  // 5. Process remaining
  const newResults = [];
  let totalInput = 0, totalOutput = 0;

  for (let i = 0; i < remaining.length; i++) {
    const v = remaining[i];
    const truncText = v.text.length > 8000 ? v.text.substring(0, 8000) + '\n...(이하 생략)' : v.text;
    console.log(`[${i+1}/${remaining.length}] video ${v.video_id.substring(0,8)}... (${v.signals.length} signals, ${v.text.length} chars)`);

    const resp = await callClaude(`다음 영상의 주요 발언들을 분석해서 투자 시그널을 추출해주세요:\n\n${truncText}`);
    if (!resp) { console.log('  FAILED'); newResults.push({ video_id: v.video_id, old_signals: v.signals.map(s=>({stock:s.stock,signal:s.signal})), new_signals: [], error: true }); continue; }

    if (resp.usage) { totalInput += resp.usage.input_tokens; totalOutput += resp.usage.output_tokens; }

    let parsed = [];
    try {
      const txt = resp.content?.[0]?.text || '';
      const m = txt.match(/\{[\s\S]*\}/);
      if (m) { const j = JSON.parse(m[0]); parsed = j.signals || []; }
    } catch(e) { console.log('  Parse error'); }

    const v11Signals = parsed.map(s => ({ stock: s.stock, signal_type: s.signal_type }));
    console.log(`  Old: ${v.signals.length} signals | V11: ${v11Signals.length} signals`);

    newResults.push({
      video_id: v.video_id,
      old_signals: v.signals.map(s => ({ id: s.id, stock: s.stock, signal: s.signal })),
      new_signals: v11Signals
    });

    await sleep(3000);
    if ((i+1) % 20 === 0) { console.log('  Extra 5s pause...'); await sleep(5000); }
    if ((i+1) % 50 === 0) { console.log(`\n=== CHECKPOINT ${i+1}/${remaining.length} ===\n`); }
  }

  // 6. Combine with previous results
  const allResults = [...prevResults, ...newResults];
  console.log(`\nTotal processed: ${allResults.length} videos`);

  // 7. Calculate before/after distribution
  const beforeDist = { '매수': 0, '긍정': 0, '중립': 0, '부정': 0, '매도': 0 };
  const afterDist = { '매수': 0, '긍정': 0, '중립': 0, '부정': 0, '매도': 0 };
  let buyToPositive = 0;
  const updateList = []; // { signal_id, new_signal_type }

  for (const r of allResults) {
    // Count old
    const oldSigs = r.old_signals || [];
    oldSigs.forEach(s => { const t = s.signal_type || s.signal; if (beforeDist[t] !== undefined) beforeDist[t]++; });

    // Count new
    const newSigs = r.new_signals || [];
    newSigs.forEach(s => { const t = s.signal_type; if (afterDist[t] !== undefined) afterDist[t]++; });

    // Match old→new by stock for UPDATE
    for (const oldSig of oldSigs) {
      const oldStock = oldSig.stock;
      const oldType = oldSig.signal_type || oldSig.signal;
      const match = newSigs.find(n => n.stock === oldStock);
      if (match && match.signal_type !== oldType && oldSig.id) {
        updateList.push({ id: oldSig.id, old_signal: oldType, new_signal: match.signal_type, stock: oldStock });
        if (oldType === '매수' && match.signal_type === '긍정') buyToPositive++;
      }
    }
  }

  const beforeTotal = Object.values(beforeDist).reduce((a,b) => a+b, 0);
  const afterTotal = Object.values(afterDist).reduce((a,b) => a+b, 0);

  console.log('\n=== BEFORE/AFTER DISTRIBUTION ===');
  console.log('Before:', JSON.stringify(beforeDist), 'Total:', beforeTotal);
  console.log('After:', JSON.stringify(afterDist), 'Total:', afterTotal);
  console.log('Buy→Positive:', buyToPositive);
  console.log('Updates to apply:', updateList.length);

  // 8. DB UPDATE
  console.log('\n=== DB UPDATE ===');
  let updateSuccess = 0, updateFail = 0;

  for (const upd of updateList) {
    const res = await fetchJSON('PATCH',
      `${SUPABASE_URL}/rest/v1/influencer_signals?id=eq.${upd.id}`,
      { ...sbHeaders, Prefer: 'return=minimal' },
      JSON.stringify({ signal: upd.new_signal, pipeline_version: 'V11' })
    );
    if (res.status >= 200 && res.status < 300) { updateSuccess++; }
    else { updateFail++; console.log(`  FAIL: ${upd.id} → ${res.status}`); }
    if (updateSuccess % 50 === 0 && updateSuccess > 0) console.log(`  Updated ${updateSuccess}...`);
  }

  console.log(`\nDB UPDATE complete: ${updateSuccess} success, ${updateFail} fail`);

  // 9. Verify final distribution
  const verifyRes = await fetchJSON('GET', `${SUPABASE_URL}/rest/v1/influencer_signals?select=signal&limit=1000`, sbHeaders);
  const finalDist = { '매수': 0, '긍정': 0, '중립': 0, '부정': 0, '매도': 0 };
  verifyRes.data.forEach(s => { if (finalDist[s.signal] !== undefined) finalDist[s.signal]++; });
  const finalTotal = Object.values(finalDist).reduce((a,b) => a+b, 0);
  console.log('\nFINAL DB Distribution:', JSON.stringify(finalDist), 'Total:', finalTotal);

  // 10. Save results
  const cost = ((totalInput * 3 / 1000000) + (totalOutput * 15 / 1000000)).toFixed(4);
  console.log(`\nCost: $${cost} (${totalInput} in / ${totalOutput} out)`);

  // Save combined data
  fs.writeFileSync(prevPath, JSON.stringify(allResults, null, 2), 'utf-8');
  console.log('Saved combined results to v11_reclassify_data.json');

  // Save summary
  const summary = {
    timestamp: new Date().toISOString(),
    total_processed: allResults.length,
    remaining_processed: newResults.length,
    cost_usd: cost,
    before: beforeDist, before_total: beforeTotal,
    after: afterDist, after_total: afterTotal,
    buy_to_positive: buyToPositive,
    db_updates: { success: updateSuccess, fail: updateFail },
    final_db: finalDist, final_total: finalTotal
  };
  fs.writeFileSync('C:\\Users\\Mario\\work\\data\\research\\v11_reclassify_summary.json', JSON.stringify(summary, null, 2), 'utf-8');
  console.log('\n=== ALL DONE ===');
  console.log(JSON.stringify(summary, null, 2));
}

main().catch(e => { console.error('FATAL:', e); process.exit(1); });
