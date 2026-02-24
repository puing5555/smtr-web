const fs = require('fs');
const tsPath = 'C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts';
const content = fs.readFileSync(tsPath, 'utf8');
const arrStart = content.indexOf('export const corinpapaSignals: CorinpapaSignal[] = [');
const statsStart = content.indexOf('export const corinpapaStats');
const arrStr = content.substring(arrStart + 'export const corinpapaSignals: CorinpapaSignal[] = '.length, statsStart).trim();
const lastBracket = arrStr.lastIndexOf(']');
const signals = JSON.parse(arrStr.substring(0, lastBracket + 1));

const titles = [...new Set(signals.map(s => s.videoTitle))];
console.log('Unique titles:', titles.length);
titles.forEach(t => console.log(t));
