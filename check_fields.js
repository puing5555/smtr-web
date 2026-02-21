const fs = require('fs');
const html = fs.readFileSync('C:/Users/Mario/.openclaw/workspace/guru_tracker_prototype_v22.html','utf8');
// Get first few full signal objects
const si = html.indexOf('var parkStatements = [');
const chunk = html.substring(si, si + 2000);
// Print first 3 objects
const lines = chunk.split('\n').slice(1, 5);
lines.forEach(l => console.log(l.trim().substring(0, 300)));
