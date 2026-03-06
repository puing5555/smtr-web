import https from 'https';
import fs from 'fs';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const ANTHROPIC_KEY = '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';

const V11_PROMPT = fs.readFileSync('C:\\Users\\Mario\\work\\invest-sns\\prompts\\pipeline_v11.md', 'utf-8');
const sleep = ms => new Promise(r => setTimeout(r, ms));

// Log file
const logFile = 'C:\\Users\\Mario\\work\\data\\research\\v11_final_log.txt';
function log(msg) {
  const timestamp = new Date().toISOString();
  const logMsg = `[${timestamp}] ${msg}\n`;
  console.log(msg);
  fs.appendFileSync(logFile, logMsg, 'utf-8');
}

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
    if (res.status === 429) { log(`  429 hit, waiting 60s... (${i+1}/${retries})`); await sleep(60000); continue; }
    if (res.status !== 200) { log(`  API error ${res.status}, retry...`); await sleep(5000); continue; }
    return res.data;
  }
  return null;
}

// Save intermediate results
function saveProgress(results, filename) {
  const path = `C:\\Users\\Mario\\work\\data\\research\\${filename}`;
  fs.writeFileSync(path, JSON.stringify(results, null, 2), 'utf-8');
  log(`Progress saved: ${results.length} results → ${filename}`);
}

