const fs = require('fs');

// Read current coingecko.ts
let src = fs.readFileSync('src/lib/api/coingecko.ts', 'utf8');

// New comprehensive mapping
const newMapping = `// 코인 심볼 -> CoinGecko ID 매핑
export const COIN_MAPPING: Record<string, string> = {
  // 크립토
  'XRP': 'ripple',
  '리플 (XRP)': 'ripple',
  '이더리움': 'ethereum',
  'ETH': 'ethereum',
  '비트코인': 'bitcoin',
  'BTC': 'bitcoin',
  '캔톤네트워크 (CC)': 'canton-network',
  '캐톤네트워크 (CC)': 'canton-network',
  'CC': 'canton-network',
  'BNB': 'binancecoin',
  '솔라나': 'solana',
  'SOL': 'solana',
  '체인링크': 'chainlink',
  '모네로': 'monero',
  '월드코인': 'worldcoin-wld',
  '퍼지펭귄 (PENGU)': 'pudgy-penguins',
  'PENGU': 'pudgy-penguins',
  '이더질라 (ATNF)': '',
  // 주식 (CoinGecko 미지원)
  '마이크로스트래티지 (MSTR)': '',
  '마이크로스트레티지 (MSTR)': '',
  'MSTR': '',
  '엔비디아': '',
  '엔비디아 (NVDA)': '',
  'NVDA': '',
  '팔란티어 (PLTR)': '',
  'PLTR': '',
  '구글 (GOOGL)': '',
  'GOOGL': '',
  '알파벳': '',
  'SBI': '',
  'SBI 홀딩스': '',
  'SK': '',
  '삼성ENA': '',
  '오뚜기': '',
  '율촌화학': '',
  '라이나스 희토류': '',
  '코스피': '',
  '캔톤 스트레티지 홀딩스 (CNTN)': '',
  'CNTN': '',
  '코인베이스 (COIN)': '',
  'COIN': '',
  '타르 (THAR)': '',
  'THAR': '',
  '비트마인 (BMNR)': '',
  'BMNR': '',
  '블리시': '',
  '샤프링크': '',
  // 카테고리 (가격 추적 불가)
  '알트코인': '',
  '스테이블코인': '',
  '암호화폐': '',
  '기술주': '',
  '미국 주식': '',
  '금': '',
  '서클 (Circle)': '',
  '월드리버티파이낸셜 (WLFI)': '',
  'WLFI': '',
  '오픈AI (ChatGPT)': '',
};`;

// Replace old mapping
const start = src.indexOf('// 코인 심볼 -> CoinGecko ID 매핑');
const end = src.indexOf('};', start) + 2;
src = src.substring(0, start) + newMapping + src.substring(end);

fs.writeFileSync('src/lib/api/coingecko.ts', src, 'utf8');
console.log('COIN_MAPPING updated');
