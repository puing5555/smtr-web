const fs = require('fs');

// Read the file
const content = fs.readFileSync('C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts', 'utf8');

// Extract the array part between the markers
const arrayStart = content.indexOf('export const corinpapaSignals: CorinpapaSignal[] = [');
const arrayEnd = content.indexOf('];', arrayStart);

if (arrayStart === -1 || arrayEnd === -1) {
  console.log('Could not find array boundaries');
  process.exit(1);
}

const beforeArray = content.slice(0, arrayStart + 'export const corinpapaSignals: CorinpapaSignal[] = ['.length);
const afterArray = content.slice(arrayEnd);

// Extract and parse the array content 
const arrayContent = content.slice(arrayStart + 'export const corinpapaSignals: CorinpapaSignal[] = ['.length, arrayEnd);

// Find all videoTitle entries with regex
const titleRegex = /"videoTitle":\s*"([^"]+)"/g;
const englishTitles = [];
let match;

while ((match = titleRegex.exec(arrayContent)) !== null) {
  const title = match[1];
  
  // Check if title contains English patterns
  const hasEnglish = /[a-z]/.test(title) && (
    /\b(and|or|the|is|of|to|in|for|with|on|at|by|from|up|about|Decision|Part|Impact|Canton|Don't|call|from|now|investment|which|endures|even|bear|market|belief|delusion|Why|Coin|YouTubers|Become|Heroes|Even|When|Your|Crashes|Psychology|performance|matters|fool|Reason|Market|Crash|Triangle|Desire|institution|only|That|your|opinion|Will|Survive|Bubble|Burst|Countdown|Upbit|Listing|Samsung|Choice|Not|Bitcoin|Clarity|Act|Indefinite|Delay|Reverberates|Coinbase|Rice|Bowl|Struggle|price|plunge|just|before|halving|ripple|effect|After|reading|Insider|Insights|Essence|Finance|Romantic|Realistic|Morgan|choice|ultimately|Feat|token|also|launched|What|happens|coins|government|blocks|overseas|exchanges|feat|Unveiling|purchase|volume|revealed|happens|blocks|overseas|Darkcoin|Not|all|chose|permissioned|blockchain|here|could|possible|key|solving|bank|debt|ditching|now)/i.test(title)
  );
  
  if (hasEnglish) {
    englishTitles.push({
      original: title,
      korean: translateTitle(title)
    });
  }
}

// Translation function for crypto/investment YouTube titles
function translateTitle(englishTitle) {
  // Remove quotes and clean up
  let title = englishTitle.replace(/^["']|["']$/g, '').trim();
  
  // Manual translations for the specific titles found
  const translations = {
    'Decision to Part with XRP (WLFI Mar-a-Lago Forum Impact)': '"XRP와의 결별 결정 (WLFI 마라라고 포럼 충격)"',
    'Don\'t call me CNTN, from now on it\'s [Canton]!': '"나를 CNTN이라 부르지 마라, 이제부터는 [캔톤]이다!"',
    'Is my investment, which endures even in a bear market, a "belief" or a "delusion"? (Subtitle: It\'...': '"곰시장에서도 견디는 내 투자, \'신념\'인가 \'망상\'인가? (부제: 그건..."',
    'Why Coin YouTubers Become Heroes Even When Your Coin Crashes" (The Psychology of John Burr)': '"코인이 폭락해도 코인 유튜버가 영웅이 되는 이유" (존 버의 심리학)',
    'It\'s performance that matters, fool" (The Reason for the Coin Market Crash)': '"중요한 건 실적이야, 바보야" (코인 시장 폭락의 이유)',
    'Bitmine (BMNR) and the Triangle of Desire': '비트마인 (BMNR)과 욕망의 삼각형',
    'Canton is an institution-only coin? That\'s your opinion~': '"캔톤은 기관 전용 코인이다? 그건 당신 생각이고~"',
    'Why Canton Will Survive the AI ​​Bubble Burst': 'AI 버블 붕괴에도 캔톤이 살아남는 이유',
    'Canton, Countdown to Upbit Listing" (Samsung\'s Choice: Canton, Not Bitcoin)': '"캔톤, 업비트 상장 카운트다운" (삼성의 선택: 비트코인이 아닌 캔톤)',
    'The Clarity Act\'s Indefinite Delay Reverberates" (Coinbase\'s Rice Bowl Struggle and Canton)': '"클래리티 법안 무기한 연기 파장" (코인베이스의 밥그릇 투쟁과 캔톤)',
    'Canton\'s price plunge just before the halving. Is this a ripple effect?': '"캔톤 반감기 직전 가격 폭락, 이게 파급효과인가?"',
    'After reading "Insider Insights" (The Essence of Finance and Canton)': '"인사이더 인사이트" 읽고 나서 (금융의 본질과 캔톤)',
    'Romantic Bitcoin vs. Realistic Cantoncoin': '낭만적인 비트코인 vs 현실적인 캔톤코인',
    'JP Morgan\'s choice is ultimately Canton" (Feat. JPMorgan\'s token also launched in Canton)': '"JP모건의 선택은 결국 캔톤" (Feat. JPM토큰도 캔톤에서 출시)',
    'What happens to my coins if the government blocks overseas coin exchanges?" (feat. Corin\'s Dad\'s...': '"정부가 해외 코인 거래소를 막으면 내 코인은?" (feat. 코린이 아빠의...',
    'Unveiling THAR!" CC Coin purchase price and volume revealed!': '"THAR 공개!" CC코인 매수 가격과 물량 대공개!',
    'Canton is Darkcoin? Not at all!" (Why the US chose a \'permissioned\' blockchain)': '"캔톤은 다크코인? 절대 아니야!" (미국이 \'허가형\' 블록체인을 선택한 이유)',
    '미국도 희토류 없으면 개털" (미국의 국방, 로봇, 우주 산업 올스톱)': '"미국도 희토류 없으면 개털" (미국의 국방, 로봇, 우주 산업 올스톱)',
    'Here\'s How $100 XRP Could Be Possible – The Key to Solving US Bank Debt': 'XRP 100달러가 가능한 이유 – 미국 은행 부채 해결의 열쇠',
    'Is Ripple Ditching XRP Now?': '리플이 이제 XRP를 버리는 건가?'
  };
  
  return translations[title] || `"${title}"`;
}

console.log(`Found ${englishTitles.length} English titles to translate:`);
console.log('\n=== TRANSLATIONS ===');

// Replace titles in the content
let updatedContent = content;
let translationCount = 0;

englishTitles.forEach((item, index) => {
  console.log(`${index + 1}. "${item.original}" -> ${item.korean}`);
  
  // Replace the exact title in the content
  const searchPattern = `"videoTitle": "${item.original}"`;
  const replacement = `"videoTitle": ${item.korean}`;
  
  if (updatedContent.includes(searchPattern)) {
    updatedContent = updatedContent.replace(searchPattern, replacement);
    translationCount++;
  }
});

// Write the updated content back to the file
fs.writeFileSync('C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts', updatedContent, 'utf8');

console.log(`\n✅ Translation complete! ${translationCount} titles were translated and saved.`);