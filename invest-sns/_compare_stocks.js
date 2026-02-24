const fs = require('fs');

// Source of truth: deduped signals
const deduped = JSON.parse(fs.readFileSync('smtr_data/corinpapa1106/_deduped_signals_8types_dated.json', 'utf8'));
const dedupedStocks = [...new Set(deduped.map(s => s.asset))].sort();

// Current site data
const src = fs.readFileSync('src/data/corinpapa-signals.ts', 'utf8');
const siteStocks = [...new Set([...src.matchAll(/"stockName":\s*"([^"]*)"/g)].map(m => m[1]))].sort();

console.log('=== 원본 (deduped) 종목 ===');
console.log(dedupedStocks.join('\n'));
console.log('\n=== 사이트 종목 ===');
console.log(siteStocks.join('\n'));

// Diff
const onlyInDeduped = dedupedStocks.filter(s => !siteStocks.includes(s));
const onlyInSite = siteStocks.filter(s => !dedupedStocks.includes(s));

console.log('\n=== 원본에만 있는 종목 ===');
console.log(onlyInDeduped.join('\n') || '없음');
console.log('\n=== 사이트에만 있는 종목 ===');
console.log(onlyInSite.join('\n') || '없음');

console.log('\n원본:', deduped.length, '개 / 사이트:', [...src.matchAll(/"id":\s*\d+/g)].length, '개');
