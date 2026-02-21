const fs = require('fs');
const html = fs.readFileSync('C:/Users/Mario/.openclaw/workspace/guru_tracker_prototype_v22.html','utf8');

// Extract sesangStatements
const si = html.indexOf('var sesangStatements = [');
let depth = 0, ei = si + 'var sesangStatements = ['.length - 1;
for (let i = ei; i < html.length; i++) {
  if (html[i] === '[') depth++;
  if (html[i] === ']') { depth--; if (depth === 0) { ei = i + 1; break; } }
}
const data = JSON.parse(html.substring(si + 'var sesangStatements = '.length, ei));
console.log('Total sesang signals:', data.length);

// Check video_ids and if they have realDates
const rdStart = html.indexOf('realDates = {');
const rdEnd = html.indexOf('};', rdStart) + 2;
// Just check unique video_ids from sesang
const vids = new Set();
data.forEach(s => { if(s.video_id) vids.add(s.video_id); });
console.log('Unique video_ids:', vids.size);
console.log('Sample video_ids:', [...vids].slice(0,10));

// Check which are in realDates
const rdBlock = html.substring(rdStart, rdEnd);
let inRD = 0, notInRD = 0;
const missing = [];
vids.forEach(v => {
  if (rdBlock.includes(v)) inRD++;
  else { notInRD++; missing.push(v); }
});
console.log('In realDates:', inRD, 'Missing:', notInRD);
console.log('Missing IDs:', missing.slice(0,20));

// Check the upload dates (from url field)
const urls = new Set();
data.forEach(s => { if(s.url) urls.add(s.url.split('?v=')[1]?.split('&')[0]); });
console.log('Unique URL video IDs:', [...urls].slice(0,10));
