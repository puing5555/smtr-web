const fs = require('fs');

// 1. Load source data
const deduped = JSON.parse(fs.readFileSync('smtr_data/corinpapa1106/_deduped_signals_8types_dated.json', 'utf8'));
const corrections = JSON.parse(fs.readFileSync('_opus_corrections.json', 'utf8'));

console.log('원본 시그널:', deduped.length);

// 2. Apply corrections
const deleteVids = corrections.filter(c => c.verdict === 'delete').map(c => c.video_id + '_' + c.original_asset);
const modifyMap = {};
for (const c of corrections.filter(c => c.verdict === 'modify')) {
  modifyMap[c.video_id + '_' + c.original_asset] = c.corrected;
}

const result = [];
for (const s of deduped) {
  const key = s.video_id + '_' + s.asset;
  
  // Check delete
  if (deleteVids.includes(key)) {
    console.log('삭제:', key);
    continue;
  }
  
  // Check modify
  if (modifyMap[key]) {
    const mod = modifyMap[key];
    console.log('수정:', key, '->', mod.signal_type);
    s.asset = mod.asset;
    s.signal_type = mod.signal_type;
    s.content = mod.content;
    s.context = mod.context;
    s.confidence = mod.confidence;
    s.timeframe = mod.timeframe;
    s.timestamp = mod.timestamp;
  }
  
  result.push(s);
}

console.log('수정 후 시그널:', result.length);

// 3. Save corrected deduped
fs.writeFileSync('smtr_data/corinpapa1106/_deduped_signals_8types_dated_corrected.json', JSON.stringify(result, null, 2), 'utf8');

// 4. Generate corinpapa-signals.ts
function extractTicker(asset) {
  const m = asset.match(/\(([^)]+)\)/);
  return m ? m[1] : asset;
}

const tsSignals = result.map((s, i) => ({
  id: 1000 + i,
  influencer: s.channel || '코린이 아빠',
  stock: extractTicker(s.asset),
  stockName: s.asset,
  signalType: s.signal_type,
  content: s.content,
  timestamp: s.timestamp,
  youtubeLink: `https://youtube.com/watch?v=${s.video_id}`,
  analysis: {
    summary: (s.merged_context || s.context || '').substring(0, 100) + '...',
    detail: s.merged_context || s.context || ''
  },
  videoDate: s.upload_date,
  videoTitle: s.title,
  confidence: s.confidence,
  timeframe: s.timeframe,
  conditional: s.conditional || false,
  skinInGame: s.skin_in_game || false,
  hedged: s.hedged || false,
  videoSummary: s.video_summary || ''
}));

const tsContent = `// 코린이 아빠 실제 시그널 데이터 (${tsSignals.length}개)
// 자동 생성됨 - 수정하지 마세요

export interface CorinpapaSignal {
  id: number;
  influencer: string;
  stock: string;
  stockName: string;
  signalType: string;
  content: string;
  timestamp: string;
  youtubeLink: string;
  analysis: {
    summary: string;
    detail: string;
  };
  videoDate: string;
  videoTitle: string;
  confidence: string;
  timeframe: string;
  conditional: boolean;
  skinInGame: boolean;
  hedged: boolean;
  videoSummary: string;
}

// 실제 시그널 데이터 (${tsSignals.length}개, 최신순 정렬)
export const corinpapaSignals: CorinpapaSignal[] = ${JSON.stringify(tsSignals.sort((a, b) => b.videoDate.localeCompare(a.videoDate)), null, 2)};
`;

fs.writeFileSync('src/data/corinpapa-signals.ts', tsContent, 'utf8');
console.log('corinpapa-signals.ts 생성 완료:', tsSignals.length, '개');
