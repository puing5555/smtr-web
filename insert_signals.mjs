import fs from 'fs';

const BASE = 'https://arypzhotxflimroprmdk.supabase.co/rest/v1';
const K = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const H = { 'apikey': K, 'Authorization': `Bearer ${K}`, 'Content-Type': 'application/json' };

const CHANNEL_ID = 'd153b75b-1843-4a99-b49f-c31081a8f566';
const SPEAKER_ID = 'b07d8758-493a-4a51-9bc5-7ef75f0be67c';

async function get(table, params) {
  const r = await fetch(`${BASE}/${table}${params}`, { headers: H });
  return r.json();
}

async function post(table, body, headers = {}) {
  const r = await fetch(`${BASE}/${table}`, {
    method: 'POST', headers: { ...H, 'Prefer': 'return=minimal', ...headers }, body: JSON.stringify(body)
  });
  if (!r.ok) { const t = await r.text(); throw new Error(`${r.status}: ${t}`); }
  return r;
}

// Step 1: Get all existing videos for this channel
console.log('Fetching existing videos...');
const existingVids = await get('influencer_videos', `?channel_id=eq.${CHANNEL_ID}&select=id,video_id&limit=1000`);
const vidMap = new Map(existingVids.map(v => [v.video_id, v.id]));
console.log(`Existing videos: ${vidMap.size}`);

// Step 2: Parse JSONL
const lines = fs.readFileSync('C:\\Users\\Mario\\work\\hs_analysis_cleaned.jsonl', 'utf8').trim().split('\n');
const parsed = lines.map(l => JSON.parse(l));

// Step 3: Create missing videos
const missingVids = parsed.filter(p => !vidMap.has(p.vid_id));
console.log(`Missing videos to create: ${missingVids.length}`);

for (let i = 0; i < missingVids.length; i += 50) {
  const batch = missingVids.slice(i, i + 50).map(p => ({
    channel_id: CHANNEL_ID,
    video_id: p.vid_id,
    title: p.title || null,
    has_subtitle: false
  }));
  try {
    await post('influencer_videos', batch, { 'Prefer': 'return=representation' });
  } catch (e) {
    // Try one by one for conflicts
    for (const v of batch) {
      try { await post('influencer_videos', v); } catch (e2) { /* skip existing */ }
    }
  }
}

// Re-fetch all videos
const allVids = await get('influencer_videos', `?channel_id=eq.${CHANNEL_ID}&select=id,video_id&limit=1000`);
const vm = new Map(allVids.map(v => [v.video_id, v.id]));
console.log(`Total videos now: ${vm.size}`);

// Step 4: Build signals
const allSignals = [];
for (const obj of parsed) {
  if (!obj.signals) continue;
  const videoUuid = vm.get(obj.vid_id);
  if (!videoUuid) { console.error(`No UUID for ${obj.vid_id}`); continue; }
  for (const s of obj.signals) {
    const ticker = s.ticker || '';
    const conf = s.confidence || 5;
    allSignals.push({
      video_id: videoUuid,
      speaker_id: SPEAKER_ID,
      stock: s.stock || null,
      ticker: ticker || null,
      market: /^\d{6}$/.test(ticker) ? 'KR' : (ticker ? 'US' : null),
      signal: s.signal_type || null,
      confidence: conf <= 3 ? 'low' : conf <= 5 ? 'medium' : conf <= 7 ? 'high' : 'very_high',
      key_quote: s.key_quote || null,
      reasoning: s.reasoning || null,
      mention_type: '논거',
      timestamp: s.timestamp || null,
      review_status: 'pending'
    });
  }
}
console.log(`Total signals to insert: ${allSignals.length}`);

// Step 5: Batch insert
const BATCH = 50;
let success = 0, failed = 0;
const failures = [];

for (let i = 0; i < allSignals.length; i += BATCH) {
  const batch = allSignals.slice(i, i + BATCH);
  let ok = false;
  for (let retry = 0; retry < 3; retry++) {
    try {
      await post('influencer_signals', batch);
      ok = true;
      break;
    } catch (e) {
      console.error(`Batch ${i} retry ${retry}: ${e.message.slice(0, 200)}`);
      if (retry < 2) await new Promise(r => setTimeout(r, 2000));
    }
  }
  if (ok) success += batch.length;
  else { failed += batch.length; failures.push({ from: i, count: batch.length }); }
  
  const done = success + failed;
  if (done % 100 < BATCH || i + BATCH >= allSignals.length) {
    console.log(`Progress: ${done}/${allSignals.length} (${(done/allSignals.length*100).toFixed(1)}%)`);
  }
}

console.log(`\n=== COMPLETE ===`);
console.log(`channel_id: ${CHANNEL_ID}`);
console.log(`speaker_id: ${SPEAKER_ID}`);
console.log(`Success: ${success} / Failed: ${failed}`);
if (failures.length) console.log('Failures:', JSON.stringify(failures));
