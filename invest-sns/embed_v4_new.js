const fs = require('fs');
const path = require('path');

console.log('🚀 signal-review-v4 데이터 임베딩 시작...');

// 1. corinpapa-signals.ts 파싱
console.log('📖 corinpapa-signals.ts 파싱 중...');
const signalsPath = path.join(__dirname, 'src', 'data', 'corinpapa-signals.ts');
const signalsContent = fs.readFileSync(signalsPath, 'utf8');

// TypeScript export를 JSON으로 변환
// 'export const corinpapaSignals: CorinpapaSignal[] = [' 이후의 내용을 추출
const exportMatch = signalsContent.match(/export const corinpapaSignals: CorinpapaSignal\[\] = (\[[\s\S]*\]);/);
if (!exportMatch) {
    console.log('첫 번째 패턴 실패, 두 번째 패턴 시도 중...');
    // 더 간단한 패턴 시도
    const simpleMatch = signalsContent.match(/= (\[[\s\S]*\]);[\s]*$/m);
    if (!simpleMatch) {
        throw new Error('corinpapa-signals.ts에서 데이터를 찾을 수 없습니다.');
    }
    const signalsData = eval(`(${simpleMatch[1]})`);
    console.log(`✅ 시그널 데이터 로드 완료: ${signalsData.length}개`);
    embedData(signalsData);
} else {
    // JavaScript로 실행하여 JSON 배열 생성
    const signalsData = eval(`(${exportMatch[1]})`);
    console.log(`✅ 시그널 데이터 로드 완료: ${signalsData.length}개`);
    embedData(signalsData);
}

function embedData(signalsData) {
    // 2. _matched_reviews.json 로드
    console.log('📖 _matched_reviews.json 로드 중...');
    const reviewsPath = path.join(__dirname, '_matched_reviews.json');
    const reviewsData = JSON.parse(fs.readFileSync(reviewsPath, 'utf8'));
    
    console.log(`✅ 리뷰 데이터 로드 완료: ${Object.keys(reviewsData).length}개`);
    
    // 3. _opus_review_results.json 로드
    console.log('📖 _opus_review_results.json 로드 중...');
    const opusPath = path.join(__dirname, '_opus_review_results.json');
    const opusData = JSON.parse(fs.readFileSync(opusPath, 'utf8'));
    
    console.log(`✅ Opus 데이터 로드 완료: ${Object.keys(opusData).length}개`);
    
    // 4. HTML 템플릿 로드
    console.log('📖 signal-review-v4.html 템플릿 로드 중...');
    const templatePath = path.join(__dirname, 'signal-review-v4.html');
    let htmlTemplate = fs.readFileSync(templatePath, 'utf8');
    
    // 5. 데이터 임베딩
    console.log('🔧 데이터 임베딩 중...');
    
    // 데이터를 JSON 문자열로 변환하고 HTML에 삽입
    let embeddedHtml = htmlTemplate
        .replace('{{SIGNALS_DATA}}', JSON.stringify(signalsData, null, 2))
        .replace('{{REVIEWS_DATA}}', JSON.stringify(reviewsData, null, 2))
        .replace('{{OPUS_DATA}}', JSON.stringify(opusData, null, 2));
    
    // 6. 최종 HTML 파일 저장
    const outputPath = path.join(__dirname, 'signal-review-v4-embedded.html');
    fs.writeFileSync(outputPath, embeddedHtml, 'utf8');
    
    console.log('✅ 데이터 임베딩 완료!');
    console.log(`📁 출력 파일: ${outputPath}`);
    console.log(`📊 파일 크기: ${Math.round(embeddedHtml.length / 1024)}KB`);
    
    // 7. 통계 출력
    console.log('\n📊 데이터 통계:');
    console.log(`- 총 시그널: ${signalsData.length}개`);
    console.log(`- 리뷰 상태: ${Object.keys(reviewsData).length}개`);
    console.log(`- Opus 검토: ${Object.keys(opusData).length}개`);
    
    // Opus 검토 결과 통계
    const opusStats = Object.values(opusData).reduce((acc, result) => {
        acc[result.verdict] = (acc[result.verdict] || 0) + 1;
        return acc;
    }, {});
    
    console.log(`- Opus 승인: ${opusStats.approve || 0}개`);
    console.log(`- Opus 수정: ${opusStats.modify || 0}개`);
    console.log(`- Opus 거부: ${opusStats.reject || 0}개`);
    
    // 리뷰 상태 통계
    const reviewStats = Object.values(reviewsData).reduce((acc, review) => {
        acc[review.status] = (acc[review.status] || 0) + 1;
        return acc;
    }, {});
    
    console.log(`- 승인된 리뷰: ${reviewStats.approved || 0}개`);
    console.log(`- 거부된 리뷰: ${reviewStats.rejected || 0}개`);
    console.log(`- 대기 중인 리뷰: ${Object.keys(reviewsData).length - (reviewStats.approved || 0) - (reviewStats.rejected || 0)}개`);
    
    console.log('\n🎉 embed_v4_new.js 실행 완료!');
    console.log('👀 브라우저에서 signal-review-v4-embedded.html을 열어보세요.');
}