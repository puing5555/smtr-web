import fs from 'fs';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const ANTHROPIC_KEY = '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';
const MODEL = 'claude-sonnet-4-20250514';

const v11Prompt = fs.readFileSync('C:\\Users\\Mario\\work\\invest-sns\\prompts\\pipeline_v11.md', 'utf-8');
const existingResults = JSON.parse(fs.readFileSync('C:\\Users\\Mario\\work\\data\\research\\v11_reclassify_data.json', 'utf-8'));
const processedVideoIds = new Set(existingResults.map(r => r.video_id));

const delay = (ms) => new Promise(r => setTimeout(r, ms));
let totalCost = 0;

// Supabase REST fetch
async function supaFetch(table, query = '') {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?${query}`, {
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json'
    }
  });
  if (!res.ok) throw new Error(`Supabase GET ${table}: ${res.status} ${await res.text()}`);
  return res.json();
}

// Supabase PATCH
async function supaPatch(table, query, body) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?${query}`, {
    method: 'PATCH',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=minimal'
    },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(`Supabase PATCH: ${res.status} ${await res.text()}`);
  return res;
}

// Anthropic API
async function callClaude(content, retries = 3) {
  const truncated = content.length > 8000 ? content.substring(0, 8000) + '...' : content;
  for (let i = 0; i < retries; i++) {
    try {
      const fetchPromise = fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': ANTHROPIC_KEY,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: MODEL,
          max_tokens: 4000,
          system: v11Prompt,
          messages: [{ role: 'user', content: `다음 영상 자막을 분석해서 투자 시그널을 추출해주세요:\n\n${truncated}` }]
        })
      });
      const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout 90s')), 90000));
      const res = await Promise.race([fetchPromise, timeoutPromise]);
      if (res.status === 429) {
        console.log(`⚠️ 429 rate limit, waiting 60s... (${i+1}/${retries})`);
        await delay(60000);
        continue;
      }
      if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
      const data = await res.json();
      const inputTok = data.usage?.input_tokens || Math.ceil(truncated.length / 4);
      const outputTok = data.usage?.output_tokens || Math.ceil(data.content[0].text.length / 4);
      const cost = (inputTok * 3 + outputTok * 15) / 1_000_000;
      totalCost += cost;
      return { content: data.content[0].text, cost };
    } catch (e) {
      console.error(`API attempt ${i+1} failed:`, e.message);
      if (i === retries - 1) throw e;
      await delay(5000);
    }
  }
}

function parseSignals(text) {
  try {
    const m = text.match(/\{[\s\S]*\}/);
    if (!m) return [];
    return JSON.parse(m[0]).signals || [];
  } catch { return []; }
}

const signalMap = {
  'STRONG_BUY': '매수', 'BUY': '긍정', 'HOLD': '중립', 'SELL': '부정', 'STRONG_SELL': '매도',
  'CAUTION': '부정', 'NEGATIVE': '부정', 'POSITIVE': '긍정', 'NEUTRAL': '중립',
  '매수': '매수', '긍정': '긍정', '중립': '중립', '부정': '부정', '매도': '매도', '경계': '부정'
};
const norm = (s) => signalMap[s] || s;

