const fs = require('fs');
const src = fs.readFileSync('src/data/corinpapa-signals.ts', 'utf8');

// Parse signals by splitting on pattern
const idRegex = /"id":\s*(\d+)/g;
const ids = [];
let m;
while ((m = idRegex.exec(src)) !== null) {
  ids.push({ id: parseInt(m[1]), pos: m.index });
}

// For each id, extract the surrounding object text
for (const entry of ids) {
  // find enclosing { before id
  let start = entry.pos;
  while (start > 0 && src[start] !== '{') start--;
  
  // find matching }
  let depth = 0, end = start;
  for (let i = start; i < src.length; i++) {
    if (src[i] === '{') depth++;
    if (src[i] === '}') { depth--; if (depth === 0) { end = i + 1; break; } }
  }
  
  const block = src.substring(start, end);
  
  // Extract fields via regex
  const stockName = (block.match(/"stockName":\s*"([^"]*)"/) || [])[1] || '';
  const signalType = (block.match(/"signalType":\s*"([^"]*)"/) || [])[1] || '';
  const content = (block.match(/"content":\s*"([^"]*)"/) || [])[1] || '';
  const youtubeLink = (block.match(/"youtubeLink":\s*"([^"]*)"/) || [])[1] || '';
  const videoTitle = (block.match(/"videoTitle":\s*"([^"]*)"/) || [])[1] || '';
  
  // Check if this is one of the rejected ones
  const vidMatch = youtubeLink.match(/v=([^&]+)/);
  const vid = vidMatch ? vidMatch[1] : '';
  
  const rejectedKeys = {
    'oC-mHWKj8m8': '비트마인',
    'TjKVuAGhC1M': '코인베이스', 
    'YxekoL6IuvM': '캔톤네트워크',
    '151ejJicjy4': '타르'
  };
  
  if (rejectedKeys[vid] && stockName.includes(rejectedKeys[vid])) {
    console.log(`\n=== ID: ${entry.id} ===`);
    console.log(`종목: ${stockName}`);
    console.log(`시그널: ${signalType}`);
    console.log(`내용: ${content.substring(0, 120)}`);
    console.log(`영상: ${videoTitle}`);
    console.log(`링크: ${youtubeLink}`);
  }
}
