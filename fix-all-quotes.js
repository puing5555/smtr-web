const fs = require('fs');
const path = 'C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts';
let c = fs.readFileSync(path, 'utf8');
const lines = c.split('\n');
let fixed = 0;

for (let i = 0; i < lines.length; i++) {
  const m = lines[i].match(/^(\s*"videoTitle":\s*)"(.*)",?\s*$/);
  if (!m) continue;
  
  let value = m[2];
  // Check if value has unescaped quotes (not preceded by \)
  // First unescape all existing escapes
  const unescaped = value.replace(/\\"/g, '\x00QUOTE\x00');
  if (unescaped.includes('"')) {
    // Has unescaped quotes - remove them all (Korean titles don't need inner quotes)
    value = unescaped.replace(/"/g, '').replace(/\x00QUOTE\x00/g, '\\"');
    lines[i] = `${m[1]}"${value}",`;
    fixed++;
  }
}

fs.writeFileSync(path, lines.join('\n'), 'utf8');
console.log('Fixed', fixed, 'lines with unescaped quotes');
