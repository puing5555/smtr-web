const fs = require('fs');
const path = 'C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts';
let content = fs.readFileSync(path, 'utf8');

// Fix videoTitle values with problematic quotes
// Match "videoTitle": "..." where inner content has unescaped quotes
let fixed = content;
let count = 0;

// Replace all videoTitle lines
fixed = fixed.replace(/"videoTitle": "(.*)",\n/g, (match, value) => {
  // Check if value has unescaped quotes (quotes not preceded by backslash)
  // Remove all existing escapes first, then re-escape
  const unescaped = value.replace(/\\"/g, '"');
  // Now escape all inner quotes
  const escaped = unescaped.replace(/"/g, '\\"');
  if (escaped !== value) count++;
  return `"videoTitle": "${escaped}",\n`;
});

fs.writeFileSync(path, fixed, 'utf8');
console.log('Fixed titles with quote issues:', count);
