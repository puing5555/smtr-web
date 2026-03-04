
import https from 'https';
import http from 'http';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A';
const SERVICE_ROLE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const ANTHROPIC_API_KEY = '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';
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '';
const TELEGRAM_CHAT_ID = '-1003764256213';

function fetch_(url, options = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const mod = u.protocol === 'https:' ? https : http;
    const req = mod.request(u, {
      method: options.method || 'GET',
      headers: options.headers || {},
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve({ status: res.statusCode, text: () => Promise.resolve(data), json: () => Promise.resolve(JSON.parse(data)) }));
    });
    req.on('error', reject);
    if (options.body) req.write(options.body);
    req.end();
  });
}

async function supabaseGet(table, query) {
  const res = await fetch_(`${SUPABASE_URL}/rest/v1/${table}?${query}`, {
    headers: {
      'apikey': SUPABASE_ANON_KEY,
      'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
    }
  });
  return res.json();
}

async function supabaseUpdate(table, id, data) {
  const res = await fetch_(`${SUPABASE_URL}/rest/v1/${table}?id=eq.${id}`, {
    method: 'PATCH',
    headers: {
      'apikey': SERVICE_ROLE_KEY,
      'Authorization': `Bearer ${SERVICE_ROLE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=minimal',
    },
    body: JSON.stringify(data),
  });
  return res.status;
}

async function callClaude(prompt) {
  const res = await fetch_('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 500,
      messages: [{ role: 'user', content: prompt }],
    }),
  });
  const json = await res.json();
  if (json.content && json.content[0]) return json.content[0].text;
  throw new Error(JSON.stringify(json));
}

async function sendTelegram(text) {
  console.log('[TG]', text);
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  console.log('Fetching signals with short reasoning...');
  
  // Get all signals, filter client-side for reasoning length
  const allSignals = await supabaseGet('influencer_signals', 'select=id,stock,ticker,signal,key_quote,reasoning&order=id');
  console.log(`Total signals: ${allSignals.length}`);
  
  const shortReasoning = allSignals.filter(s => !s.reasoning || s.reasoning.length < 100);
  const shortKeyQuote = allSignals.filter(s => !s.key_quote || s.key_quote.length < 50);
  
  console.log(`Short reasoning (<100): ${shortReasoning.length}`);
  console.log(`Short key_quote (<50): ${shortKeyQuote.length}`);
  
  // Collect samples for report
  const samples = [];
  let processed = 0;
  let failed = 0;
  let kqProcessed = 0;
  let kqFailed = 0;

  // Process reasoning
  for (let i = 0; i < shortReasoning.length; i++) {
    const s = shortReasoning[i];
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
        if (enhanced && enhanced.length >= 50) {
          // Also enhance key_quote if short
          let updateData = { reasoning: enhanced };
          
          if (s.key_quote && s.key_quote.length < 50) {
            try {
              const kqPrompt = `다음 투자 시그널의 핵심 발언을 50자 이상으로 보강해주세요.

종목: ${s.stock}
시그널: ${s.signal}
현재 핵심발언: ${s.key_quote}
reasoning: ${enhanced}

보강 규칙:
- 원래 발언의 의미를 유지하면서 구체적으로 확장
- 실제 인플루언서가 말한 것처럼 자연스러운 어투
- 한국어로 작성
- 따옴표 없이 순수 텍스트만 출력

보강된 핵심발언만 출력하세요:`;
              const enhancedKQ = await callClaude(kqPrompt);
              if (enhancedKQ && enhancedKQ.length >= 30) {
                updateData.key_quote = enhancedKQ;
                kqProcessed++;
              }
              await sleep(500);
            } catch(e) {
              console.error(`KQ enhance failed for ${s.id}: ${e.message}`);
              kqFailed++;
            }
          }
          
          const status = await supabaseUpdate('influencer_signals', s.id, updateData);
          if (status >= 200 && status < 300) {
            if (samples.length < 5) {
              samples.push({ id: s.id, stock: s.stock, oldReasoning: s.reasoning, newReasoning: enhanced, oldKQ: s.key_quote, newKQ: updateData.key_quote });
            }
            processed++;
            success = true;
            break;
          }
        }
        throw new Error('Short response or update failed');
      } catch(e) {
        console.error(`Retry ${retry+1}/3 for ${s.id} (${s.stock}): ${e.message}`);
        await sleep(2000);
      }
    }
    if (!success) {
      failed++;
      console.error(`SKIPPED ${s.id} (${s.stock})`);
    }

    await sleep(1000);

    if ((i + 1) % 100 === 0) {
      const msg = `🔧 [DEV] summary 보강 진행: ${i+1}/${shortReasoning.length}건 (성공: ${processed}, 실패: ${failed})`;
      console.log(msg);
      await sendTelegram(msg);
    }
    
    if ((i + 1) % 10 === 0) {
      console.log(`Progress: ${i+1}/${shortReasoning.length} (ok:${processed} fail:${failed})`);
    }
  }

  // Handle remaining short key_quotes not already processed
  const processedIds = new Set(shortReasoning.map(s => s.id));
  const remainingKQ = shortKeyQuote.filter(s => !processedIds.has(s.id));
  
  for (let i = 0; i < remainingKQ.length; i++) {
    const s = remainingKQ[i];
    let success = false;
    for (let retry = 0; retry < 3; retry++) {
      try {
        const kqPrompt = `다음 투자 시그널의 핵심 발언을 50자 이상으로 보강해주세요.

종목: ${s.stock}
시그널: ${s.signal}
현재 핵심발언: ${s.key_quote || '없음'}
reasoning: ${s.reasoning || '없음'}

보강 규칙:
- 원래 발언의 의미를 유지하면서 구체적으로 확장
- 실제 인플루언서가 말한 것처럼 자연스러운 어투
- 한국어로 작성
- 따옴표 없이 순수 텍스트만 출력

보강된 핵심발언만 출력하세요:`;
        const enhanced = await callClaude(kqPrompt);
        if (enhanced && enhanced.length >= 30) {
          const status = await supabaseUpdate('influencer_signals', s.id, { key_quote: enhanced });
          if (status >= 200 && status < 300) { kqProcessed++; success = true; break; }
        }
        throw new Error('Failed');
      } catch(e) {
        await sleep(2000);
      }
    }
    if (!success) kqFailed++;
    await sleep(1000);
  }

  // Save report
  let report = `# Summary Enhancement Report\n\n`;
  report += `- 처리 대상 (reasoning): ${shortReasoning.length}건\n`;
  report += `- 성공: ${processed}건\n`;
  report += `- 실패: ${failed}건\n`;
  report += `- key_quote 보강: ${kqProcessed}건 (실패: ${kqFailed}건)\n\n`;
  report += `## 보강 전후 비교 샘플\n\n`;
  for (const s of samples) {
    report += `### ID: ${s.id} — ${s.stock}\n`;
    report += `**Before reasoning:** ${s.oldReasoning || '(없음)'}\n\n`;
    report += `**After reasoning:** ${s.newReasoning}\n\n`;
    if (s.newKQ) {
      report += `**Before key_quote:** ${s.oldKQ || '(없음)'}\n\n`;
      report += `**After key_quote:** ${s.newKQ}\n\n`;
    }
    report += `---\n\n`;
  }

  const fs = await import('fs');
  fs.mkdirSync('data', { recursive: true });
  fs.writeFileSync('data/summary_enhancement_report.md', report);
  console.log('Report saved to data/summary_enhancement_report.md');

  const finalMsg = `✅ [DEV] summary 보강 완료: reasoning ${processed}/${shortReasoning.length}건 (실패 ${failed}건), key_quote ${kqProcessed}건 보강`;
  console.log(finalMsg);
  await sendTelegram(finalMsg);
}

main().catch(e => { console.error('FATAL:', e); process.exit(1); });
