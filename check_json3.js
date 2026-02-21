const fs = require('fs');
const html = fs.readFileSync('C:/Users/Mario/.openclaw/workspace/guru_tracker_prototype_v22.html','utf8');

for (const name of ['parkStatements', 'hsStatements', 'sesangStatements']) {
  const marker = 'var ' + name + ' = [';
  const si = html.indexOf(marker);
  if (si < 0) { console.log(name, 'NOT FOUND'); continue; }
  let depth = 0, ei = si + marker.length - 1;
  for (let i = ei; i < html.length; i++) {
    if (html[i] === '[') depth++;
    if (html[i] === ']') { depth--; if (depth === 0) { ei = i + 1; break; } }
  }
  const jsonStr = html.substring(si + marker.length - 1, ei);
  try {
    const data = JSON.parse(jsonStr);
    console.log(name, 'OK, count:', data.length);
  } catch(e) {
    console.log(name, 'PARSE ERROR:', e.message.substring(0, 100));
    const pos = parseInt(e.message.match(/position (\d+)/)?.[1] || '0');
    if (pos > 0) console.log('  context:', JSON.stringify(jsonStr.substring(pos-80, pos+80)));
  }
}
