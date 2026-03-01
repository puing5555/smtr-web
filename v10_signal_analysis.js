const fs = require('fs');

// 데이터 로드
const signalsData = JSON.parse(fs.readFileSync('signals_data.json', 'utf8'));

console.log('=== V10 프롬프트 규칙 위반 분석 ===');

const issues = [];

// 규칙 1: 논거 vs 결론 - 논거인데 매수로 분류된 것 검토
console.log('\n🔍 규칙 1: 논거 vs 결론 검토');
const argumentSignals = signalsData.filter(s => s.mention_type === '논거' && s.signal === '매수');
if (argumentSignals.length > 0) {
  console.log(`❌ 논거인데 매수로 분류된 시그널: ${argumentSignals.length}개`);
  argumentSignals.forEach(s => {
    console.log(`- ID: ${s.id}, 종목: ${s.stock}, 화자: ${s.speakers?.name}`);
    console.log(`  key_quote: ${s.key_quote}`);
    console.log(`  reasoning: ${s.reasoning.substring(0, 100)}...`);
    issues.push({
      id: s.id,
      stock: s.stock,
      speaker: s.speakers?.name,
      issue: '규칙1 위반: 논거인데 매수 분류',
      current: `${s.signal} (${s.mention_type})`,
      suggested: '긍정 (논거)'
    });
  });
} else {
  console.log('✅ 논거→매수 분류 문제 없음');
}

// 규칙 3: 전망 vs 권유 - "~다/된다/보인다" 패턴인데 매수로 분류된 것
console.log('\n🔍 규칙 3: 전망 vs 권유 검토');
const prospectPatterns = /이다$|된다$|보인다$|전망이다$|예상된다$|가능하다$|갈 수 있다$|수밖에 없다$/;
const prospectBuySignals = signalsData.filter(s => 
  s.signal === '매수' && prospectPatterns.test(s.key_quote)
);
console.log(`⚠️ 전망 표현인데 매수 분류 의심: ${prospectBuySignals.length}개`);
prospectBuySignals.forEach(s => {
  console.log(`- ID: ${s.id}, 종목: ${s.stock}, 화자: ${s.speakers?.name}`);
  console.log(`  key_quote: ${s.key_quote}`);
  issues.push({
    id: s.id,
    stock: s.stock,
    speaker: s.speakers?.name,
    issue: '규칙3 위반: 전망 표현인데 매수 분류',
    current: `${s.signal}`,
    suggested: '긍정'
  });
});

// 규칙 29: 화자 식별 - speaker가 채널명과 같은 경우 (게스트가 있는 영상에서)
console.log('\n🔍 규칙 29: 화자 식별 검토');
// 채널별로 그룹화하여 같은 영상에서 여러 화자가 있는지 확인
const videoSpeakers = {};
signalsData.forEach(s => {
  if (!videoSpeakers[s.video_id]) {
    videoSpeakers[s.video_id] = new Set();
  }
  videoSpeakers[s.video_id].add(s.speakers?.name);
});

const suspiciousSpeakers = signalsData.filter(s => {
  const videoTitle = s.influencer_videos?.title || '';
  const speakerName = s.speakers?.name;
  
  // 영상 제목에 "| 이름" 패턴이 있는데 화자가 다른 경우
  const guestPattern = /\|\s*([가-힣]+(?:\s+[가-힣]+)*)/;
  const titleMatch = videoTitle.match(guestPattern);
  
  if (titleMatch && titleMatch[1] !== speakerName) {
    return true;
  }
  
  // 채널 이름과 화자가 같은지 의심스러운 케이스들
  const channelKeywords = ['TV', '채널', '뉴스', '증권'];
  if (channelKeywords.some(keyword => speakerName?.includes(keyword))) {
    return true;
  }
  
  return false;
});

console.log(`⚠️ 화자 식별 의심: ${suspiciousSpeakers.length}개`);
suspiciousSpeakers.forEach(s => {
  console.log(`- ID: ${s.id}, 종목: ${s.stock}, 화자: ${s.speakers?.name}`);
  console.log(`  영상: ${s.influencer_videos?.title}`);
  issues.push({
    id: s.id,
    stock: s.stock,
    speaker: s.speakers?.name,
    issue: '규칙29 위반: 화자 식별 의심',
    current: s.speakers?.name,
    suggested: '실제 발언자 확인 필요'
  });
});

// 규칙 30: key_quote 품질 - 종목명 없거나 투자 근거 없거나 15자 미만
console.log('\n🔍 규칙 30: key_quote 품질 검토');
const badKeyQuotes = signalsData.filter(s => {
  const quote = s.key_quote || '';
  const stock = s.stock || '';
  
  // 15자 미만
  if (quote.length < 15) return true;
  
  // 종목명이 없음 (종목명 또는 ticker가 key_quote에 포함되어 있어야 함)
  if (!quote.includes(stock) && !quote.includes(s.ticker)) {
    // 약칭이나 다른 표현도 체크
    const stockVariations = [stock, s.ticker];
    if (stock === 'SK하이닉스') stockVariations.push('하닉스', '하이닉스');
    if (stock === '삼성전자') stockVariations.push('삼전', '삼성');
    if (stock === '엔비디아') stockVariations.push('NVIDIA', 'NVDA');
    
    if (!stockVariations.some(v => quote.includes(v))) {
      return true;
    }
  }
  
  // 투자 근거가 없음 (너무 단순한 표현들)
  const simpleExpressions = ['좋아요', '사세요', '추천', '좋습니다', '괜찮다'];
  if (simpleExpressions.some(expr => quote === expr || quote.endsWith(expr))) {
    return true;
  }
  
  return false;
});

