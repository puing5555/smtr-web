import https from 'https';
import fs from 'fs';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const ANTHROPIC_KEY = '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';

function fetchJSON(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const opts = { hostname: u.hostname, path: u.pathname + u.search, headers: { ...headers } };
    https.get(opts, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve(JSON.parse(d)); } catch(e) { reject(new Error(d.substring(0,500))); }
      });
    }).on('error', reject);
  });
}

function callClaude(systemPrompt, userPrompt) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      system: systemPrompt,
      messages: [{ role: 'user', content: userPrompt }]
    });
    const opts = {
      hostname: 'api.anthropic.com',
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_KEY,
        'anthropic-version': '2023-06-01'
      }
    };
    const req = https.request(opts, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(d);
          resolve(parsed);
        } catch(e) { reject(new Error(d.substring(0,500))); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

// V10 prompt (current) - extract signals with current criteria
const PROMPT_V10 = `당신은 한국 주식/미국 주식/크립토 인플루언서 영상 분석가입니다.
아래 자막에서 종목별 투자 시그널을 추출하세요.

**시그널 5단계:**
- 매수: "사라, 담아라, 들어가라, 비중 확대" (명확한 매수 액션 권유)
- 긍정: "좋아보인다, 괜찮다, 관심가져라" (호의적이나 명확한 매수 권유 아님)
- 중립: "지켜보자, 모르겠다" 또는 뉴스/리포트/교육 전달
- 부정: "조심해라, 리스크 있다, 주의" (부정적이나 매도 권유 아님)
- 매도: "팔아라, 손절해라, 빠져라" (명확한 매도 액션 권유)

**규칙:**
- 1영상 1종목 1시그널
- 논거/비교용 종목은 시그널 제외
- 뉴스/리포트 전달은 중립
- key_quote는 원문 그대로

**출력 형식 (JSON 배열):**
[{"stock_name": "종목명", "signal_type": "매수|긍정|중립|부정|매도", "confidence": 0.0-1.0, "key_quote": "핵심 발언 원문", "reason": "판단 근거"}]

시그널이 없으면 빈 배열 [] 반환.`;

// V11 prompt (enhanced) - much stricter buy criteria
const PROMPT_V11 = `당신은 한국 주식/미국 주식/크립토 인플루언서 영상 분석가입니다.
아래 자막에서 종목별 투자 시그널을 추출하세요.

**시그널 5단계 (V11 강화 기준):**

🔵 **매수** = 발언자가 **직접적으로 매수 행동을 권유**한 경우 **만**:
  - "사라", "매수 추천", "지금 들어가야", "포트폴리오에 편입해라"
  - "저는 이 종목 샀습니다/담았습니다" (본인 매매 공개 + 추천 맥락)
  - "이 가격이면 사도 된다", "분할매수 하라", "비중 확대해라"
  - ⚠️ 핵심 질문: "발언자가 직접 '사라'고 했는가?" → No이면 매수 아님

🟢 **긍정** = 호의적이지만 직접 매수 권유가 **없는** 경우:
  - "좋은 종목", "전망 밝다", "관심 가져볼 만하다"
  - "장기적으로 유망하다", "실적이 좋다"
  - "주목할 필요가 있다", "기대된다"
  - 분석만 제공하고 투자 액션 제안이 없는 경우
  - 타인/시장/애널리스트 의견 전달

🟡 **중립** = 단순 소개, 실적 분석만 (방향성 없음):
  - 뉴스/리포트 전달, 교육적 설명
  - "지켜보자", "모르겠다"

🟠 **부정** = 부정적이나 매도 권유 아님:
  - "위험하다", "주의해야", "비싸다", "고평가"

🔴 **매도** = 직접적 매도 권유:
  - "팔아라", "손절해라", "빠져라", "매도 추천"

**⚠️ 가장 흔한 오류: "긍정"을 "매수"로 분류하는 것**
- "전망이 밝다" → 긍정 (O) / 매수 (X)
- "좋은 기업이다" → 긍정 (O) / 매수 (X)  
- "관심 가져보세요" → 긍정 (O) / 매수 (X)
- "사세요", "담으세요", "지금 들어가세요" → 매수 (O)

**규칙:**
- 1영상 1종목 1시그널
- 논거/비교용 종목은 시그널 제외
- 뉴스/리포트 전달은 중립
- key_quote는 원문 그대로

**출력 형식 (JSON 배열):**
[{"stock_name": "종목명", "signal_type": "매수|긍정|중립|부정|매도", "confidence": 0.0-1.0, "key_quote": "핵심 발언 원문", "reason": "판단 근거"}]

시그널이 없으면 빈 배열 [] 반환.`;

async function main() {
  console.log('=== A/B Test V10 vs V11 ===\n');
  
  // 1. Fetch 10 videos with subtitles
  const sbHeaders = { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}` };
  const videos = await fetchJSON(
    `${SUPABASE_URL}/rest/v1/influencer_videos?has_subtitle=eq.true&select=id,title,channel_id,subtitle_text,published_at,video_id&order=published_at.desc&limit=10`,
    sbHeaders
  );
  console.log(`Fetched ${videos.length} videos\n`);
  
  // 2. Fetch existing signals for these videos
  const videoIds = videos.map(v => v.id);
  const existingSignals = await fetchJSON(
    `${SUPABASE_URL}/rest/v1/influencer_signals?video_id=in.(${videoIds.join(',')})&select=*`,
    sbHeaders
  );
  console.log(`Existing signals: ${existingSignals.length}\n`);
  
  // Group existing signals by video_id
  const signalsByVideo = {};
  for (const s of existingSignals) {
    if (!signalsByVideo[s.video_id]) signalsByVideo[s.video_id] = [];
    signalsByVideo[s.video_id].push(s);
  }
  
  const results = [];
  let totalInputTokens = 0, totalOutputTokens = 0;
  
  for (let i = 0; i < videos.length; i++) {
    const v = videos[i];
    const subtitle = v.subtitle_text || '';
    if (subtitle.length < 100) {
      console.log(`[${i+1}] Skipping "${v.title}" - subtitle too short (${subtitle.length})`);
      continue;
    }
    
    // Truncate subtitle to ~8000 chars to fit in context
    const truncSub = subtitle.length > 8000 ? subtitle.substring(0, 8000) + '\n...(이하 생략)' : subtitle;
    const userMsg = `영상 제목: ${v.title}\n\n자막:\n${truncSub}`;
    
    console.log(`[${i+1}/10] "${v.title.substring(0,50)}..." (subtitle: ${subtitle.length} chars)`);
    
    // A: V10 current
    console.log('  Running V10...');
    const respA = await callClaude(PROMPT_V10, userMsg);
    await sleep(3000);
    
    // B: V11 enhanced
    console.log('  Running V11...');
    const respB = await callClaude(PROMPT_V11, userMsg);
    await sleep(3000);
    
    // Track tokens
    if (respA.usage) { totalInputTokens += respA.usage.input_tokens; totalOutputTokens += respA.usage.output_tokens; }
    if (respB.usage) { totalInputTokens += respB.usage.input_tokens; totalOutputTokens += respB.usage.output_tokens; }
    
    // Parse results
    let signalsA = [], signalsB = [];
    try {
      const textA = respA.content?.[0]?.text || '';
      const jsonMatchA = textA.match(/\[[\s\S]*\]/);
      if (jsonMatchA) signalsA = JSON.parse(jsonMatchA[0]);
    } catch(e) { console.log('  V10 parse error:', e.message); }
    
    try {
      const textB = respB.content?.[0]?.text || '';
      const jsonMatchB = textB.match(/\[[\s\S]*\]/);
      if (jsonMatchB) signalsB = JSON.parse(jsonMatchB[0]);
    } catch(e) { console.log('  V11 parse error:', e.message); }
    
    const existing = signalsByVideo[v.id] || [];
    
    console.log(`  V10: ${signalsA.length} signals (매수: ${signalsA.filter(s=>s.signal_type==='매수').length})`);
    console.log(`  V11: ${signalsB.length} signals (매수: ${signalsB.filter(s=>s.signal_type==='매수').length})`);
    console.log(`  DB:  ${existing.length} signals\n`);
    
    results.push({
      video_id: v.id,
      title: v.title,
      published_at: v.published_at,
      subtitle_length: subtitle.length,
      v10_signals: signalsA,
      v11_signals: signalsB,
      db_signals: existing.map(s => ({ stock_name: s.stock_name, signal_type: s.signal_type, confidence: s.confidence })),
    });
  }
  
  // Summary
  const allV10 = results.flatMap(r => r.v10_signals);
  const allV11 = results.flatMap(r => r.v11_signals);
  const allDB = results.flatMap(r => r.db_signals);
  
  const countByType = (arr, field='signal_type') => {
    const c = {};
    for (const s of arr) { c[s[field]] = (c[s[field]] || 0) + 1; }
    return c;
  };
  
  const summary = {
    total_videos: results.length,
    v10: { total: allV10.length, by_type: countByType(allV10) },
    v11: { total: allV11.length, by_type: countByType(allV11) },
    db: { total: allDB.length, by_type: countByType(allDB) },
    cost: {
      input_tokens: totalInputTokens,
      output_tokens: totalOutputTokens,
      estimated_cost_usd: ((totalInputTokens * 3 / 1000000) + (totalOutputTokens * 15 / 1000000)).toFixed(4)
    }
  };
  
  console.log('\n=== SUMMARY ===');
  console.log(JSON.stringify(summary, null, 2));
  
  // Generate markdown report
  let md = `# 시그널 A/B 테스트: V10 현행 vs V11 강화 기준\n\n`;
  md += `**테스트 일시**: 2026-03-05\n`;
  md += `**테스트 영상**: ${results.length}개\n`;
  md += `**모델**: claude-sonnet-4-20250514\n\n`;
  
  md += `## 요약\n\n`;
  md += `| 구분 | V10 (현행) | V11 (강화) | DB (기존) |\n`;
  md += `|------|-----------|-----------|----------|\n`;
  md += `| 총 시그널 | ${allV10.length} | ${allV11.length} | ${allDB.length} |\n`;
  md += `| 매수 | ${summary.v10.by_type['매수']||0} | ${summary.v11.by_type['매수']||0} | ${summary.db.by_type['BUY']||summary.db.by_type['매수']||0} |\n`;
  md += `| 긍정 | ${summary.v10.by_type['긍정']||0} | ${summary.v11.by_type['긍정']||0} | ${summary.db.by_type['POSITIVE']||summary.db.by_type['긍정']||0} |\n`;
  md += `| 중립 | ${summary.v10.by_type['중립']||0} | ${summary.v11.by_type['중립']||0} | ${summary.db.by_type['NEUTRAL']||summary.db.by_type['중립']||0} |\n`;
  md += `| 부정 | ${summary.v10.by_type['부정']||0} | ${summary.v11.by_type['부정']||0} | ${summary.db.by_type['CONCERN']||summary.db.by_type['부정']||0} |\n`;
  md += `| 매도 | ${summary.v10.by_type['매도']||0} | ${summary.v11.by_type['매도']||0} | ${summary.db.by_type['SELL']||summary.db.by_type['매도']||0} |\n\n`;
  
  const v10Buy = summary.v10.by_type['매수']||0;
  const v11Buy = summary.v11.by_type['매수']||0;
  const buyReduction = v10Buy > 0 ? Math.round((1 - v11Buy/v10Buy) * 100) : 0;
  md += `### 핵심 지표\n`;
  md += `- **매수 시그널 변화**: ${v10Buy}개 → ${v11Buy}개 (${buyReduction}% 감소)\n`;
  md += `- **매수 비율**: V10 ${allV10.length?Math.round(v10Buy/allV10.length*100):0}% → V11 ${allV11.length?Math.round(v11Buy/allV11.length*100):0}%\n\n`;
  
  md += `## 영상별 상세 비교\n\n`;
  for (const r of results) {
    md += `### ${r.title}\n`;
    md += `- 발행: ${r.published_at}\n\n`;
    
    md += `**V10 시그널:**\n`;
    for (const s of r.v10_signals) {
      md += `- ${s.signal_type} | ${s.stock_name} | "${s.key_quote?.substring(0,80)||''}" | ${s.reason?.substring(0,80)||''}\n`;
    }
    if (r.v10_signals.length === 0) md += `- (없음)\n`;
    
    md += `\n**V11 시그널:**\n`;
    for (const s of r.v11_signals) {
      md += `- ${s.signal_type} | ${s.stock_name} | "${s.key_quote?.substring(0,80)||''}" | ${s.reason?.substring(0,80)||''}\n`;
    }
    if (r.v11_signals.length === 0) md += `- (없음)\n`;
    
    md += `\n**DB 기존 시그널:**\n`;
    for (const s of r.db_signals) {
      md += `- ${s.signal_type} | ${s.stock_name}\n`;
    }
    if (r.db_signals.length === 0) md += `- (없음)\n`;
    
    // Analyze misclassifications
    const v10Buys = r.v10_signals.filter(s => s.signal_type === '매수');
    const v11Reclassified = v10Buys.filter(v10s => {
      const match = r.v11_signals.find(v11s => v11s.stock_name === v10s.stock_name);
      return match && match.signal_type !== '매수';
    });
    if (v11Reclassified.length > 0) {
      md += `\n**⚠️ V10→V11 재분류 (매수→다른등급):**\n`;
      for (const s of v11Reclassified) {
        const v11match = r.v11_signals.find(v11s => v11s.stock_name === s.stock_name);
        md += `- ${s.stock_name}: 매수 → ${v11match.signal_type} | V11 근거: ${v11match.reason?.substring(0,100)||''}\n`;
      }
    }
    md += `\n---\n\n`;
  }
  
  md += `## 비용\n`;
  md += `- Input tokens: ${totalInputTokens.toLocaleString()}\n`;
  md += `- Output tokens: ${totalOutputTokens.toLocaleString()}\n`;
  md += `- 예상 비용: $${summary.cost.estimated_cost_usd}\n`;
  
  // Save
  fs.mkdirSync('C:\\Users\\Mario\\work\\data\\research', { recursive: true });
  fs.writeFileSync('C:\\Users\\Mario\\work\\data\\research\\signal_ab_test_v11.md', md, 'utf8');
  console.log('\nReport saved to data/research/signal_ab_test_v11.md');
  
  // Output summary JSON for messaging
  fs.writeFileSync('C:\\Users\\Mario\\work\\data\\research\\ab_test_summary.json', JSON.stringify(summary, null, 2), 'utf8');
}

main().catch(e => { console.error('FATAL:', e); process.exit(1); });
