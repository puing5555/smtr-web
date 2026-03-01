const fs = require('fs');
const path = require('path');

const dir = 'C:/Users/Mario/work/subs';
const files = fs.readdirSync(dir).filter(f => f.endsWith('_fulltext.txt'));

// Need summaries for these video IDs (placeholder summaries in DB)
const needSummary = [
  'R6w3T3eUVIs','XFHD_1M3Mxg','x0TKvrIdIwI','I4Tt3tevuTU','8-hYd-8eojE',
  '-US4r1E1kOQ','ldT75QwBB6g','irK0YCnox78','qYAiv0Kljas','hxpOT8n_ICw',
  '_MrBnIb0jOk','kFa9RxL4HnA','xtl0nnxAYKc','rpoGBOJZ2fk','B2ARIKugV-k',
  'B5owNUs_DFw'
];

for (const vid of needSummary) {
  const file = files.find(f => {
    const noSuffix = f.replace('_fulltext.txt','');
    const idx = noSuffix.indexOf('_');
    return noSuffix.substring(idx+1) === vid;
  });
  if (!file) { console.log(`NO FILE: ${vid}`); continue; }
  const text = fs.readFileSync(path.join(dir, file), 'utf8');
  const first2k = text.substring(0, 2000);
  console.log(`\n=== ${vid} (${file}) ===`);
  console.log(first2k);
  console.log('=== END ===');
}
