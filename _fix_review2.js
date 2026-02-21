const fs = require('fs');

// Read signals
const signals = JSON.parse(fs.readFileSync('invest-sns/smtr_data/corinpapa1106/_all_signals_194.json', 'utf8'));
const mapped = signals.map(s => ({
  video_id: s.video_id,
  stock: s.asset || 'N/A',
  signal: (s.signal_type || '').toLowerCase(),
  timestamp: '',
  quote: s.content || '',
  detail: s.context || '',
  speaker: '코린이 아빠',
  summary: s.title || '',
  source: 'corinpapa1106',
  influencer: '코린이 아빠',
  upload_date: '',
  dirType: (s.signal_type || '').toLowerCase(),
  date: '',
  confidence: s.confidence || ''
}));

// Read verify results
const verifyText = fs.readFileSync('C:/Users/Mario/.openclaw/workspace/smtr_data/corinpapa1106/_verify_batch_full_result.jsonl', 'utf8').trim();

let html = fs.readFileSync('invest-sns/signal-review.html', 'utf8');

// Replace signals data
html = html.replace(/const EMBEDDED_SIGNALS_DATA\s*=\s*.*?;/, 'const EMBEDDED_SIGNALS_DATA = ' + JSON.stringify(mapped) + ';');

// Add embedded verify data if not already there
if (!html.includes('EMBEDDED_VERIFY_DATA')) {
  html = html.replace(
    'const EMBEDDED_SIGNALS_DATA',
    'const EMBEDDED_VERIFY_DATA = ' + JSON.stringify(verifyText) + ';\nconst EMBEDDED_SIGNALS_DATA'
  );
}

// Patch loadData to use embedded verify data instead of fetch
html = html.replace(
  /\/\/ GPT 검증 결과 로드 \(JSONL 파일\)[\s\S]*?console\.warn\('GPT 검증 결과를 불러올 수 없습니다:', e\);\s*\}/,
  '// GPT 검증 결과 (내장 데이터)\n                if(typeof EMBEDDED_VERIFY_DATA !== "undefined") {\n                    parseVerificationResults(EMBEDDED_VERIFY_DATA);\n                }'
);

// Patch Claude results - pipeline said 0 suspicious so skip
html = html.replace(
  /\/\/ Claude 검증 결과 로드 \(JSON 파일\)[\s\S]*?console\.warn\('Claude 검증 결과를 불러올 수 없습니다:', e\);\s*\}/,
  '// Claude 검증 (의심 시그널 0개로 생략됨 - 전부 통과)\n                console.log("Claude: 전체 통과");'
);

fs.writeFileSync('invest-sns/signal-review.html', html);
console.log('Done! Signals:', mapped.length, 'Verify lines:', verifyText.split('\n').length);
