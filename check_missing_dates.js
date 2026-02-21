const fs = require('fs');
const html = fs.readFileSync('C:/Users/Mario/.openclaw/workspace/guru_tracker_prototype_v22.html','utf8');

// Extract realDates
const rdStart = html.indexOf('realDates = {');
const rdEnd = html.indexOf('};', rdStart) + 2;
const rdBlock = html.substring(rdStart, rdEnd);

for (const name of ['parkStatements', 'hsStatements', 'sesangStatements']) {
  const marker = 'var ' + name + ' = [';
  const si = html.indexOf(marker);
  let depth = 0, ei = si + marker.length - 1;
  for (let i = ei; i < html.length; i++) {
    if (html[i] === '[') depth++;
    if (html[i] === ']') { depth--; if (depth === 0) { ei = i + 1; break; } }
  }
  const data = JSON.parse(html.substring(si + marker.length - 1, ei));
  
  const vids = new Map();
  data.forEach(s => {
    const vid = s.video_id || (s.url && s.url.match(/[?&]v=([A-Za-z0-9_-]+)/)?.[1]);
    if (vid && vid.length >= 8) vids.set(vid, s.url);
  });
  
  let inRD = 0, missing = [];
  vids.forEach((url, v) => {
    if (rdBlock.includes('"' + v + '"')) inRD++;
    else missing.push(v);
  });
  
  console.log(`\n=== ${name} ===`);
  console.log(`Total signals: ${data.length}, Unique valid videos: ${vids.size}`);
  console.log(`In realDates: ${inRD}, Missing: ${missing.length}`);
  if (missing.length > 0) {
    console.log('Missing video IDs:');
    missing.forEach(v => console.log(`  ${v}  https://www.youtube.com/watch?v=${v}`));
  }
}