async function main() {
  log('=== V11 FINAL RECLASSIFY + DB UPDATE ===');

  // Clear previous log
  if (fs.existsSync(logFile)) fs.unlinkSync(logFile);

  // 1. Get all signals from DB
  log('Fetching all signals from DB...');
  const sigRes = await fetchJSON('GET', `${SUPABASE_URL}/rest/v1/influencer_signals?select=id,video_id,stock,signal,key_quote,confidence&limit=1000`, sbHeaders);
  const allSignals = sigRes.data;
  log(`Total signals in DB: ${allSignals.length}`);

  // 2. Group by video_id
  log('Grouping signals by video_id...');
  const videoGroups = {};
  allSignals.forEach(s => {
    if (!videoGroups[s.video_id]) videoGroups[s.video_id] = [];
    videoGroups[s.video_id].push(s);
  });

  // 3. Filter: only those with 200+ chars combined key_quote
  const eligible = Object.entries(videoGroups)
    .filter(([, sigs]) => {
      const combinedText = sigs.map(s => s.key_quote || '').join(' ');
      return combinedText.length >= 200;
    })
    .map(([vid, sigs]) => ({ 
      video_id: vid, 
      signals: sigs, 
      text: sigs.map(s => s.key_quote || '').join('\n\n'),
      textLength: sigs.map(s => s.key_quote || '').join(' ').length
    }));

  log(`Videos with 200+ chars: ${eligible.length}`);

  // 4. Process each video
  const results = [];
  let totalInput = 0, totalOutput = 0;

  for (let i = 0; i < eligible.length; i++) {
    const v = eligible[i];
    const truncText = v.text.length > 8000 ? v.text.substring(0, 8000) + '\n...(이하 생략)' : v.text;
    log(`[${i+1}/${eligible.length}] Processing video ${v.video_id.substring(0,8)}... (${v.signals.length} signals, ${v.textLength} chars)`);

    const resp = await callClaude(`다음 영상의 주요 발언들을 분석해서 투자 시그널을 추출해주세요:\n\n${truncText}`);
    
    if (!resp) {
      log(`  FAILED: API call returned null`);
      results.push({ 
        video_id: v.video_id, 
        old_signals: v.signals.map(s=>({id: s.id, stock:s.stock,signal:s.signal})), 
        new_signals: [], 
        error: true 
      });
      continue;
    }

    if (resp.usage) { 
      totalInput += resp.usage.input_tokens; 
      totalOutput += resp.usage.output_tokens; 
      log(`  Tokens: ${resp.usage.input_tokens} in / ${resp.usage.output_tokens} out`);
    }

    let parsed = [];
    try {
      const txt = resp.content?.[0]?.text || '';
      const m = txt.match(/\{[\s\S]*\}/);
      if (m) { 
        const j = JSON.parse(m[0]); 
        parsed = j.signals || []; 
      }
    } catch(e) { 
      log(`  Parse error: ${e.message}`); 
    }

    const v11Signals = parsed.map(s => ({ stock: s.stock, signal_type: s.signal_type }));
    log(`  Results: ${v.signals.length} old signals → ${v11Signals.length} new signals`);

    results.push({
      video_id: v.video_id,
      old_signals: v.signals.map(s => ({ id: s.id, stock: s.stock, signal: s.signal })),
      new_signals: v11Signals,
      processed_at: new Date().toISOString()
    });

    // Rate limiting
    await sleep(3000);
    if ((i+1) % 20 === 0) { 
      log('  Extra 5s pause after 20 requests...'); 
      await sleep(5000); 
    }

    // Save progress every 50
    if ((i+1) % 50 === 0) {
      log(`\n=== CHECKPOINT ${i+1}/${eligible.length} ===`);
      saveProgress(results, `v11_progress_${i+1}.json`);
      log('');
    }
  }

  log(`\nProcessing complete! Analyzed ${results.length} videos`);

  // 5. Calculate distributions and prepare updates
  log('\nCalculating before/after distributions...');
  const beforeDist = { '매수': 0, '긍정': 0, '중립': 0, '부정': 0, '매도': 0 };
  const afterDist = { '매수': 0, '긍정': 0, '중립': 0, '부정': 0, '매도': 0 };
  const updateList = [];

  for (const r of results) {
    // Count old signals
    const oldSigs = r.old_signals || [];
    oldSigs.forEach(s => { 
      const t = s.signal; 
      if (beforeDist[t] !== undefined) beforeDist[t]++; 
    });

    // Count new signals
    const newSigs = r.new_signals || [];
    newSigs.forEach(s => { 
      const t = s.signal_type; 
      if (afterDist[t] !== undefined) afterDist[t]++; 
    });

    // Match old→new by stock for UPDATE
    for (const oldSig of oldSigs) {
      const oldStock = oldSig.stock;
      const oldType = oldSig.signal;
      const match = newSigs.find(n => n.stock === oldStock);
      
      if (match && match.signal_type !== oldType && oldSig.id) {
        updateList.push({ 
          id: oldSig.id, 
          old_signal: oldType, 
          new_signal: match.signal_type, 
          stock: oldStock,
          video_id: r.video_id
        });
      }
    }
  }

  const beforeTotal = Object.values(beforeDist).reduce((a,b) => a+b, 0);
  const afterTotal = Object.values(afterDist).reduce((a,b) => a+b, 0);

  log('\n=== DISTRIBUTION ANALYSIS ===');
  log(`Before: ${JSON.stringify(beforeDist)} (Total: ${beforeTotal})`);
  log(`After:  ${JSON.stringify(afterDist)} (Total: ${afterTotal})`);
  log(`Updates needed: ${updateList.length}`);

  const buyToPositive = updateList.filter(u => u.old_signal === '매수' && u.new_signal === '긍정').length;
  log(`Buy→Positive changes: ${buyToPositive}`);

  // 6. Apply DB updates
  log('\n=== APPLYING DB UPDATES ===');
  let updateSuccess = 0, updateFail = 0;

  for (let i = 0; i < updateList.length; i++) {
    const upd = updateList[i];
    log(`[${i+1}/${updateList.length}] Updating signal ${upd.id}: ${upd.old_signal} → ${upd.new_signal} (${upd.stock})`);
    
    const res = await fetchJSON('PATCH',
      `${SUPABASE_URL}/rest/v1/influencer_signals?id=eq.${upd.id}`,
      { ...sbHeaders, Prefer: 'return=minimal' },
      JSON.stringify({ signal: upd.new_signal, pipeline_version: 'V11' })
    );
    
    if (res.status >= 200 && res.status < 300) { 
      updateSuccess++; 
    } else { 
      updateFail++; 
      log(`  FAILED: status ${res.status}`); 
    }

    if (updateSuccess % 25 === 0 && updateSuccess > 0) {
      log(`  Progress: ${updateSuccess} updates completed...`);
    }
  }

  log(`\nDB UPDATE COMPLETE: ${updateSuccess} success, ${updateFail} failed`);

  // 7. Verify final distribution
  log('\nVerifying final DB distribution...');
  const verifyRes = await fetchJSON('GET', `${SUPABASE_URL}/rest/v1/influencer_signals?select=signal&limit=1000`, sbHeaders);
  const finalDist = { '매수': 0, '긍정': 0, '중립': 0, '부정': 0, '매도': 0 };
  verifyRes.data.forEach(s => { 
    if (finalDist[s.signal] !== undefined) finalDist[s.signal]++; 
  });
  const finalTotal = Object.values(finalDist).reduce((a,b) => a+b, 0);
  log(`Final DB: ${JSON.stringify(finalDist)} (Total: ${finalTotal})`);

  // 8. Calculate cost
  const cost = ((totalInput * 3 / 1000000) + (totalOutput * 15 / 1000000)).toFixed(4);
  log(`\nCost: $${cost} (${totalInput} input tokens / ${totalOutput} output tokens)`);

  // 9. Save final results
  const finalResults = {
    timestamp: new Date().toISOString(),
    total_videos: results.length,
    eligible_videos: eligible.length,
    cost_usd: parseFloat(cost),
    token_usage: { input: totalInput, output: totalOutput },
    before: { distribution: beforeDist, total: beforeTotal },
    after: { distribution: afterDist, total: afterTotal },
    buy_to_positive_changes: buyToPositive,
    db_updates: { success: updateSuccess, fail: updateFail, total: updateList.length },
    final_db: { distribution: finalDist, total: finalTotal },
    detailed_results: results
  };

  const resultsPath = 'C:\\Users\\Mario\\work\\data\\research\\v11_final_results.json';
  fs.writeFileSync(resultsPath, JSON.stringify(finalResults, null, 2), 'utf-8');
  log(`Final results saved to: ${resultsPath}`);

  // Summary for reporting
  const summary = {
    completed_at: new Date().toISOString(),
    videos_processed: results.length,
    cost: `$${cost}`,
    before_distribution: beforeDist,
    after_distribution: afterDist,
    final_db_distribution: finalDist,
    db_updates_applied: updateSuccess,
    buy_to_positive_changes: buyToPositive
  };

  log('\n=== FINAL SUMMARY ===');
  log(JSON.stringify(summary, null, 2));
  log('\n=== ALL DONE ===');

  return summary;
}

main().catch(e => { 
  log(`FATAL ERROR: ${e.message}`);
  log(e.stack);
  process.exit(1); 
});