const fs = require('fs');
const html = fs.readFileSync('C:/Users/Mario/.openclaw/workspace/guru_tracker_prototype_v22.html','utf8');
// Try different patterns
const patterns = ['var allStatements = [', 'let allStatements = [', 'allStatements = ['];
for (const p of patterns) {
  const idx = html.indexOf(p);
  if (idx >= 0) { console.log('Found:', p, 'at', idx); console.log(html.substring(idx, idx+100)); break; }
}
