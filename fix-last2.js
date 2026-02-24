const fs = require('fs');
const path = 'C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts';
let c = fs.readFileSync(path, 'utf8');
// Replace all variations of this title
c = c.replace(/"videoTitle": "Is the AI[^"]*Barry[^"]*"/g, '"videoTitle": "AI 버블 정말 끝났나? 배리의 공매도와 손정의의 탈출."');
fs.writeFileSync(path, c, 'utf8');
console.log('done');
