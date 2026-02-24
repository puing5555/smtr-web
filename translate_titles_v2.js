const fs = require('fs');

// Read the file
const content = fs.readFileSync('C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts', 'utf8');

// Find all videoTitle entries more precisely 
const titleRegex = /"videoTitle": "([^"\\]*(\\.[^"\\]*)*)"/g;
const allTitles = [];
let match;

while ((match = titleRegex.exec(content)) !== null) {
  allTitles.push(match[1]);
}

// Filter for English titles
const englishTitles = allTitles.filter(title => {
  return /[a-z]/.test(title) && (
    /\b(Decision|Part|XRP|WLFI|Mar-a-Lago|Forum|Impact|Don't|call|me|CNTN|from|now|on|it's|Canton|Is|my|investment|which|endures|even|in|a|bear|market|belief|delusion|Subtitle|It|Why|Coin|YouTubers|Become|Heroes|Even|When|Your|Crashes|Psychology|John|Burr|performance|that|matters|fool|The|Reason|for|the|Market|Crash|Bitmine|BMNR|and|Triangle|of|Desire|institution|only|coin|That|your|opinion|Will|Survive|AI|Bubble|Burst|Countdown|to|Upbit|Listing|Samsung|Choice|Not|Bitcoin|Clarity|Act|Indefinite|Delay|Reverberates|Coinbase|Rice|Bowl|Struggle|price|plunge|just|before|halving|ripple|effect|After|reading|Insider|Insights|Essence|Finance|Romantic|vs|Realistic|Cantoncoin|JP|Morgan|choice|is|ultimately|Feat|JPMorgan|token|also|launched|What|happens|coins|if|government|blocks|overseas|exchanges|feat|Corin|Dad|Unveiling|THAR|CC|purchase|volume|revealed|Darkcoin|Not|at|all|US|chose|permissioned|blockchain|Here|How|100|Could|Be|Possible|Key|Solving|Bank|Debt|Ripple|Ditching|Now)/i.test(title)
  );
});

// Enhanced translation mapping for crypto/investment YouTube titles
function getKoreanTranslation(englishTitle) {
  const translations = {
    // Exact matches
    '"Decision to Part with XRP (WLFI Mar-a-Lago Forum Impact)"': '"XRP와의 결별 결정 (WLFI 마라라고 포럼 충격)"',
    '"Don\'t call me CNTN, from now on it\'s [Canton]!"': '"나를 CNTN이라 부르지 마라, 이제부터는 [캔톤]이다!"',
    'Is my investment, which endures even in a bear market, a "belief" or a "delusion"? (Subtitle: It\'...': '곰시장에서도 견디는 내 투자, "신념"인가 "망상"인가? (부제: 그건...',
    '"Why Coin YouTubers Become Heroes Even When Your Coin Crashes" (The Psychology of John Burr)': '"코인이 폭락해도 코인 유튜버가 영웅이 되는 이유" (존 버의 심리학)',
    '"It\'s performance that matters, fool" (The Reason for the Coin Market Crash)': '"중요한 건 실적이야, 바보야" (코인 시장 폭락의 이유)',
    'Bitmine (BMNR) and the Triangle of Desire': '비트마인 (BMNR)과 욕망의 삼각형',
    '"Canton is an institution-only coin? That\'s your opinion~"': '"캔톤은 기관 전용 코인이다? 그건 당신 생각이고~"',
    'Why Canton Will Survive the AI ​​Bubble Burst': 'AI 버블 붕괴에도 캔톤이 살아남는 이유',
    '"Canton, Countdown to Upbit Listing" (Samsung\'s Choice: Canton, Not Bitcoin)': '"캔톤, 업비트 상장 카운트다운" (삼성의 선택: 비트코인이 아닌 캔톤)',
    '"The Clarity Act\'s Indefinite Delay Reverberates" (Coinbase\'s Rice Bowl Struggle and Canton)': '"클래리티 법안 무기한 연기 파장" (코인베이스의 밥그릇 투쟁과 캔톤)',
    '"Canton\'s price plunge just before the halving. Is this a ripple effect?"': '"캔톤 반감기 직전 가격 폭락, 이게 파급효과인가?"',
    'After reading "Insider Insights" (The Essence of Finance and Canton)': '"인사이더 인사이트" 읽고 나서 (금융의 본질과 캔톤)',
    'Romantic Bitcoin vs. Realistic Cantoncoin': '낭만적인 비트코인 vs 현실적인 캔톤코인',
    '"JP Morgan\'s choice is ultimately Canton" (Feat. JPMorgan\'s token also launched in Canton)': '"JP모건의 선택은 결국 캔톤" (Feat. JPM토큰도 캔톤에서 출시)',
    '"What happens to my coins if the government blocks overseas coin exchanges?" (feat. Corin\'s Dad\'s...': '"정부가 해외 코인 거래소를 막으면 내 코인은?" (feat. 코린이 아빠의...',
    '"Unveiling THAR!" CC Coin purchase price and volume revealed!': '"THAR 공개!" CC코인 매수 가격과 물량 대공개!',
    '"Canton is Darkcoin? Not at all!" (Why the US chose a \'permissioned\' blockchain)': '"캔톤은 다크코인? 절대 아니야!" (미국이 "허가형" 블록체인을 선택한 이유)',
    'Here\'s How $100 XRP Could Be Possible – The Key to Solving US Bank Debt': 'XRP 100달러가 가능한 이유 – 미국 은행 부채 해결의 열쇠',
    'Is Ripple Ditching XRP Now?': '리플이 이제 XRP를 버리는 건가?',
    
    // Additional translations for other found titles
    'Are Bitcoin and Ethereum the ultimate collateral assets? (I don\'t know much about RWA.)': '비트코인과 이더리움이 최고의 담보 자산일까? (RWA를 잘 모르겠어요.)',
    'The altcoin extinction of 2026 begins. (Here\'s the inconvenient truth!)': '2026년 알트코인 대멸종이 시작된다. (불편한 진실은 이겁니다!)',
    'Why I Climb Canton (CC) Alone and Why I Published a Book on Amazon (Feat. Tymune)': '내가 혼자 캔톤 (CC)을 올라타는 이유와 아마존에 책을 출간한 이유 (Feat. 타이뮤)',
    'Causes of SVB\'s Bankruptcy and the Need for Canton': 'SVB 파산의 원인과 캔톤의 필요성',
    'The World\'s Easiest RWA Explained (With Real Estate Transactions as an Example)': '세상에서 가장 쉬운 RWA 설명 (부동산 거래를 예시로)',
    'Etherzilla Sells Ethereum and Implements RWA? Peter Thiel\'s Proof of a Fraudulent Transaction': '비탈릭이 이더리움을 팔고 RWA 도입? 피터 틸의 사기 거래 증거',
    'THAR, Tymune\'s secretive strategy. Why is the stock price stagnant?': 'THAR, 타이뮤의 은밀한 전략. 주가는 왜 제자리일까?',
    'US Treasury bonds rise above Canton (a clear signal of full-scale operation in 2026)': '미국 국채가 캔톤 위로 상승 (2026년 본격 가동의 명확한 신호)',
    'CC Coin Exclusive Strategy - feat. Zero to One': 'CC코인 독점 전략 - feat. 제로 투 원',
    'Why Monopolies Lie': '독점기업이 거짓말하는 이유',
    'Canton Coin (CC), the secret behind the explosive amount of burn. (Absolutely no impulse buying!)': '캔톤코인 (CC), 폭발적 소각량 뒤의 비밀. (절대 충동매수 금지!)',
    'Canton Network and Wall Street\'s Big Picture: Creating Their Own Deflationary Currency?': '캔톤 네트워크와 월스트리트의 큰 그림: 자체 디플레이션 화폐 만들기?',
    'Why is Canton Network\'s ticker CC? Canton\'s ambitions revealed through AlchemyPay News.': '캔톤 네트워크의 티커가 CC인 이유는? 알케미페이 뉴스로 드러난 캔톤의 야심.',
    'Why Cantoncoin (CC) Listed During November\'s Fear Zone': '11월 공포 구간에 캔톤코인 (CC)이 상장한 이유',
    'Why Cashwood Invested in THAR, a Zackcoin Collecting Company': '캐시우드가 잭코인 수집회사 THAR에 투자한 이유',
    'CC Coin (Canton Network Coin) is a scam?': 'CC코인 (캔톤 네트워크 코인)이 사기인가?',
    'The counterattack of giants begins a tectonic shift in the crypto market.': '거인들의 반격이 암호화폐 시장의 지각 변동을 시작한다.',
    'Monopolizing the $2 trillion RWA market. Introducing the Wall Street tycoon\'s secret ': '2조 달러 RWA 시장 독점. 월스트리트 거물의 비밀 무기 공개',
    'A must-watch before investing in CC Coin! This is CC Coin\'s fatal weakness.': 'CC코인 투자 전 필수 시청! CC코인의 치명적 약점이 바로 이거다.',
    'BMNR Breaking News - The Real Implications of Peter Thiel\'s Sale and CEO Change': 'BMNR 속보 - 피터 틸의 매도와 CEO 교체의 진짜 의미',
    'Is the AI bubble really over? Barry\'s short selling and Son Jeong-ui\'s escape.': 'AI 버블이 정말 끝났나? 배리의 공매도와 손정의의 탈출.',
    'The global M2 myth is over. Bitcoin is tied to the dollar.': '글로벌 M2 신화는 끝났다. 비트코인은 달러에 묶였다.',
    'Is the Ethereum crash due to a hack?': '이더리움 폭락이 해킹 때문인가?',
    'Is Ethereum finally finished? Goodbye, departing holders!': '이더리움이 드디어 끝났나? 떠나는 홀더들아 안녕!',
    'Between Cool and Passion – What Does Ethereum Mean to You?': '쿨함과 열정 사이 – 당신에게 이더리움은 무엇인가?',
    'Ethereum Unstaking for 57 Days? Is This a Sign of a Crash?': '이더리움 57일째 언스테이킹? 폭락 신호인가?',
    'Peter Thiel Swallows Memecoin – The Secret of Fuzzy Penguin': '피터 틸이 밈코인을 삼키다 – 퍼지펭귄의 비밀',
    'Why the National Pension Service Can\'t Hold Bitcoin (BMNR)': '국민연금이 비트코인 (BMNR)을 보유할 수 없는 이유',
    'Is Peter Thiel investing in the next Bitcoin? What is Etherzilla (ATNF)?': '피터 틸이 다음 비트코인에 투자하나? 이더질라 (ATNF)란 무엇?',
    'Bitcoin (BMNR) & Sharplink \'Wave Riding\' Warning!': '비트마인 (BMNR) & 샤프링크 "파도타기" 경고!',
    '"Sharplink is up… but why is Bitmine (BMNR) stock price like this?"': '"샤프링크는 오르는데… 비트마인 (BMNR) 주가는 왜 이 모양?"',
    'Why I Sold 100% of My XRP and Invested in Ripple': '내가 XRP 100% 매도하고 리플에 투자한 이유',
    'The Big Picture of Bitmine (BMNR) and Peter Thiel': '비트마인 (BMNR)과 피터 틸의 큰 그림',
    'Bitcoin to Become Ethereum\'s Safe – Why Peter Thiel Chose It': '비트코인이 이더리움의 금고가 되다 – 피터 틸이 선택한 이유',
    'The Inconvenient Truth for Those Who Believe in XRP': 'XRP를 믿는 자들을 위한 불편한 진실',
    'Bitmine vs. Sharplink: Who Will Win the Ethereum Accumulation War?': '비트마인 vs 샤프링크: 이더리움 쌓기 전쟁에서 누가 이길까?',
    'Is Ethereum Staking Just Interest?': '이더리움 스테이킹은 단순 이자일까?',
    'Cashwood finally got his hands on Bitmine! (Is he really a Tenberger?)': '캐시우드가 드디어 비트마인에 손을 댔다! (정말 텐버거 맞나?)',
    'Is Peter Thiel Behind Ethereum? (Part 3 of the Passage of the Crypto 3 Laws)': '피터 틸이 이더리움 배후에? (암호화폐 3법 통과 3부)',
    'Will XRP continue to surge after the US House of Representatives passes the three crypto bills?': '미 하원 암호화폐 3법 통과 후 XRP 계속 급등할까?',
    'Trump\'s Sons Are Serious About Ethereum (Part 2 of Celebrating the Passage of the Crypto 3 Laws)': '트럼프 아들들이 이더리움에 진심이다 (암호화폐 3법 통과 축하 2부)'
  };

  return translations[englishTitle] || englishTitle;
}

console.log(`Found ${englishTitles.length} unique English titles:`);

// Remove duplicates and sort
const uniqueEnglishTitles = [...new Set(englishTitles)];

console.log('\n=== ENGLISH TITLES TO TRANSLATE ===');
uniqueEnglishTitles.forEach((title, index) => {
  console.log(`${index + 1}. "${title}"`);
});

// Replace titles in content
let updatedContent = content;
let translationCount = 0;

console.log('\n=== TRANSLATIONS ===');
uniqueEnglishTitles.forEach((englishTitle, index) => {
  const koreanTitle = getKoreanTranslation(englishTitle);
  
  if (koreanTitle !== englishTitle) {
    console.log(`${index + 1}. "${englishTitle}" -> ${koreanTitle}`);
    
    // Replace exact match in content
    const searchPattern = `"videoTitle": "${englishTitle}"`;
    const replacement = `"videoTitle": "${koreanTitle}"`;
    
    const beforeCount = (updatedContent.match(new RegExp(searchPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
    updatedContent = updatedContent.replace(new RegExp(searchPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), replacement);
    const afterCount = (updatedContent.match(new RegExp(replacement.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
    
    if (beforeCount > 0) {
      translationCount += beforeCount;
    }
  }
});

// Write updated content back
fs.writeFileSync('C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts', updatedContent, 'utf8');

console.log(`\n✅ Translation complete! ${translationCount} titles were successfully translated and saved.`);
console.log(`📄 Updated file: C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts`);