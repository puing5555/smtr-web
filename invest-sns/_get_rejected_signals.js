const fs = require('fs');
const deduped = JSON.parse(fs.readFileSync('smtr_data/corinpapa1106/_deduped_signals_8types_dated.json', 'utf8'));

const rejectedVideos = {
  'oC-mHWKj8m8': '비트마인',
  'TjKVuAGhC1M': '코인베이스',
  'YxekoL6IuvM': '캔톤네트워크',
  '151ejJicjy4': '타르'
};

for (const s of deduped) {
  for (const [vid, stock] of Object.entries(rejectedVideos)) {
    if (s.video_id === vid && s.asset.includes(stock)) {
      console.log(JSON.stringify(s, null, 2));
      console.log('---SEPARATOR---');
    }
  }
}
