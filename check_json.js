const fs = require('fs');
const html = fs.readFileSync('C:/Users/Mario/.openclaw/workspace/guru_tracker_prototype_v22.html','utf8');
// Find allStatements data
const startMarker = 'const allStatements = [';
const si = html.indexOf(startMarker);
console.log('allStatements starts at:', si);
// Find the closing ];
let depth = 0, ei = si + startMarker.length - 1;
for (let i = ei; i < html.length; i++) {
  if (html[i] === '[') depth++;
  if (html[i] === ']') { depth--; if (depth === 0) { ei = i + 1; break; } }
}
const jsonStr = html.substring(si + 'const allStatements = '.length, ei);
try {
  const data = JSON.parse(jsonStr);
  console.log('Parsed OK, signals:', data.length);
} catch(e) {
  console.log('PARSE ERROR:', e.message);
  // Find position
  const pos = parseInt(e.message.match(/position (\d+)/)?.[1] || '0');
  console.log('Around pos', pos, ':', jsonStr.substring(pos-50, pos+50));
}
