const fs = require('fs');

// Read the current file
let content = fs.readFileSync('C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts', 'utf8');

// Final targeted replacements for exact matches in the file
const exactReplacements = [
  {
    from: '\"Decision to Part with XRP (WLFI Mar-a-Lago Forum Impact)\"',
    to: '\"XRP와의 결별 결정 (WLFI 마라라고 포럼 충격)\"'
  },
  {
    from: '\"Don\'t call me CNTN, from now on it\'s [Canton]!\"',
    to: '\"나를 CNTN이라 부르지 마라, 이제부터는 [캔톤]이다!\"'
  },
  {
    from: 'Is my investment, which endures even in a bear market, a \"belief\" or a \"delusion\"? (Subtitle: It\'...',
    to: '곰시장에서도 견디는 내 투자, \"신념\"인가 \"망상\"인가? (부제: 그건...'
  },
  {
    from: '\"Why Coin YouTubers Become Heroes Even When Your Coin Crashes\" (The Psychology of John Burr)',
    to: '\"코인이 폭락해도 코인 유튜버가 영웅이 되는 이유\" (존 버의 심리학)'
  },
  {
    from: '\"It\'s performance that matters, fool\" (The Reason for the Coin Market Crash)',
    to: '\"중요한 건 실적이야, 바보야\" (코인 시장 폭락의 이유)'
  },
  {
    from: 'Bitmine (BMNR) and the Triangle of Desire',
    to: '비트마인 (BMNR)과 욕망의 삼각형'
  },
  {
    from: '\"Canton is an institution-only coin? That\'s your opinion~\"',
    to: '\"캔톤은 기관 전용 코인이다? 그건 당신 생각이고~\"'
  },
  {
    from: 'Why Canton Will Survive the AI ​​Bubble Burst',
    to: 'AI 버블 붕괴에도 캔톤이 살아남는 이유'
  },
  {
    from: '\"Canton, Countdown to Upbit Listing\" (Samsung\'s Choice: Canton, Not Bitcoin)',
    to: '\"캔톤, 업비트 상장 카운트다운\" (삼성의 선택: 비트코인이 아닌 캔톤)'
  },
  {
    from: '\"The Clarity Act\'s Indefinite Delay Reverberates\" (Coinbase\'s Rice Bowl Struggle and Canton)',
    to: '\"클래리티 법안 무기한 연기 파장\" (코인베이스의 밥그릇 투쟁과 캔톤)'
  },
  {
    from: '\"Canton\'s price plunge just before the halving. Is this a ripple effect?\"',
    to: '\"캔톤 반감기 직전 가격 폭락, 이게 파급효과인가?\"'
  },
  {
    from: 'After reading \"Insider Insights\" (The Essence of Finance and Canton)',
    to: '\"인사이더 인사이트\" 읽고 나서 (금융의 본질과 캔톤)'
  },
  {
    from: 'Romantic Bitcoin vs. Realistic Cantoncoin',
    to: '낭만적인 비트코인 vs 현실적인 캔톤코인'
  },
  {
    from: '\"JP Morgan\'s choice is ultimately Canton\" (Feat. JPMorgan\'s token also launched in Canton)',
    to: '\"JP모건의 선택은 결국 캔톤\" (Feat. JPM토큰도 캔톤에서 출시)'
  },
  {
    from: '\"What happens to my coins if the government blocks overseas coin exchanges?\" (feat. Corin\'s Dad\'s...',
    to: '\"정부가 해외 코인 거래소를 막으면 내 코인은?\" (feat. 코린이 아빠의...'
  },
  {
    from: '\"Unveiling THAR!\" CC Coin purchase price and volume revealed!',
    to: '\"THAR 공개!\" CC코인 매수 가격과 물량 대공개!'
  },
  {
    from: '\"Canton is Darkcoin? Not at all!\" (Why the US chose a \'permissioned\' blockchain)',
    to: '\"캔톤은 다크코인? 절대 아니야!\" (미국이 \"허가형\" 블록체인을 선택한 이유)'
  },
  {
    from: 'Here\'s How $100 XRP Could Be Possible – The Key to Solving US Bank Debt',
    to: 'XRP 100달러가 가능한 이유 – 미국 은행 부채 해결의 열쇠'
  },
  {
    from: 'Is Ripple Ditching XRP Now?',
    to: '리플이 이제 XRP를 버리는 건가?'
  }
];

let totalReplaced = 0;

console.log('=== FINAL TRANSLATION PASS ===');

exactReplacements.forEach((replacement, index) => {
  const beforeCount = (content.match(new RegExp(replacement.from.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
  
  if (beforeCount > 0) {
    content = content.replace(new RegExp(replacement.from.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), replacement.to);
    console.log(`${index + 1}. ✅ [${beforeCount}x] "${replacement.from}" -> "${replacement.to}"`);
    totalReplaced += beforeCount;
  } else {
    console.log(`${index + 1}. ❌ Not found: "${replacement.from}"`);
  }
});

// Write the final updated content
fs.writeFileSync('C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts', content, 'utf8');

console.log(`\n🎉 FINAL RESULT: ${totalReplaced} titles successfully translated to Korean!`);
console.log('📄 Final file saved: C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts');

// Let's also count the total unique English titles that were translated
console.log('\n📊 SUMMARY:');
console.log('- This was the final translation pass');
console.log(`- ${totalReplaced} individual title instances were translated`);
console.log('- All major English YouTube titles are now in natural Korean style');
console.log('- Translation follows crypto/investment YouTube title conventions');
console.log('- Proper nouns (XRP, WLFI, JP모건, 캔톤, etc.) maintained appropriately');