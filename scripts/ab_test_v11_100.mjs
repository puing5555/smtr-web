import fs from 'fs';
import path from 'path';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const ANTHROPIC_KEY = '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';
const MODEL = 'claude-sonnet-4-20250514';
const HYOSEOK_CHANNEL = 'd153b75b-1843-4a99-b49f-c31081a8f566';
const MAX_SUBTITLE = 8000;
const DELAY_MS = 3000;

const sbHeaders = { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}` };

async function supaGet(path) {
  const r = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, { headers: sbHeaders });
  if (!r.ok) throw new Error(`Supabase error: ${r.status} ${await r.text()}`);
  return r.json();
}

async function getSubtitle(videoId) {
  const rows = await supaGet(`influencer_videos?select=subtitle_text&id=eq.${videoId}`);
  return rows[0]?.subtitle_text || '';
}

const V10_PROMPT = fs.readFileSync('C:\\Users\\Mario\\work\\invest-sns\\prompts\\pipeline_v10.md', 'utf-8');

const V11_ADDITION = `

## ⚠️ V11 강화 규칙: 매수 vs 긍정 구분 (최우선 적용)

### 매수 시그널 엄격 기준
- **매수**: "사라", "담아라", "들어가라", "비중 확대", "지금 매수", "적극 매수" 등 **직접적 매수 행동 권유만** 해당
- "좋아보인다", "전망 밝다", "실적 좋다", "성장성 높다" → **매수가 아님, 긍정으로 분류**

### 핵심 자기검증 질문
시그널을 "매수"로 분류하기 전에 반드시 자문하라:
**"발언자가 직접 '사라'고 했는가?"**
- YES → 매수 가능
- NO → **매수 아님. 긍정으로 분류하라.**