async function main() {
  console.log('🚀 Phase 1: 나머지 108개 V11 재분류');
  console.log(`이미 처리된 영상: ${processedVideoIds.size}개`);

  // 1. 모든 시그널 가져오기 (key_quote 있는 것)
  const allSignals = await supaFetch('influencer_signals', 'select=*&key_quote=not.is.null&key_quote=neq.&order=created_at.desc&limit=2000');
  console.log(`전체 시그널 (key_quote 있음): ${allSignals.length}개`);

  // 2. video_id별 그룹화
  const videoGroups = {};
  allSignals.forEach(s => {
    if (!videoGroups[s.video_id]) videoGroups[s.video_id] = { video_id: s.video_id, signals: [], combined_quotes: '' };
    videoGroups[s.video_id].signals.push({ ...s, signal_type: norm(s.signal) });
    if (s.key_quote) videoGroups[s.video_id].combined_quotes += s.key_quote + ' ';
  });

  // 3. 미처리 + 200자 이상 필터
  const remaining = Object.values(videoGroups)
    .filter(v => !processedVideoIds.has(v.video_id) && v.combined_quotes.length >= 200);
  console.log(`미처리 영상 (200자+): ${remaining.length}개`);

  const newResults = [];
  for (let i = 0; i < remaining.length; i++) {
    const v = remaining[i];
    const label = v.combined_quotes.substring(0, 80) + '...';
    console.log(`[${i+1}/${remaining.length}] ${label}`);

    try {
      console.log(`  content_len=${v.combined_quotes.length}, calling API...`);
      const api = await callClaude(v.combined_quotes);
      console.log(`  API response received, cost=$${api.cost.toFixed(4)}`);
      const sigs = parseSignals(api.content).map(s => ({ ...s, signal_type: norm(s.signal_type) }));
      newResults.push({
        video_id: v.video_id,
        title: label,
        old_signals: v.signals,
        new_signals: sigs,
        old_signal_count: v.signals.length,
        new_signal_count: sigs.length,
        api_cost: api.cost,
        content_length: v.combined_quotes.length
      });
    } catch (e) {
      console.error(`❌ ${v.video_id}:`, e.message);
      newResults.push({
        video_id: v.video_id, title: label, error: e.message,
        old_signals: v.signals, new_signals: [],
        old_signal_count: v.signals.length, new_signal_count: 0,
        api_cost: 0, content_length: v.combined_quotes.length
      });
    }

    // 매번 중간저장
    const merged = [...existingResults, ...newResults];
    fs.writeFileSync('C:\\Users\\Mario\\work\\data\\research\\v11_reclassify_data.json', JSON.stringify(merged, null, 2));

    // 레이트리밋 방지
    await delay(3000);
    if ((i + 1) % 20 === 0) {
      console.log(`😴 20개 처리 완료, 5초 휴식... (누적비용: $${totalCost.toFixed(4)})`);
      await delay(5000);
    }
  }

  // 전체 결과 병합 & 저장
  const allResults = [...existingResults, ...newResults];
  fs.writeFileSync('C:\\Users\\Mario\\work\\data\\research\\v11_reclassify_data.json', JSON.stringify(allResults, null, 2));
  console.log(`\n✅ Phase 1 완료: 총 ${allResults.length}개 영상 (기존${existingResults.length} + 신규${newResults.length})`);
  console.log(`💰 Phase 1 비용: $${totalCost.toFixed(4)}`);

  // Phase 2: DB UPDATE
  console.log('\n🚀 Phase 2: DB UPDATE');

  // 전체 시그널 가져오기 (UPDATE 전 분포 기록)
  const allDbSignals = await supaFetch('influencer_signals', 'select=id,video_id,stock,signal,pipeline_version&limit=2000');
  console.log(`DB 전체 시그널: ${allDbSignals.length}개`);

  // Before 분포
  const beforeDist = { '매수': 0, '긍정': 0, '중립': 0, '부정': 0, '매도': 0 };
  allDbSignals.forEach(s => { if (beforeDist[s.signal] !== undefined) beforeDist[s.signal]++; });
  console.log('Before:', beforeDist);

  let updateCount = 0;
  let skipCount = 0;

  for (const result of allResults) {
    if (result.error || result.new_signals.length === 0) continue;

    for (const oldSig of result.old_signals) {
      const oldStock = oldSig.stock;
      const oldSignalType = norm(oldSig.signal);

      // V11에서 매칭되는 종목 찾기
      const match = result.new_signals.find(ns => ns.stock === oldStock);
      if (!match) { skipCount++; continue; }

      const newSignalType = norm(match.signal_type);
      if (oldSignalType === newSignalType) { skipCount++; continue; } // 변경 없으면 스킵

      // UPDATE
      try {
        await supaPatch('influencer_signals', `id=eq.${oldSig.id}`, {
          signal: newSignalType,
          pipeline_version: 'V11'
        });
        updateCount++;
        if (updateCount % 20 === 0) {
          console.log(`  Updated ${updateCount}건...`);
          await delay(1000);
        }
      } catch (e) {
        console.error(`PATCH failed for ${oldSig.id}:`, e.message);
      }
    }
  }

  // 처리된 영상의 변경 없는 시그널도 pipeline_version만 V11로
  console.log('pipeline_version V11 일괄 업데이트 중...');
  const processedVids = allResults.filter(r => !r.error).map(r => r.video_id);
  // 배치로 처리
  for (let i = 0; i < processedVids.length; i += 20) {
    const batch = processedVids.slice(i, i + 20);
    const vidFilter = batch.map(v => `"${v}"`).join(',');
    try {
      await supaPatch('influencer_signals', `video_id=in.(${vidFilter})`, { pipeline_version: 'V11' });
    } catch (e) {
      console.error(`Batch pipeline_version update failed:`, e.message);
    }
    await delay(500);
  }

  console.log(`\n✅ Phase 2 완료: ${updateCount}건 signal 변경, ${skipCount}건 스킵`);

  // Phase 3: After 분포 가져오기
  const afterSignals = await supaFetch('influencer_signals', 'select=id,signal,pipeline_version&limit=2000');
  const afterDist = { '매수': 0, '긍정': 0, '중립': 0, '부정': 0, '매도': 0 };
  afterSignals.forEach(s => { if (afterDist[s.signal] !== undefined) afterDist[s.signal]++; });
  const v11Count = afterSignals.filter(s => s.pipeline_version === 'V11').length;

  console.log('After:', afterDist);
  console.log(`V11 적용: ${v11Count}건`);

  // 리포트 생성
  const report = `# V11 재분류 + DB UPDATE 완료 리포트

## 실행 정보
- 실행: ${new Date().toLocaleString('ko-KR', {timeZone:'Asia/Bangkok'})}
- 처리 영상: ${allResults.length}개 (기존 ${existingResults.length} + 신규 ${newResults.length})
- 오류: ${newResults.filter(r=>r.error).length}개
- API 비용: $${totalCost.toFixed(4)}

## 전후 비교 (전체 ${afterSignals.length}개)

| 타입 | Before | After | 변화 |
|------|--------|-------|------|
| 매수 | ${beforeDist['매수']} | ${afterDist['매수']} | ${afterDist['매수']-beforeDist['매수']} |
| 긍정 | ${beforeDist['긍정']} | ${afterDist['긍정']} | ${afterDist['긍정']-beforeDist['긍정'] > 0 ? '+' : ''}${afterDist['긍정']-beforeDist['긍정']} |
| 중립 | ${beforeDist['중립']} | ${afterDist['중립']} | ${afterDist['중립']-beforeDist['중립'] > 0 ? '+' : ''}${afterDist['중립']-beforeDist['중립']} |
| 부정 | ${beforeDist['부정']} | ${afterDist['부정']} | ${afterDist['부정']-beforeDist['부정'] > 0 ? '+' : ''}${afterDist['부정']-beforeDist['부정']} |
| 매도 | ${beforeDist['매도']} | ${afterDist['매도']} | ${afterDist['매도']-beforeDist['매도'] > 0 ? '+' : ''}${afterDist['매도']-beforeDist['매도']} |

## DB UPDATE
- signal 변경: ${updateCount}건
- 스킵 (변경없음/매칭없음): ${skipCount}건
- pipeline_version V11: ${v11Count}건
`;

  fs.writeFileSync('C:\\Users\\Mario\\work\\data\\research\\v11_reclassify_report.md', report);

  // 텔레그램 보고용 JSON
  const telegramMsg = {
    beforeDist, afterDist, totalSignals: afterSignals.length,
    updateCount, skipCount, v11Count,
    totalCost: totalCost.toFixed(4),
    totalVideos: allResults.length, errors: newResults.filter(r=>r.error).length
  };
  fs.writeFileSync('C:\\Users\\Mario\\work\\data\\research\\v11_telegram_report.json', JSON.stringify(telegramMsg, null, 2));

  console.log('\n🎉 전체 완료!');
  console.log(JSON.stringify(telegramMsg, null, 2));
}

main().catch(e => { console.error('FATAL:', e); process.exit(1); });