console.log(`❌ 품질 기준 미달 key_quote: ${badKeyQuotes.length}개`);
badKeyQuotes.forEach(s => {
  console.log(`- ID: ${s.id}, 종목: ${s.stock}, 화자: ${s.speakers?.name}`);
  console.log(`  key_quote (${s.key_quote.length}자): "${s.key_quote}"`);
  
  let issueDetail = [];
  if (s.key_quote.length < 15) issueDetail.push('15자 미만');
  if (!s.key_quote.includes(s.stock) && !s.key_quote.includes(s.ticker)) issueDetail.push('종목명 없음');
  
  issues.push({
    id: s.id,
    stock: s.stock,
    speaker: s.speakers?.name,
    issue: `규칙30 위반: ${issueDetail.join(', ')}`,
    current: s.key_quote,
    suggested: '종목명+투자근거+15자 이상으로 수정'
  });
});

// 규칙 5: 교육 - mention_type이 교육인데 시그널이 중립이 아닌 것
console.log('\n🔍 규칙 5: 교육 콘텐츠 검토');
const educationSignals = signalsData.filter(s => s.mention_type === '교육' && s.signal !== '중립');
console.log(`❌ 교육인데 중립이 아닌 시그널: ${educationSignals.length}개`);
educationSignals.forEach(s => {
  console.log(`- ID: ${s.id}, 종목: ${s.stock}, 화자: ${s.speakers?.name}`);
  console.log(`  현재: ${s.signal} (교육), key_quote: ${s.key_quote}`);
  issues.push({
    id: s.id,
    stock: s.stock,
    speaker: s.speakers?.name,
    issue: '규칙5 위반: 교육 콘텐츠인데 투자 시그널 생성',
    current: `${s.signal} (교육)`,
    suggested: '시그널 제외 또는 중립'
  });
});

// 규칙 6: 조건부 - 조건부 표현인데 confidence가 medium 이상인 것
console.log('\n🔍 규칙 6: 조건부 발언 검토');
const conditionalPatterns = /한다면|될 경우|가격대에서|까지는|만약|규제.*통과|원 밑에서|원 위에서/;
const conditionalSignals = signalsData.filter(s => {
  const hasConditionalInQuote = conditionalPatterns.test(s.key_quote);
  const hasConditionalInReasoning = conditionalPatterns.test(s.reasoning);
  const isHighConfidence = ['very_high', 'high'].includes(s.confidence);
  
  return (hasConditionalInQuote || hasConditionalInReasoning) && isHighConfidence;
});

console.log(`❌ 조건부 발언인데 confidence 미하향: ${conditionalSignals.length}개`);
conditionalSignals.forEach(s => {
  console.log(`- ID: ${s.id}, 종목: ${s.stock}, 화자: ${s.speakers?.name}`);
  console.log(`  confidence: ${s.confidence}, key_quote: ${s.key_quote}`);
  issues.push({
    id: s.id,
    stock: s.stock,
    speaker: s.speakers?.name,
    issue: '규칙6 위반: 조건부 발언인데 confidence 미하향',
    current: s.confidence,
    suggested: 'medium 이하로 하향'
  });
});

// 중복 검사: 같은 영상+종목+화자
console.log('\n🔍 중복 검사');
const duplicateMap = {};
signalsData.forEach(s => {
  const key = `${s.video_id}_${s.stock}_${s.speaker_id}`;
  if (!duplicateMap[key]) {
    duplicateMap[key] = [];
  }
  duplicateMap[key].push(s);
});

const duplicates = Object.values(duplicateMap).filter(group => group.length > 1);
console.log(`❌ 중복 시그널 그룹: ${duplicates.length}개`);
duplicates.forEach((group, idx) => {
  console.log(`\n중복 그룹 ${idx + 1}:`);
  group.forEach(s => {
    console.log(`  - ID: ${s.id}, 종목: ${s.stock}, 화자: ${s.speakers?.name}`);
    console.log(`    key_quote: ${s.key_quote}`);
  });
  
  group.slice(1).forEach(s => {
    issues.push({
      id: s.id,
      stock: s.stock,
      speaker: s.speakers?.name,
      issue: '중복: 같은 영상+종목+화자',
      current: '중복 시그널',
      suggested: '최신 의견만 남기고 제거'
    });
  });
});

// 이슈 요약
console.log('\n\n=== 이슈 요약 ===');
console.log(`총 발견된 이슈: ${issues.length}개`);

const issueTypes = {};
issues.forEach(issue => {
  const type = issue.issue.split(':')[0];
  issueTypes[type] = (issueTypes[type] || 0) + 1;
});

Object.entries(issueTypes).forEach(([type, count]) => {
  console.log(`${type}: ${count}개`);
});

// 이슈를 JSON 파일로 저장
fs.writeFileSync('v10_issues.json', JSON.stringify(issues, null, 2));
console.log('\n이슈 목록을 v10_issues.json에 저장했습니다.');

// 시그널 분포 다시 확인
console.log('\n=== 현재 시그널 분포 ===');
const signalCounts = {};
signalsData.forEach(s => {
  signalCounts[s.signal] = (signalCounts[s.signal] || 0) + 1;
});
console.log(signalCounts);

console.log('\n=== mention_type 분포 ===');
const mentionCounts = {};
signalsData.forEach(s => {
  mentionCounts[s.mention_type] = (mentionCounts[s.mention_type] || 0) + 1;
});
console.log(mentionCounts);