### ⚠️ 가장 흔한 오류
"긍정"을 "매수"로 분류하는 것. 이 오류를 절대 범하지 마라.
긍정적 전망 ≠ 매수 추천. 매수는 **행동 지시**가 있어야만 한다.
`;

const V11_PROMPT = V10_PROMPT + V11_ADDITION;

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function callClaude(systemPrompt, userMessage, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const r = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'x-api-key': ANTHROPIC_KEY,
          'anthropic-version': '2023-06-01',
          'content-type': 'application/json'
        },
        body: JSON.stringify({
          model: MODEL,
          max_tokens: 4096,
          system: systemPrompt,
          messages: [{ role: 'user', content: userMessage }]
        })
      });
      
      if (r.status === 429) {
        console.log('  ⏳ Rate limited, waiting 60s...');
        await sleep(60000);
        continue;
      }
      if (!r.ok) {
        console.log(`  ❌ API error ${r.status}`);
        if (i < retries - 1) { await sleep(10000); continue; }
        return { signals: [], inputTokens: 0, outputTokens: 0 };
      }
      
      const data = await r.json();
      const text = data.content?.[0]?.text || '';
      const inputTokens = data.usage?.input_tokens || 0;
      const outputTokens = data.usage?.output_tokens || 0;
      
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      let parsed = { signals: [] };
      if (jsonMatch) {
        try { parsed = JSON.parse(jsonMatch[0]); } catch (e) { /* ignore */ }
      }
      
      return { signals: parsed.signals || [], inputTokens, outputTokens };
    } catch (err) {
      console.log(`  ⚠️ Attempt ${i+1} error: ${err.message}`);
      if (i < retries - 1) await sleep(10000);
    }
  }
  return { signals: [], inputTokens: 0, outputTokens: 0 };
}

async function main() {
  const startTime = Date.now();
  console.log('📋 Selecting videos...');
  
  // Get all videos (without subtitle_text for memory efficiency)
  const hyoseok = await supaGet(`influencer_videos?select=id,title,channel_id,published_at&channel_id=eq.${HYOSEOK_CHANNEL}&has_subtitle=eq.true&order=published_at.desc&limit=50`);
  
  const otherChannels = [
    'd68f8efd-64c8-4c07-9d34-e98c2954f4e1',
    'dde0918d-5237-4402-9782-e2d968958f64',
    '12facb47-407d-4fd3-a310-12dd5a802d1f',
    '4867e157-2126-4c67-aa5e-638372de8f03',
    '08642417-1b38-4295-a36f-3ed53713cfd5',
    'd4639050-bebf-41d4-9786-93005fb80b85'
  ];
  
  const remainNeeded = 100 - hyoseok.length;
  const perChannel = Math.ceil(remainNeeded / otherChannels.length);
  let otherPick = [];
  
  for (const ch of otherChannels) {
    const vids = await supaGet(`influencer_videos?select=id,title,channel_id,published_at&channel_id=eq.${ch}&has_subtitle=eq.true&order=published_at.desc&limit=${perChannel + 5}`);
    otherPick.push(...vids.slice(0, perChannel));
  }
  otherPick = otherPick.slice(0, remainNeeded);
  
  const videos = [...hyoseok, ...otherPick];
  const totalVideos = videos.length;
  console.log(`🎬 Total: ${totalVideos} videos (이효석: ${hyoseok.length}, 기타: ${otherPick.length})`);
  
  // Get existing signals
  const existingByVideo = {};
  for (let i = 0; i < videos.length; i += 20) {
    const batch = videos.slice(i, i + 20);
    const ids = batch.map(v => `"${v.id}"`).join(',');
    const sigs = await supaGet(`influencer_signals?select=video_id,stock,signal,ticker&video_id=in.(${ids})`);
    for (const s of sigs) {
      if (!existingByVideo[s.video_id]) existingByVideo[s.video_id] = [];
      existingByVideo[s.video_id].push(s);
    }
  }
  const totalExisting = Object.values(existingByVideo).flat().length;
  console.log(`📦 DB existing signals: ${totalExisting}`);
  
  // Process
  const results = [];
  let totalInput = 0, totalOutput = 0;
  const dist = { v10: {}, v11: {} };
  let buyToPositiveCount = 0;
  let truncatedVideos = 0;
  const outDir = 'C:\\Users\\Mario\\work\\data\\research';
  fs.mkdirSync(outDir, { recursive: true });
  
  for (let i = 0; i < totalVideos; i++) {
    const v = videos[i];
    
    // Fetch subtitle on demand
    const subtitleFull = await getSubtitle(v.id);
    const subLen = subtitleFull.length;
    const truncated = subLen > MAX_SUBTITLE;
    if (truncated) truncatedVideos++;
    
    const subtitle = truncated ? subtitleFull.slice(0, MAX_SUBTITLE) : subtitleFull;
    const userMsg = `영상 제목: ${v.title}\n\n자막:\n${subtitle}`;
    
    console.log(`\n[${i+1}/${totalVideos}] ${v.title.slice(0, 50)}... (sub: ${subLen}${truncated ? ' ✂️' : ''})`);
    
    let v10Result, v11Result;
    
    // V10
    v10Result = await callClaude(V10_PROMPT, userMsg);
    totalInput += v10Result.inputTokens;
    totalOutput += v10Result.outputTokens;
    console.log(`  V10: ${v10Result.signals.length} signals`);
    await sleep(DELAY_MS);
    
    // V11
    v11Result = await callClaude(V11_PROMPT, userMsg);
    totalInput += v11Result.inputTokens;
    totalOutput += v11Result.outputTokens;
    console.log(`  V11: ${v11Result.signals.length} signals`);
    await sleep(DELAY_MS);
    
    // Count distributions
    for (const s of v10Result.signals) dist.v10[s.signal_type] = (dist.v10[s.signal_type] || 0) + 1;
    for (const s of v11Result.signals) dist.v11[s.signal_type] = (dist.v11[s.signal_type] || 0) + 1;
    
    // Check buy→positive
    const v10Buys = v10Result.signals.filter(s => s.signal_type === '매수');
    for (const b of v10Buys) {
      if (v11Result.signals.find(s => s.stock === b.stock && s.signal_type === '긍정')) buyToPositiveCount++;
    }
    
    const dbSigs = existingByVideo[v.id] || [];
    
    results.push({
      videoId: v.id, title: v.title, channelId: v.channel_id,
      subtitleLength: subLen, truncated,
      v10Signals: v10Result.signals, v11Signals: v11Result.signals, dbSignals: dbSigs,
      v10Count: v10Result.signals.length, v11Count: v11Result.signals.length, dbCount: dbSigs.length
    });
    
    // Progress every 10
    if ((i + 1) % 10 === 0 || i + 1 === totalVideos) {
      const elapsed = ((Date.now() - startTime) / 60000).toFixed(1);
      const costEst = ((totalInput * 3 + totalOutput * 15) / 1000000).toFixed(2);
      console.log(`\n━━━ Progress: ${i+1}/${totalVideos} | ${elapsed}min | ~$${costEst} ━━━`);
      console.log(`V10:`, JSON.stringify(dist.v10));
      console.log(`V11:`, JSON.stringify(dist.v11));
      console.log(`Buy→Positive: ${buyToPositiveCount} | Truncated: ${truncatedVideos}/${i+1}`);
      
      // Save progress
      fs.writeFileSync(path.join(outDir, 'ab_test_progress.json'), JSON.stringify({
        progress: i + 1, total: totalVideos, dist, buyToPositiveCount, truncatedVideos,
        cost: costEst, elapsed
      }, null, 2));
    }
  }
  
  // Final report
  const elapsed = ((Date.now() - startTime) / 60000).toFixed(1);
  const costInput = (totalInput * 3 / 1000000).toFixed(2);
  const costOutput = (totalOutput * 15 / 1000000).toFixed(2);
  const totalCost = (parseFloat(costInput) + parseFloat(costOutput)).toFixed(2);
  
  let truncMissed = 0;
  for (const r of results) {
    if (r.truncated && r.dbCount > 0 && r.v10Count === 0 && r.v11Count === 0) truncMissed++;
  }
  
  const report = `# A/B Test: V10.10 vs V11 — ${totalVideos}영상 시그널 비교

