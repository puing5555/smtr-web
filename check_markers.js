const fs = require('fs');
const html = fs.readFileSync('C:/Users/Mario/.openclaw/workspace/guru_tracker_prototype_v22.html','utf8');

// Get some marker dates
const re = /"date":\s*"([^"]+)"/g;
const dates = new Set();
let m;
while(m = re.exec(html)) { dates.add(m[1]); if(dates.size > 20) break; }
console.log('Sample signal dates:', [...dates].slice(0,20));

// Get some price data dates
const priceRe = /"time":\s*"([^"]+)"/g;
const priceDates = new Set();
while(m = priceRe.exec(html)) { priceDates.add(m[1]); if(priceDates.size > 10) break; }
console.log('Sample price dates:', [...priceDates].slice(0,10));
