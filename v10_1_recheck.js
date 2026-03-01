const fs = require('fs');

// 기존 이슈들과 개선된 V10.1 규칙을 대조 검토
const signalsData = JSON.parse(fs.readFileSync('signals_data.json', 'utf8'));
const previousIssues = JSON.parse(fs.readFileSync('v10_issues.json', 'utf8'));

console.log('=== V10.1 프롬프트 개선 효과 검증 ===');

// 이전에 발견된 이슈들을 새로운 규칙으로 재평가
const resolvedIssues = [];
const remainingIssues = [];

console.log('\n🔍 규칙 30 강화 효과 (key_quote 품질)');
const rule30Issues = previousIssues.filter(issue => issue.issue.includes('규칙30'));
console.log(`이전 규칙30 위반: ${rule30Issues.length}개`);

// 새로운 규칙 30 기준으로 재평가
rule30Issues.forEach(issue => {
  const signal = signalsData.find(s => s.id === issue.id);
  if (!signal) return;
  
  const quote = signal.key_quote || '';
  const stock = signal.stock || '';
  
  // V10.1 새 기준 적용
  let newIssues = [];
  
  // 1. 종목명 명시적 포함 (약칭/대명사 금지)
  const bannedPronouns = ['이 회사', '둘 다', '여기', '그거', '이거'];
  if (bannedPronouns.some(p => quote.includes(p))) {
    newIssues.push('대명사 사용');
  } else if (!quote.includes(stock) && !quote.includes(signal.ticker)) {
    // 약칭 체크 (삼성전자 → 삼전, SK하이닉스 → 하닉스)
    let hasStockRef = false;
    if (stock === 'SK하이닉스' && (quote.includes('하닉스') || quote.includes('하이닉스'))) hasStockRef = true;
    if (stock === '삼성전자' && (quote.includes('삼전') || quote.includes('삼성'))) hasStockRef = true;
    if (stock === '엔비디아' && (quote.includes('NVIDIA') || quote.includes('NVDA'))) hasStockRef = true;
    
    if (!hasStockRef) {
      newIssues.push('종목명 없음');
    }
  }
  
  // 2. 구체적 투자 판단 근거 (단순 감정 표현 금지)
  const bannedPhrases = ['좋아요', '괜찮다', '주인공이다', '추천합니다', '좋습니다'];
  if (bannedPhrases.some(p => quote.includes(p))) {
    newIssues.push('단순 감정 표현');
  }
  
  // 3. 20자 이상
  if (quote.length < 20) {
    newIssues.push('20자 미만');
  }
  
  if (newIssues.length > 0) {
    remainingIssues.push({
      ...issue,
      newIssues: newIssues,
      quote: quote
    });
  } else {
    resolvedIssues.push({
      ...issue,
      resolution: 'V10.1 기준으로 해결됨'
    });
  }
});

console.log(`✅ 해결된 이슈: ${resolvedIssues.length}개`);
console.log(`❌ 여전히 문제: ${remainingIssues.length}개`);

if (remainingIssues.length > 0) {
  console.log('\n여전히 문제인 key_quote들:');
  remainingIssues.slice(0, 5).forEach((issue, idx) => {
    console.log(`${idx + 1}. ${issue.stock} - ${issue.speaker}`);
    console.log(`   문제: ${issue.newIssues.join(', ')}`);
    console.log(`   quote: "${issue.quote}"`);
  });
}

console.log('\n🔍 규칙 29 강화 효과 (화자 식별)');
const rule29Issues = previousIssues.filter(issue => issue.issue.includes('규칙29'));
console.log(`이전 규칙29 위반: ${rule29Issues.length}개`);

// 영상 제목 패턴으로 해결 가능한 것들 체크
const resolvableByTitle = rule29Issues.filter(issue => {
  const signal = signalsData.find(s => s.id === issue.id);
  if (!signal) return false;
  
  const title = signal.influencer_videos?.title || '';
  const guestPattern = /\|\s*([가-힣]+(?:\s+[가-힣]+)*)/;
  const match = title.match(guestPattern);
  
  return match && match[1] && match[1] !== signal.speakers?.name;
});

