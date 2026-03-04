
const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A';
const SERVICE_ROLE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const ANTHROPIC_API_KEY = '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';

async function supabaseGet(table, query) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?${query}`, {
    headers: { 'apikey': SUPABASE_ANON_KEY, 'Authorization': `Bearer ${SUPABASE_ANON_KEY}` }
  });
  return res.json();
}

async function supabaseUpdate(table, id, data) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?id=eq.${id}`, {
    method: 'PATCH',
    headers: {
      'apikey': SERVICE_ROLE_KEY, 'Authorization': `Bearer ${SERVICE_ROLE_KEY}`,
      'Content-Type': 'application/json', 'Prefer': 'return=minimal',
    },
    body: JSON.stringify(data),
  });
  return res.status;
}

async function callClaude(prompt) {
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': ANTHROPIC_API_KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json',
    },
    body: JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 500, messages: [{ role: 'user', content: prompt }] }),
  });
  const json = await res.json();
  if (json.content?.[0]) return json.content[0].text;
  throw new Error(JSON.stringify(json));
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function main() {
  console.log('Fetching...');
  const all = await supabaseGet('influencer_signals', 'select=id,stock,ticker,signal,key_quote,reasoning&order=id');
  const short = all.filter(s => !s.reasoning || s.reasoning.length < 100);
  const shortKQ = all.filter(s => !s.key_quote || s.key_quote.length < 50);
  console.log(`Total: ${all.length}, Short reasoning: ${short.length}, Short KQ: ${shortKQ.length}`);

  const samples = [];
  let ok = 0, fail = 0, kqOk = 0, kqFail = 0;

  for (let i = 0; i < short.length; i++) {
    const s = short[i];
    console.log(`[${i}] Starting ${s.id} ${s.stock} (r:${s.reasoning?.length})`);
    const prompt = `다음 투자 시그널의 reasoning을 보강해주세요. 3~5문장, 100자 이상으로 확장합니다.

종목: ${s.stock}
시그널: ${s.signal}
핵심발언: ${s.key_quote || '없음'}
현재 reasoning: ${s.reasoning || '없음'}

보강 규칙:
- 문장 1: 화자가 이 종목을 언급한 맥락/이유
- 문장 2-3: 구체적 근거 (실적, 밸류에이션, 산업 트렌드 등)
- 문장 4-5: 전망/리스크
- 기존 reasoning의 내용을 포함하되 확장
- 한국어로 작성
- JSON 없이 순수 텍스트만 출력

보강된 reasoning만 출력하세요:`;

    let success = false;
    for (let retry = 0; retry < 3; retry++) {
      try {
        const enhanced = await callClaude(prompt);
        if (!enhanced || enhanced.length < 50) throw new Error('Too short');
        let updateData = { reasoning: enhanced };

        // Also enhance key_quote if short
        if (s.key_quote && s.key_quote.length < 50 && s.key_quote.length > 0) {
          try {
            const kqEnhanced = await callClaude(`다음 투자 시그널의 핵심 발언을 50자 이상으로 보강해주세요.

종목: ${s.stock}, 시그널: ${s.signal}
현재 핵심발언: ${s.key_quote}
reasoning: ${enhanced}

원래 발언의 의미를 유지하면서 구체적으로 확장. 인플루언서가 말한 것처럼 자연스러운 한국어 어투. 따옴표 없이 순수 텍스트만 출력.

보강된 핵심발언만 출력하세요:`);
            if (kqEnhanced?.length >= 30) { updateData.key_quote = kqEnhanced; kqOk++; }
            await sleep(500);
          } catch(e) { kqFail++; }
        }

        const st = await supabaseUpdate('influencer_signals', s.id, updateData);
        if (st >= 200 && st < 300) {
          if (samples.length < 5) samples.push({ id: s.id, stock: s.stock, oldR: s.reasoning, newR: enhanced, oldKQ: s.key_quote, newKQ: updateData.key_quote });
          ok++; success = true; break;
        }
        throw new Error('Update failed: ' + st);
      } catch(e) {
        console.error(`Retry ${retry+1}/3 [${s.id}] ${s.stock}: ${e.message?.substring(0,100)}`);
        await sleep(2000);
      }
    }
    if (!success) { fail++; console.error(`SKIP ${s.id} ${s.stock}`); }
    await sleep(1000);

    if ((i+1) % 10 === 0) console.log(`[${i+1}/${short.length}] ok:${ok} fail:${fail} kq:${kqOk}`);
    if ((i+1) % 100 === 0) console.log(`=== MILESTONE ${i+1}/${short.length} ===`);
  }

  // Remaining short key_quotes
  const doneIds = new Set(short.map(s => s.id));
  const remKQ = shortKQ.filter(s => !doneIds.has(s.id));
  console.log(`Remaining KQ to enhance: ${remKQ.length}`);
  for (const s of remKQ) {
    try {
      const kqE = await callClaude(`투자 시그널의 핵심 발언을 50자 이상으로 보강. 종목: ${s.stock}, 시그널: ${s.signal}, 현재: ${s.key_quote||'없음'}, reasoning: ${s.reasoning||'없음'}. 자연스러운 한국어, 텍스트만 출력.`);
      if (kqE?.length >= 30) { await supabaseUpdate('influencer_signals', s.id, { key_quote: kqE }); kqOk++; }
    } catch(e) { kqFail++; }
    await sleep(1000);
  }

  // Report
  const fs = await import('fs');
  fs.mkdirSync('data', { recursive: true });
  let rpt = `# Summary Enhancement Report\n\n- Reasoning 대상: ${short.length}건\n- 성공: ${ok}건, 실패: ${fail}건\n- Key_quote 보강: ${kqOk}건 (실패: ${kqFail}건)\n\n## 보강 전후 비교\n\n`;
  for (const s of samples) {
    rpt += `### ${s.stock} (${s.id})\n**Before:** ${s.oldR||'(없음)'}\n\n**After:** ${s.newR}\n\n`;
    if (s.newKQ) rpt += `**KQ Before:** ${s.oldKQ}\n\n**KQ After:** ${s.newKQ}\n\n`;
    rpt += '---\n\n';
  }
  fs.writeFileSync('data/summary_enhancement_report.md', rpt);

  console.log(`\n=== DONE === reasoning: ${ok}/${short.length} (fail:${fail}), kq: ${kqOk} (fail:${kqFail})`);
}

main().catch(e => { console.error('FATAL:', e); process.exit(1); });
