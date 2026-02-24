const fs = require('fs');
const path = 'C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts';
let c = fs.readFileSync(path, 'utf8');

// Fix double-double quotes at end: "title"", -> "title",
let count = 0;
c = c.replace(/"videoTitle": "((?:[^"\\]|\\.)*)"\s*",/g, (match, inner) => {
  count++;
  return `"videoTitle": "${inner}",`;
});

fs.writeFileSync(path, c, 'utf8');
console.log('Fixed', count, 'double-quote issues');