console.log(`✅ 영상 제목으로 해결 가능: ${resolvableByTitle.length}개`);
console.log(`❌ 여전히 해결 필요: ${rule29Issues.length - resolvableByTitle.length}개`);

console.log('\n🔍 규칙 3 확장 효과 (전망 vs 권유)');
const rule3Issues = previousIssues.filter(issue => issue.issue.includes('규칙3'));
console.log(`이전 규칙3 위반: ${rule3Issues.length}개`);

rule3Issues.forEach(issue => {
  const signal = signalsData.find(s => s.id === issue.id);
  if (!signal) return;
  
  console.log(`\n종목: ${issue.stock} - ${issue.speaker}`);
  console.log(`key_quote: "${signal.key_quote}"`);
  
  // V10.1 새 규칙 적용
  if (signal.key_quote.includes('해야 된다') || signal.key_quote.includes('되어야 한다') || 
      signal.key_quote.includes('포트폴리오에 있어야')) {
    console.log('✅ V10.1 규칙으로 해결: 전망 표현으로 재분류 가능');
    resolvedIssues.push({...issue, resolution: 'V10.1 전망 패턴 확장으로 해결'});
  }
});

console.log('\n🔍 규칙 32 신규 (중복 방지) 효과');
const duplicateIssues = previousIssues.filter(issue => issue.issue.includes('중복'));
console.log(`중복 이슈: ${duplicateIssues.length}개`);

// 바스켓 발언 중복 체크
const basketSignals = signalsData.filter(s => {
  const reasoning = s.reasoning || '';
  return reasoning.includes('4개 핵심') || reasoning.includes('바스켓') || 
         (s.speakers?.name === '배재규' && ['TSMC', '엔비디아', 'SK하이닉스', 'ASML'].includes(s.stock));
});

console.log(`🎯 바스켓 발언 중복 대상: ${basketSignals.length}개`);
if (basketSignals.length > 0) {
  console.log('배재규의 4개 핵심 종목들:');
  basketSignals.forEach(s => {
    console.log(`  - ${s.stock}: ${s.key_quote.substring(0, 50)}...`);
  });
  console.log('✅ V10.1 규칙 32로 해결: 반도체 SECTOR 1개 시그널로 통합 가능');
}

console.log('\n📊 전체 개선 효과 요약');
const totalPreviousIssues = previousIssues.length;
const estimatedResolved = resolvedIssues.length + resolvableByTitle.length + basketSignals.length - 4; // 바스켓 중복 제거
const estimatedRemaining = totalPreviousIssues - estimatedResolved;

console.log(`이전 이슈 총: ${totalPreviousIssues}개`);
console.log(`예상 해결: ${estimatedResolved}개 (${Math.round(estimatedResolved/totalPreviousIssues*100)}%)`);
console.log(`예상 잔존: ${estimatedRemaining}개 (${Math.round(estimatedRemaining/totalPreviousIssues*100)}%)`);

// V10.1의 주요 개선 사항 요약
console.log('\n🎯 V10.1 주요 개선 사항:');
console.log('1. key_quote 품질 기준 강화 (15자→20자, 구체적 근거 요구)');
console.log('2. 화자 식별 우선순위 명시 (영상 제목이 1순위)');  
console.log('3. 전망 vs 권유 패턴 확장 ("해야 된다" 등 당위성 표현)');
console.log('4. 중복 방지 규칙 신설 (바스켓 발언, 동일 내용)');
console.log('5. 교차 검증 항목 3개 추가 (29항목으로 확장)');

fs.writeFileSync('v10_1_improvement_report.json', JSON.stringify({
  summary: {
    previousIssues: totalPreviousIssues,
    estimatedResolved: estimatedResolved,
    estimatedRemaining: estimatedRemaining,
    improvementRate: Math.round(estimatedResolved/totalPreviousIssues*100)
  },
  resolvedIssues: resolvedIssues,
  remainingIssues: remainingIssues.slice(0, 10), // 상위 10개만
  resolvableByTitle: resolvableByTitle.slice(0, 10)
}, null, 2));

console.log('\n개선 보고서를 v10_1_improvement_report.json에 저장했습니다.');