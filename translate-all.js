const fs = require('fs');
const path = 'C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts';
const c = fs.readFileSync(path, 'utf8');

const arrStart = c.indexOf('export const corinpapaSignals: CorinpapaSignal[] = [');
const statsStart = c.indexOf('export const corinpapaStats');
const header = c.substring(0, arrStart);
const arrStr = c.substring(arrStart + 'export const corinpapaSignals: CorinpapaSignal[] = '.length, statsStart).trim();
const lastBracket = arrStr.lastIndexOf(']');
const signals = JSON.parse(arrStr.substring(0, lastBracket + 1));
const footer = c.substring(statsStart);

const map = {
  '"Decision to Part with XRP (WLFI Mar-a-Lago Forum Impact)"': '"XRP와의 이별 결심 (WLFI 마라라고 포럼 충격)"',
  '"Don\'t call me CNTN, from now on it\'s [Canton]!"': '"CNTN이라 부르지 마, 이제부터 [캔톤]이야!"',
  'Is my investment, which endures even in a bear market, a "belief" or a "delusion"? (Subtitle: It\'...': '하락장에서도 버티는 내 투자, "신념"인가 "망상"인가?',
  '"Why Coin YouTubers Become Heroes Even When Your Coin Crashes" (The Psychology of John Burr)': '"코인이 폭락해도 코인 유튜버가 영웅이 되는 이유" (존 버의 심리학)',
  '"It\'s performance that matters, fool" (The Reason for the Coin Market Crash)': '"중요한 건 실적이야, 바보야" (코인 시장 폭락의 이유)',
  '"Canton is an institution-only coin? That\'s your opinion~"': '"캔톤은 기관 전용 코인? 그건 니 생각이고~"',
  'After reading "Insider Insights" (The Essence of Finance and Canton)': '"인사이더 인사이트" 읽고 나서 (금융의 본질과 캔톤)',
  '"Canton, Countdown to Upbit Listing" (Samsung\'s Choice: Canton, Not Bitcoin)': '"캔톤, 업비트 상장 카운트다운" (삼성의 선택: 비트코인이 아닌 캔톤)',
  '"The Clarity Act\'s Indefinite Delay Reverberates" (Coinbase\'s Rice Bowl Struggle and Canton)': '"명확성법 무기한 연기 파장" (코인베이스의 밥그릇 싸움과 캔톤)',
  '"Canton is Darkcoin? Not at all!" (Why the US chose a \'permissioned\' blockchain)': '"캔톤이 다크코인? 천만에!" (미국이 허가형 블록체인을 선택한 이유)',
  '"What happens to my coins if the government blocks overseas coin exchanges?" (feat. Corin\'s Dad\'s...': '"정부가 해외 코인 거래소 막으면 내 코인은?" (feat. 코린이 아빠의...)',
  '"Unveiling THAR!" CC Coin purchase price and volume revealed!': '"THAR 공개!" CC 코인 매수가와 물량 공개!',
  '"JP Morgan\'s choice is ultimately Canton" (Feat. JPMorgan\'s token also launched in Canton)': '"JP모건의 선택은 결국 캔톤" (Feat. JP모건 토큰도 캔톤에서 출시)',
  '"Canton\'s price plunge just before the halving. Is this a ripple effect?"': '"반감기 직전 캔톤 가격 폭락. 연쇄 반응인가?"',
  '"Canton Coin (CC): Why is it crashing when everyone else is rising?" (The reason for the lonely d...': '"캔톤 코인(CC): 다 오르는데 왜 혼자 빠지나?" (외로운 하락의 이유)',
  '"Hey buddy, throw some Ethereum in too" (Is Ethereum the king of RWA?)': '"야 형아, 이더리움도 좀 넣어" (이더리움이 RWA의 왕인가?)',
  '"Brother XRP, get out quick!" (Narrative and Numbers Collapse)': '"형 XRP 빨리 나와!" (내러티브와 숫자의 붕괴)',
  '"Hey buddy, throw your Bitcoins away now" (M2 has already been diverted elsewhere)': '"야 형아, 비트코인 이제 버려" (M2는 이미 다른 곳으로 갔다)',
  '"Is CC Coin and THAR Worth Investing for Individuals?"': '"CC 코인과 THAR, 개인이 투자할 가치가 있나?"',
  '"The Collapse of Investment Patterns and Beliefs (CC Coin\'s Quiet Santa Rally)"': '"투자 패턴과 신념의 붕괴 (CC 코인의 조용한 산타 랠리)"',
  'Monopolizing the $2 trillion RWA market. Introducing the Wall Street tycoon\'s secret "CC Coin" pr...': '2조 달러 RWA 시장 독점. 월가 거물의 비밀 "CC 코인" 프로젝트 공개...',
  '"Why aren\'t Ethereum and Bitcoin going? The culprit is Bitcoin."': '"이더리움과 비트코인 왜 안 가? 범인은 비트코인이야."',
  '"Are Ethereum & Bitcoin (ETH & BMNR) going to explode or crash?"': '"이더리움 & 비트코인(ETH & BMNR) 폭발할까 폭락할까?"',
  '"Ethereum is digital oil? So there\'s no reason for its price to rise!" -feat. Andrew Kang': '"이더리움이 디지털 오일? 그럼 가격 오를 이유가 없다!" -feat. 앤드류 강',
  '"After BMNR\'s severance, Corin\'s father makes excuses."': '"BMNR 손절 후 코린이 아빠의 변명"',
  '"What did Son Jeong-ui hear? As a Corin, I panicked about BMNR."': '"손정의가 뭘 들었길래? 코린이로서 BMNR에 패닉했다."',
  'Is the AI bubble really over? Barry\'s short selling and Son Jeong-ui\'s escape.': 'AI 버블 정말 끝났나? 배리의 공매도와 손정의의 탈출.',
  '"Bitmine Accumulates 3.4 Million Ethereum, I\'m an ETH & BMNR Fanatic"': '"비트마인 이더리움 340만 개 매집, 나는 ETH & BMNR 광신자"',
  '"Buffett is addicted to the past, Son Jeong-ui is addicted to the future. What\'s your investment ...': '"버핏은 과거에 중독, 손정의는 미래에 중독. 당신의 투자는..."',
  '"Sharplink is up… but why is Bitmine (BMNR) stock price like this?"': '"샤프링크는 올랐는데... 비트마인(BMNR) 주가는 왜 이래?"',
};

let count = 0;
for (const s of signals) {
  if (s.videoTitle && map[s.videoTitle]) {
    s.videoTitle = map[s.videoTitle];
    count++;
  }
}
console.log('Translated:', count, 'signals');

// Check remaining English
let remaining = 0;
for (const s of signals) {
  if (!s.videoTitle) continue;
  const ascii = s.videoTitle.replace(/[^a-zA-Z]/g, '').length / s.videoTitle.length;
  if (ascii > 0.5) {
    remaining++;
    console.log('STILL ENG:', s.videoTitle);
  }
}
console.log('Remaining English:', remaining);

const newTs = header + 'export const corinpapaSignals: CorinpapaSignal[] = ' + JSON.stringify(signals, null, 2) + ';\n\n' + footer;
fs.writeFileSync(path, newTs, 'utf8');
console.log('Done');
