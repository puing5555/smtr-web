const fs = require('fs');
const html = fs.readFileSync('C:/Users/Mario/work/smtr-web/signal-review-v3.html', 'utf8');
const match = html.match(/const\s+SIGNALS_DATA\s*=\s*(\[[\s\S]*?\]);/);
const signals = eval(match[1]);

// Build multiple maps
const byVidAssetType = {};
const byVidAsset = {};
const byVidContent = {};
for (const s of signals) {
  if (s.video_summary && s.video_id) {
    byVidAssetType[s.video_id + '|' + s.asset + '|' + s.signal_type] = s.video_summary;
    // Also by video_id + content substring
    const contentKey = s.video_id + '|' + (s.content || '').substring(0, 30);
    byVidContent[contentKey] = s.video_summary;
  }
}

const tsPath = 'C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts';
let tsContent = fs.readFileSync(tsPath, 'utf8');
const arrStart = tsContent.indexOf('export const corinpapaSignals: CorinpapaSignal[] = [');
const statsStart = tsContent.indexOf('export const corinpapaStats');
const arrStr = tsContent.substring(arrStart + 'export const corinpapaSignals: CorinpapaSignal[] = '.length, statsStart).trim();
const lastBracket = arrStr.lastIndexOf(']');
const tsSignals = JSON.parse(arrStr.substring(0, lastBracket + 1));

let unmatched = 0;
for (const sig of tsSignals) {
  if (sig.videoSummary) continue;
  const vidMatch = sig.youtubeLink && sig.youtubeLink.match(/[?&]v=([^&]+)/);
  if (!vidMatch) { unmatched++; continue; }
  const videoId = vidMatch[1];
  
  // Try content match
  const contentKey = videoId + '|' + (sig.content || '').substring(0, 30);
  if (byVidContent[contentKey]) {
    continue; // would match
  }
  
  console.log(`UNMATCHED: ${sig.stock} | ${sig.signalType} | vid=${videoId} | content=${(sig.content||'').substring(0,40)}`);
  // Show what HTML has for same video_id
  const htmlSigs = signals.filter(s => s.video_id === videoId);
  for (const h of htmlSigs) {
    console.log(`  HTML: ${h.asset} | ${h.signal_type} | content=${(h.content||'').substring(0,40)}`);
  }
  unmatched++;
}
console.log('Total unmatched:', unmatched);
