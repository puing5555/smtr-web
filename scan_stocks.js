const fs = require('fs');
const html = fs.readFileSync('C:/Users/Mario/.openclaw/workspace/guru_tracker_prototype_v22.html','utf8');
const re = /"stock":\s*"([^"]+)"/g;
const counts = {};
let m;
while(m = re.exec(html)) { counts[m[1]] = (counts[m[1]]||0)+1; }
Object.entries(counts).sort((a,b)=>b[1]-a[1]).forEach(([k,v])=>console.log(v+'\t'+k));