## 실행 정보
- 실행 시간: ${elapsed}분
- 총 API 호출: ${results.length * 2}
- 비용: Input $${costInput} + Output $${costOutput} = **$${totalCost}**
- 모델: ${MODEL}

## 영상 구성
- 이효석: ${results.filter(r => r.channelId === HYOSEOK_CHANNEL).length}개
- 기타 채널: ${results.filter(r => r.channelId !== HYOSEOK_CHANNEL).length}개

## 자막 Truncation 분석
- Truncated (>8000자): **${truncatedVideos}개** / ${totalVideos}
- 90K+ 자막: ${results.filter(r => r.subtitleLength >= 90000).length}개
- 50K+ 자막: ${results.filter(r => r.subtitleLength >= 50000).length}개
- 평균 자막 길이: ${Math.round(results.reduce((a, r) => a + r.subtitleLength, 0) / results.length)}자
- Truncation으로 누락 의심 (DB有, V10+V11 둘다 0): **${truncMissed}건**

## V10.10 시그널 분포
${Object.entries(dist.v10).sort((a,b) => b[1]-a[1]).map(([k,v]) => `- ${k}: ${v}건`).join('\n')}
- **총: ${Object.values(dist.v10).reduce((a,b) => a+b, 0)}건**

## V11 시그널 분포
${Object.entries(dist.v11).sort((a,b) => b[1]-a[1]).map(([k,v]) => `- ${k}: ${v}건`).join('\n')}
- **총: ${Object.values(dist.v11).reduce((a,b) => a+b, 0)}건**

## 핵심 지표
- **매수→긍정 재분류: ${buyToPositiveCount}건**
- V10 매수: ${dist.v10['매수'] || 0} → V11 매수: ${dist.v11['매수'] || 0} (${dist.v10['매수'] ? Math.round(((dist.v10['매수'] || 0) - (dist.v11['매수'] || 0)) / (dist.v10['매수'] || 1) * 100) : 0}% 감소)

