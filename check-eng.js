const fs = require('fs');
const c = fs.readFileSync('C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts', 'utf8');
const arrStart = c.indexOf('export const corinpapaSignals: CorinpapaSignal[] = [');
const statsStart = c.indexOf('export const corinpapaStats');
const arrStr = c.substring(arrStart + 'export const corinpapaSignals: CorinpapaSignal[] = '.length, statsStart).trim();
const lastBracket = arrStr.lastIndexOf(']');
const signals = JSON.parse(arrStr.substring(0, lastBracket + 1));

// Check how many still have English titles
const engPattern = /^["\s]*[A-Z]/;
let engCount = 0;
let korCount = 0;
const engTitles = new Set();
for (const s of signals) {
  if (!s.videoTitle) continue;
  // Check if title contains mostly ASCII
  const asciiRatio = s.videoTitle.replace(/[^a-zA-Z]/g, '').length / s.videoTitle.length;
  if (asciiRatio > 0.5) {
    engCount++;
    engTitles.add(s.videoTitle);
  } else {
    korCount++;
  }
}
console.log('English titles:', engCount, '(unique:', engTitles.size, ')');
console.log('Korean titles:', korCount);
console.log('\nEnglish titles:');
engTitles.forEach(t => console.log(' ', t));
