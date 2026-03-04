const fs = require('fs');

const lines = fs.readFileSync('hs_analysis_results.jsonl', 'utf8').trim().split('\n');
const data = lines.map(l => JSON.parse(l));

// Step 1: Non-stock keywords to remove
const nonStockKeywords = [
  '비트코인', '이더리움', '리플', '솔라나', '도지코인', '카르다노', '폴카닷', '아발란체',
  '체인링크', '스텔라루멘', '라이트코인', '폴리곤', '시바이누', '앱토스',
  '금', '은', '원유', '천연가스', '구리', '백금', '팔라듐', '니켈', '알루미늄',
  '옥수수', '대두', '소맥', '밀', '철광석',
  '구리 관련 광산기업'
];

// Step 2: Unlisted companies to remove
const unlistedCompanies = ['스페이스X', '오픈AI', '웨이모', '야놀자', '삼성파운드리', '삼성디스플레이'];

// Ticker mappings for listed companies missing tickers
const tickerMap = {
  '폭스바겐': 'VOW3.DE',
  '루멘텀': 'LITE',  // Lumentum
  '화웨이': null, // not listed
  'BYD': '1211.HK',
};
// 화웨이 is not publicly traded on accessible exchanges - treat as unlisted
const alsoUnlisted = ['화웨이'];

let stats = { nonStock: 0, unlisted: 0, tickerFixed: 0, duplicateRemoved: 0 };
let totalOriginal = 0;

const cleaned = data.map(video => {
  const origLen = video.signals.length;
  totalOriginal += origLen;
  
  // Filter out non-stock signals
  let signals = video.signals.filter(s => {
    if (nonStockKeywords.includes(s.stock)) {
      stats.nonStock++;
      return false;
    }
    return true;
  });
  
  // Filter out unlisted companies, fix tickers
  signals = signals.filter(s => {
    if (unlistedCompanies.includes(s.stock) || alsoUnlisted.includes(s.stock)) {
      stats.unlisted++;
      return false;
    }
    // Fix missing tickers for listed companies
    if ((!s.ticker || s.ticker === '') && tickerMap[s.stock] !== undefined) {
      if (tickerMap[s.stock] === null) {
        stats.unlisted++;
        return false;
      }
      s.ticker = tickerMap[s.stock];
      stats.tickerFixed++;
    }
    return true;
  });
  
  // Deduplicate: same vid_id + same stock -> keep first
  const seen = new Set();
  signals = signals.filter(s => {
    const key = s.stock;
    if (seen.has(key)) {
      stats.duplicateRemoved++;
      return false;
    }
    seen.add(key);
    return true;
  });
  
  return { ...video, signals };
});

const totalCleaned = cleaned.reduce((sum, v) => sum + v.signals.length, 0);

// Write output
const output = cleaned.map(v => JSON.stringify(v)).join('\n');
fs.writeFileSync('hs_analysis_cleaned.jsonl', output + '\n');

console.log(JSON.stringify({
  totalOriginal,
  totalCleaned,
  removed: totalOriginal - totalCleaned,
  stats
}, null, 2));
