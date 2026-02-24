const fs = require('fs');
const path = 'C:/Users/Mario/work/invest-sns/src/data/corinpapa-signals.ts';
let c = fs.readFileSync(path, 'utf8');

// Use line-by-line approach: find all "videoTitle": lines and fix them
const lines = c.split('\n');
const translations = {
  'Decision to Part with XRP': 'XRP와의 이별 결심 (WLFI 마라라고 포럼 충격)',
  "Don't call me CNTN": 'CNTN이라 부르지 마, 이제부터 캔톤이야!',
  'Is my investment, which endures': '하락장에서도 버티는 내 투자, 신념인가 망상인가?',
  'Why Coin YouTubers Become Heroes': '코인이 폭락해도 코인 유튜버가 영웅이 되는 이유 (존 버의 심리학)',
  "It's performance that matters": '중요한 건 실적이야, 바보야 (코인 시장 폭락의 이유)',
  'Canton is an institution-only': '캔톤은 기관 전용 코인? 그건 니 생각이고~',
  'After reading': '인사이더 인사이트 읽고 나서 (금융의 본질과 캔톤)',
  'Canton, Countdown to Upbit': '캔톤, 업비트 상장 카운트다운 (삼성의 선택: 비트코인이 아닌 캔톤)',
  "Clarity Act's Indefinite": '명확성법 무기한 연기 파장 (코인베이스의 밥그릇 싸움과 캔톤)',
  'Canton is Darkcoin': '캔톤이 다크코인? 천만에! (미국이 허가형 블록체인을 선택한 이유)',
  'What happens to my coins if': '정부가 해외 코인 거래소 막으면 내 코인은?',
  'Unveiling THAR': 'THAR 공개! CC 코인 매수가와 물량 공개!',
  "JP Morgan's choice": 'JP모건의 선택은 결국 캔톤 (JP모건 토큰도 캔톤에서 출시)',
  "Canton's price plunge": '반감기 직전 캔톤 가격 폭락. 연쇄 반응인가?',
  'Canton Coin (CC): Why is it crashing': '캔톤 코인(CC): 다 오르는데 왜 혼자 빠지나?',
  'Hey buddy, throw some Ethereum': '야 형아, 이더리움도 좀 넣어 (이더리움이 RWA의 왕인가?)',
  'Brother XRP, get out quick': '형 XRP 빨리 나와! (내러티브와 숫자의 붕괴)',
  'Hey buddy, throw your Bitcoins': '야 형아, 비트코인 이제 버려 (M2는 이미 다른 곳으로 갔다)',
  'Is CC Coin and THAR Worth': 'CC 코인과 THAR, 개인이 투자할 가치가 있나?',
  'Collapse of Investment Patterns': '투자 패턴과 신념의 붕괴 (CC 코인의 조용한 산타 랠리)',
  'Monopolizing the': '2조 달러 RWA 시장 독점. 월가 거물의 비밀 CC 코인 프로젝트 공개',
  "Why aren't Ethereum and Bitcoin going": '이더리움과 비트코인 왜 안 가? 범인은 비트코인이야.',
  'Are Ethereum & Bitcoin': '이더리움 & 비트코인(ETH & BMNR) 폭발할까 폭락할까?',
  'Ethereum is digital oil': '이더리움이 디지털 오일? 그럼 가격 오를 이유가 없다! -feat. 앤드류 강',
  "After BMNR's severance": 'BMNR 손절 후 코린이 아빠의 변명',
  'What did Son Jeong-ui hear': '손정의가 뭘 들었길래? 코린이로서 BMNR에 패닉했다.',
  'Is the AI bubble really over': 'AI 버블 정말 끝났나? 배리의 공매도와 손정의의 탈출.',
  'Bitmine Accumulates 3.4 Million': '비트마인 이더리움 340만 개 매집, 나는 ETH & BMNR 광신자',
  'Buffett is addicted to the past': '버핏은 과거에 중독, 손정의는 미래에 중독. 당신의 투자는...',
  'Sharplink is up': '샤프링크는 올랐는데... 비트마인(BMNR) 주가는 왜 이래?',
  // Additional ones that might have been from subagent with quotes inside
  '인사이더 인사이트': null, // already Korean, skip
};

let count = 0;
for (let i = 0; i < lines.length; i++) {
  const match = lines[i].match(/^\s*"videoTitle":\s*"(.*)"\s*,?\s*$/);
  if (!match) continue;
  const title = match[1].replace(/\\"/g, '"');
  
  // Check if it's mostly English
  const asciiLetters = title.replace(/[^a-zA-Z]/g, '').length;
  const totalChars = title.replace(/\s/g, '').length;
  if (totalChars === 0 || asciiLetters / totalChars < 0.4) continue; // Already Korean
  
  // Find matching translation
  let translated = null;
  for (const [key, val] of Object.entries(translations)) {
    if (val && title.includes(key)) {
      translated = val;
      break;
    }
  }
  
  if (translated) {
    lines[i] = lines[i].replace(/"videoTitle":\s*".*"/, `"videoTitle": "${translated}"`);
    count++;
  }
}

fs.writeFileSync(path, lines.join('\n'), 'utf8');
console.log('Translated', count, 'title lines');

// Verify: count remaining English titles
let remaining = 0;
for (const line of lines) {
  const m = line.match(/"videoTitle":\s*"(.*)"/);
  if (!m) continue;
  const t = m[1];
  const asc = t.replace(/[^a-zA-Z]/g, '').length;
  const tot = t.replace(/\s/g, '').length;
  if (tot > 0 && asc / tot > 0.5) {
    remaining++;
    console.log('STILL:', t.substring(0, 60));
  }
}
console.log('Remaining English:', remaining);
