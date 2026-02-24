const fs = require('fs');
let src = fs.readFileSync('src/data/corinpapa-signals.ts', 'utf8');

// Remove broken stats section
const statsIdx = src.indexOf('export const corinpapaStats');
if (statsIdx > 0) {
  src = src.substring(0, statsIdx);
}

// Add proper stats
src += `
export const corinpapaStats = {
  totalSignals: 175,
  signalDistribution: {
    "STRONG_BUY": 8,
    "BUY": 29,
    "POSITIVE": 57,
    "HOLD": 8,
    "NEUTRAL": 7,
    "CONCERN": 37,
    "SELL": 18,
    "STRONG_SELL": 11
  },
  topStocks: [
    "캔톤네트워크 (CC)",
    "이더리움",
    "비트마인 (BMNR)",
    "XRP",
    "비트코인"
  ],
  accuracy: 68,
  avgReturn: 12.4,
  lastUpdate: '2026-02-24'
};
`;

fs.writeFileSync('src/data/corinpapa-signals.ts', src, 'utf8');
console.log('done');
