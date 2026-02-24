const fs = require('fs');
const path = 'C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts';
let c = fs.readFileSync(path, 'utf8');
const lines = c.split('\n');
let count = 0;
for (let i = 0; i < lines.length; i++) {
  if (lines[i].includes('Is the AI bubble really over')) {
    lines[i] = '    "videoTitle": "AI 버블 정말 끝났나? 배리의 공매도와 손정의의 탈출.",';
    count++;
  }
}
fs.writeFileSync(path, lines.join('\n'), 'utf8');
console.log('Fixed', count);
