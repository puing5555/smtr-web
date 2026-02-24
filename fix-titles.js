const fs = require('fs');
const path = 'C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts';
let content = fs.readFileSync(path, 'utf8');

// Fix unquoted videoTitle values
// Pattern: "videoTitle": <not a quote>...,
const fixed = content.replace(/"videoTitle": ([^"\n][^\n]*?),\n/g, (match, value) => {
  // value is unquoted - wrap in quotes, escape any inner quotes
  const clean = value.trim().replace(/"/g, '\\"');
  return `"videoTitle": "${clean}",\n`;
});

const diff = content.length !== fixed.length;
fs.writeFileSync(path, fixed, 'utf8');

// Count fixes
const origMatches = content.match(/"videoTitle": [^"\n]/g);
console.log('Unquoted titles found:', origMatches ? origMatches.length : 0);
console.log('Fixed:', diff ? 'yes' : 'no change');
