const fs = require('fs');
const tsPath = 'C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts';
const content = fs.readFileSync(tsPath, 'utf8');

// Find the array
const arrStart = content.indexOf('export const corinpapaSignals: CorinpapaSignal[] = [');
const statsStart = content.indexOf('export const corinpapaStats');
const arrStr = content.substring(arrStart + 'export const corinpapaSignals: CorinpapaSignal[] = '.length, statsStart).trim();
const lastBracket = arrStr.lastIndexOf(']');
const signals = JSON.parse(arrStr.substring(0, lastBracket + 1));

// Find the XRP signal with "Why Coin YouTubers"
const sig = signals.find(s => s.videoTitle && s.videoTitle.includes('Why Coin YouTubers'));
if (sig) {
  console.log('videoSummary length:', sig.videoSummary ? sig.videoSummary.length : 'NONE');
  console.log('videoSummary:', sig.videoSummary);
}
