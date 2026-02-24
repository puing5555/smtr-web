const fs = require('fs');

// Read the current file
let content = fs.readFileSync('C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts', 'utf8');

// Direct replacements for the specific quoted titles that need fixing
const quotedTitleReplacements = [
  {
    search: '"Decision to Part with XRP (WLFI Mar-a-Lago Forum Impact)"',
    replace: '"XRP와의 결별 결정 (WLFI 마라라고 포럼 충격)"'
  },
  {
    search: '"Don\'t call me CNTN, from now on it\'s [Canton]!"',
    replace: '"나를 CNTN이라 부르지 마라, 이제부터는 [캔톤]이다!"'
  },
  {
    search: '"Why Coin YouTubers Become Heroes Even When Your Coin Crashes" (The Psychology of John Burr)',
    replace: '"코인이 폭락해도 코인 유튜버가 영웅이 되는 이유" (존 버의 심리학)'
  },
  {
    search: '"It\'s performance that matters, fool" (The Reason for the Coin Market Crash)',
    replace: '"중요한 건 실적이야, 바보야" (코인 시장 폭락의 이유)'
  },
  {
    search: '"Canton is an institution-only coin? That\'s your opinion~"',
    replace: '"캔톤은 기관 전용 코인이다? 그건 당신 생각이고~"'
  },
  {
    search: '"Canton, Countdown to Upbit Listing" (Samsung\'s Choice: Canton, Not Bitcoin)',
    replace: '"캔톤, 업비트 상장 카운트다운" (삼성의 선택: 비트코인이 아닌 캔톤)'
  },
  {
    search: '"The Clarity Act\'s Indefinite Delay Reverberates" (Coinbase\'s Rice Bowl Struggle and Canton)',
    replace: '"클래리티 법안 무기한 연기 파장" (코인베이스의 밥그릇 투쟁과 캔톤)'
  },
  {
    search: '"Canton is Darkcoin? Not at all!" (Why the US chose a \'permissioned\' blockchain)',
    replace: '"캔톤은 다크코인? 절대 아니야!" (미국이 "허가형" 블록체인을 선택한 이유)'
  },
  {
    search: '"What happens to my coins if the government blocks overseas coin exchanges?" (feat. Corin\'s Dad\'s...',
    replace: '"정부가 해외 코인 거래소를 막으면 내 코인은?" (feat. 코린이 아빠의...'
  },
  {
    search: '"Unveiling THAR!" CC Coin purchase price and volume revealed!',
    replace: '"THAR 공개!" CC코인 매수 가격과 물량 대공개!'
  },
  {
    search: '"JP Morgan\'s choice is ultimately Canton" (Feat. JPMorgan\'s token also launched in Canton)',
    replace: '"JP모건의 선택은 결국 캔톤" (Feat. JPM토큰도 캔톤에서 출시)'
  },
  {
    search: '"Canton\'s price plunge just before the halving. Is this a ripple effect?"',
    replace: '"캔톤 반감기 직전 가격 폭락, 이게 파급효과인가?"'
  },
  {
    search: 'Is my investment, which endures even in a bear market, a "belief" or a "delusion"? (Subtitle: It\'...',
    replace: '곰시장에서도 견디는 내 투자, "신념"인가 "망상"인가? (부제: 그건...'
  },
  {
    search: 'After reading "Insider Insights" (The Essence of Finance and Canton)',
    replace: '"인사이더 인사이트" 읽고 나서 (금융의 본질과 캔톤)'
  },
  {
    search: 'Bitmine (BMNR) and the Triangle of Desire',
    replace: '비트마인 (BMNR)과 욕망의 삼각형'
  },
  {
    search: 'Why Canton Will Survive the AI ​​Bubble Burst',
    replace: 'AI 버블 붕괴에도 캔톤이 살아남는 이유'
  },
  {
    search: 'Romantic Bitcoin vs. Realistic Cantoncoin',
    replace: '낭만적인 비트코인 vs 현실적인 캔톤코인'
  },
  {
    search: 'Here\'s How $100 XRP Could Be Possible – The Key to Solving US Bank Debt',
    replace: 'XRP 100달러가 가능한 이유 – 미국 은행 부채 해결의 열쇠'
  },
  {
    search: 'Is Ripple Ditching XRP Now?',
    replace: '리플이 이제 XRP를 버리는 건가?'
  },
  {
    search: '"Sharplink is up… but why is Bitmine (BMNR) stock price like this?"',
    replace: '"샤프링크는 오르는데… 비트마인 (BMNR) 주가는 왜 이 모양?"'
  }
];

let replacedCount = 0;

console.log('=== FIXING QUOTED TITLES ===');

quotedTitleReplacements.forEach((replacement, index) => {
  const searchPattern = `"videoTitle": "${replacement.search}"`;
  const replacePattern = `"videoTitle": "${replacement.replace}"`;
  
  if (content.includes(searchPattern)) {
    content = content.replace(new RegExp(searchPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), replacePattern);
    console.log(`${index + 1}. ✅ "${replacement.search}" -> "${replacement.replace}"`);
    replacedCount++;
  } else {
    console.log(`${index + 1}. ❌ Not found: "${replacement.search}"`);
  }
});

// Additional cleanup for any remaining titles with common patterns
const additionalReplacements = [
  {
    from: 'Canton Coin (CC): Why is it crashing when everyone else is rising?\" (The reason for the lonely d...',
    to: '캔톤코인 (CC): 모두 오르는데 왜 혼자 폭락하나? (외톨이 하락의 이유)'
  },
  {
    from: 'Hey buddy, throw some Ethereum in too\" (Is Ethereum the king of RWA?)',
    to: '친구야, 이더리움도 던져\" (이더리움이 RWA의 왕인가?)'
  },
  {
    from: 'Brother XRP, get out quick!\" (Narrative and Numbers Collapse)',
    to: 'XRP 형님, 빨리 탈출하세요!\" (서사와 숫자의 붕괴)'
  },
  {
    from: 'Hey buddy, throw your Bitcoins away now\" (M2 has already been diverted elsewhere)',
    to: '친구야, 비트코인 이제 던져\" (M2는 이미 다른 곳으로 쏠림)'
  }
];

additionalReplacements.forEach((replacement, index) => {
  const searchPattern = `"videoTitle": "${replacement.from}"`;
  const replacePattern = `"videoTitle": "${replacement.to}"`;
  
  if (content.includes(searchPattern)) {
    content = content.replace(searchPattern, replacePattern);
    console.log(`${quotedTitleReplacements.length + index + 1}. ✅ Additional: "${replacement.from}" -> "${replacement.to}"`);
    replacedCount++;
  }
});

// Write the updated content
fs.writeFileSync('C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts', content, 'utf8');

console.log(`\n🎉 Final cleanup complete! ${replacedCount} additional titles were translated.`);
console.log('📄 File saved: C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts');