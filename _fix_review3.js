const fs = require('fs');
let html = fs.readFileSync('invest-sns/signal-review.html', 'utf8');

// 1. Add influencer field to all signals data
html = html.replace(/"video_id"/g, '"influencer":"코린이 아빠","video_id"');

// 2. Add influencer name next to asset in card header
// Find the card rendering that shows asset name and add influencer
html = html.replace(
  /(\$\{signal\.asset\})/g,
  '${signal.asset} <span style="color:#94a3b8;font-size:14px;font-weight:400">· ${signal.influencer || "알 수 없음"}</span>'
);

// If that didn't work, try alternative patterns
if (!html.includes('signal.influencer')) {
  // Try finding the asset display pattern
  html = html.replace(
    /(signal\.asset)/g,
    function(match, p1, offset) {
      // Only replace first occurrence per pattern to avoid breaking code
      return match;
    }
  );
}

// 3. Add influencer filter dropdown
html = html.replace(
  /<option value="">전체<\/option>\s*<\/select>\s*<\/div>\s*<div[^>]*>\s*<label[^>]*>시그널 타입/,
  function(match) {
    return match; // Keep as is, we'll handle differently
  }
);

fs.writeFileSync('invest-sns/signal-review.html', html);
console.log('Done');
