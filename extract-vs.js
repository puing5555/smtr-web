const fs = require('fs');
const html = fs.readFileSync('C:/Users/Mario/work/smtr-web/signal-review-v3.html', 'utf8');

const match = html.match(/const\s+SIGNALS_DATA\s*=\s*(\[[\s\S]*?\]);/);
const signals = eval(match[1]);
console.log('Total HTML signals:', signals.length);

// video_summary is per-video, so just map video_id -> video_summary
const vsMap = {};
for (const s of signals) {
  if (s.video_summary && s.video_id && !vsMap[s.video_id]) {
    vsMap[s.video_id] = s.video_summary;
  }
}
console.log('Unique videos with summary:', Object.keys(vsMap).length);

// Read TS
const tsPath = 'C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts';
let tsContent = fs.readFileSync(tsPath, 'utf8');
const arrStart = tsContent.indexOf('export const corinpapaSignals: CorinpapaSignal[] = [');
const statsStart = tsContent.indexOf('export const corinpapaStats');
const header = tsContent.substring(0, arrStart);
const arrStr = tsContent.substring(arrStart + 'export const corinpapaSignals: CorinpapaSignal[] = '.length, statsStart).trim();
const lastBracket = arrStr.lastIndexOf(']');
const tsSignals = JSON.parse(arrStr.substring(0, lastBracket + 1));
console.log('TS signals:', tsSignals.length);
const footer = tsContent.substring(statsStart);

let updated = 0;
for (const sig of tsSignals) {
  const vidMatch = sig.youtubeLink && sig.youtubeLink.match(/[?&]v=([^&]+)/);
  if (!vidMatch) continue;
  const videoId = vidMatch[1];
  if (vsMap[videoId]) {
    sig.videoSummary = vsMap[videoId];
    updated++;
  }
}
console.log('Updated:', updated);

const newTs = header + 'export const corinpapaSignals: CorinpapaSignal[] = ' + JSON.stringify(tsSignals, null, 2) + ';\n\n' + footer;
fs.writeFileSync(tsPath, newTs, 'utf8');
console.log('Done');
