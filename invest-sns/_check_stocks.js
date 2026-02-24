const fs = require('fs');
const c = fs.readFileSync('./src/data/corinpapa-signals.ts', 'utf8');
const stocks = new Set();
const re = /"stock":\s*"([^"]+)"/g;
let m;
while ((m = re.exec(c)) !== null) stocks.add(m[1]);
console.log('Unique stocks:', [...stocks].sort());
console.log('Count:', stocks.size);