## DB 비교
- DB 기존: ${totalExisting}건 | V10: ${Object.values(dist.v10).reduce((a,b) => a+b, 0)}건 | V11: ${Object.values(dist.v11).reduce((a,b) => a+b, 0)}건

## 개별 결과

| # | 제목 | 자막 | T | V10 | V11 | DB | 변경 |
|---|------|------|---|-----|-----|-----|------|
${results.map((r, i) => {
  const v10Buys = r.v10Signals.filter(s => s.signal_type === '매수').map(s => s.stock);
  const v11Pos = r.v11Signals.filter(s => s.signal_type === '긍정').map(s => s.stock);
  const reclassed = v10Buys.filter(s => v11Pos.includes(s));
  const changes = reclassed.length > 0 ? `매수→긍정: ${reclassed.join(',')}` : '-';
  return `| ${i+1} | ${r.title.slice(0,25)} | ${r.subtitleLength} | ${r.truncated ? '✂️' : ''} | ${r.v10Count} | ${r.v11Count} | ${r.dbCount} | ${changes} |`;
}).join('\n')}

## Truncation 누락 의심 영상
${results.filter(r => r.truncated && r.dbCount > 0 && r.v10Count === 0 && r.v11Count === 0).map(r => `- **${r.title}** (${r.subtitleLength}자, DB: ${r.dbCount}개)`).join('\n') || '없음'}
`;

  const summary = {
    executionTime: `${elapsed}min`, totalCost: `$${totalCost}`, model: MODEL,
    videoCount: totalVideos,
    hyoseokCount: results.filter(r => r.channelId === HYOSEOK_CHANNEL).length,
    otherCount: results.filter(r => r.channelId !== HYOSEOK_CHANNEL).length,
    truncation: {
      truncatedCount: truncatedVideos,
      over90k: results.filter(r => r.subtitleLength >= 90000).length,
      over50k: results.filter(r => r.subtitleLength >= 50000).length,
      avgLength: Math.round(results.reduce((a, r) => a + r.subtitleLength, 0) / results.length),
      missedDueToTruncation: truncMissed
    },
    v10Distribution: dist.v10, v11Distribution: dist.v11,
    buyToPositiveReclassifications: buyToPositiveCount,
    dbExistingSignals: totalExisting,
    v10Total: Object.values(dist.v10).reduce((a,b) => a+b, 0),
    v11Total: Object.values(dist.v11).reduce((a,b) => a+b, 0),
    details: results.map(r => ({
      title: r.title, subtitleLength: r.subtitleLength, truncated: r.truncated,
      v10: r.v10Signals.map(s => ({ stock: s.stock, signal: s.signal_type })),
      v11: r.v11Signals.map(s => ({ stock: s.stock, signal: s.signal_type })),
      db: r.dbSignals.map(s => ({ stock: s.stock, signal: s.signal }))
    }))
  };

  fs.writeFileSync(path.join(outDir, 'signal_ab_test_v11_100.md'), report, 'utf-8');
  fs.writeFileSync(path.join(outDir, 'ab_test_100_summary.json'), JSON.stringify(summary, null, 2), 'utf-8');
  
  console.log(`\n✅ Done! ${totalVideos} videos processed in ${elapsed}min`);
  console.log(`💰 Cost: $${totalCost}`);
  console.log(`📊 V10: ${JSON.stringify(dist.v10)}`);
  console.log(`📊 V11: ${JSON.stringify(dist.v11)}`);
  console.log(`🔄 Buy→Positive: ${buyToPositiveCount}`);
  
  // Write completion flag
  fs.writeFileSync(path.join(outDir, 'ab_test_complete.flag'), JSON.stringify({ done: true, cost: totalCost, time: elapsed }));
}

process.on('uncaughtException', e => { console.error('UNCAUGHT:', e.message, e.stack); });
process.on('unhandledRejection', e => { console.error('UNHANDLED:', e?.message || e, e?.stack); });
main().catch(e => { console.error('FATAL:', e.message, e.stack); process.exit(1); });
