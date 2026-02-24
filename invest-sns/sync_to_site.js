const fs = require('fs');
const path = require('path');

console.log('🔄 SMTR 사이트 동기화 시작...');

function loadJSON(filepath) {
    try {
        const fullPath = path.resolve(filepath);
        return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
    } catch (error) {
        console.error(`❌ 파일 로드 실패: ${filepath}`, error.message);
        return null;
    }
}

function loadSignalsFromTS() {
    try {
        const signalsPath = path.join(__dirname, 'src', 'data', 'corinpapa-signals.ts');
        const signalsContent = fs.readFileSync(signalsPath, 'utf8');
        
        // TypeScript export를 JSON으로 변환
        const exportMatch = signalsContent.match(/export const corinpapaSignals: CorinpapaSignal\[\] = (\[[\s\S]*\]);/);
        if (!exportMatch) {
            // 더 간단한 패턴 시도
            const simpleMatch = signalsContent.match(/= (\[[\s\S]*\]);[\s]*$/m);
            if (!simpleMatch) {
                throw new Error('corinpapa-signals.ts에서 데이터를 찾을 수 없습니다.');
            }
            return eval(`(${simpleMatch[1]})`);
        } else {
            return eval(`(${exportMatch[1]})`);
        }
    } catch (error) {
        console.error('❌ 시그널 데이터 로드 실패:', error.message);
        return null;
    }
}

function saveSignalsToTS(signalsData, outputPath) {
    const tsContent = `// 코린이 아빠 실제 시그널 데이터 (${signalsData.length}개)
// 자동 생성됨 - 수정하지 마세요
// 마지막 동기화: ${new Date().toISOString()}

export interface CorinpapaSignal {
  id: number;
  influencer: string;
  stock: string;
  stockName: string;
  signalType: 'STRONG_BUY' | 'BUY' | 'POSITIVE' | 'HOLD' | 'NEUTRAL' | 'CONCERN' | 'SELL' | 'STRONG_SELL';
  content: string;
  timestamp: string;
  youtubeLink: string;
  analysis: {
    summary: string;
    detail: string;
  };
  videoDate: string;
  videoTitle: string;
  confidence: string;
  timeframe: string;
  conditional: boolean;
  skinInGame: boolean;
  hedged: boolean;
  videoSummary?: string;
}

// 실제 시그널 데이터 (${signalsData.length}개, 최신순 정렬)
export const corinpapaSignals: CorinpapaSignal[] = ${JSON.stringify(signalsData, null, 2)};`;

    fs.writeFileSync(outputPath, tsContent, 'utf8');
    console.log(`✅ TypeScript 파일 저장: ${outputPath}`);
}

function getSignalKey(signal) {
    return `${signal.youtubeLink.split('/').pop()}_${signal.stockName}`;
}

function main() {
    // 1. 현재 시그널 데이터 로드
    console.log('📖 현재 시그널 데이터 로드 중...');
    const originalSignals = loadSignalsFromTS();
    if (!originalSignals) {
        console.error('❌ 원본 시그널 데이터를 불러올 수 없습니다.');
        return;
    }
    console.log(`✅ 원본 시그널: ${originalSignals.length}개`);

    // 2. 리뷰 상태 로드 (여러 소스에서)
    console.log('📖 리뷰 상태 로드 중...');
    
    // 기본 리뷰 데이터
    const reviewsData = loadJSON('./_matched_reviews.json') || {};
    console.log(`📋 기본 리뷰 데이터: ${Object.keys(reviewsData).length}개`);
    
    // 브라우저 로컬스토리지에서 다운로드한 리뷰 상태
    const reviewStateFiles = fs.readdirSync('.')
        .filter(file => file.startsWith('review-state-') && file.endsWith('.json'))
        .sort()
        .reverse(); // 최신 파일 우선
    
    let latestReviewState = {};
    if (reviewStateFiles.length > 0) {
        console.log(`📄 최신 리뷰 상태 파일: ${reviewStateFiles[0]}`);
        const stateData = loadJSON(`./${reviewStateFiles[0]}`);
        if (stateData && stateData.reviews) {
            latestReviewState = stateData.reviews;
            console.log(`📋 브라우저 리뷰 상태: ${Object.keys(latestReviewState).length}개`);
        }
    } else {
        console.log('⚠️  브라우저 리뷰 상태 파일을 찾을 수 없습니다. 기본 리뷰 데이터만 사용합니다.');
    }

    // 3. 리뷰 상태 병합 (브라우저 상태가 우선)
    const mergedReviews = { ...reviewsData };
    Object.keys(latestReviewState).forEach(key => {
        mergedReviews[key] = latestReviewState[key];
    });
    
    console.log(`🔄 병합된 리뷰 상태: ${Object.keys(mergedReviews).length}개`);

    // 4. 시그널 필터링 및 수정
    console.log('🔧 시그널 처리 중...');
    
    let approvedCount = 0;
    let rejectedCount = 0;
    let modifiedCount = 0;
    let deletedCount = 0;

    const processedSignals = originalSignals.filter(signal => {
        const key = getSignalKey(signal);
        const review = mergedReviews[key];
        
        // 디버깅: 처음 몇 개 시그널의 키와 리뷰 상태 출력
        if (approvedCount + rejectedCount + modifiedCount + deletedCount < 10) {
            console.log(`🔍 시그널 키: ${key}, 리뷰 상태:`, review?.status || 'undefined');
        }
        
        if (!review) {
            // 리뷰 정보가 없으면 기본적으로 승인으로 처리
            approvedCount++;
            return true;
        }

        if (review.status === 'approved') {
            approvedCount++;
            return true;
        } else if (review.status === 'rejected') {
            if (review.action === 'delete') {
                console.log(`❌ 삭제 처리: ${key} (${signal.stockName})`);
                deletedCount++;
                return false; // 삭제
            } else if (review.action === 'modify' && review.signalType) {
                console.log(`🔄 수정 처리: ${key} (${signal.stockName}) ${signal.signalType} → ${review.signalType}`);
                modifiedCount++;
                signal.signalType = review.signalType; // 시그널 타입 수정
                return true;
            } else {
                console.log(`🚫 거부 처리: ${key} (${signal.stockName})`);
                rejectedCount++;
                return false; // 기본 거부
            }
        } else {
            // pending 상태는 승인으로 처리
            approvedCount++;
            return true;
        }
    });

    // 5. 결과 통계
    console.log('\n📊 동기화 결과:');
    console.log(`- 승인된 시그널: ${approvedCount}개`);
    console.log(`- 수정된 시그널: ${modifiedCount}개`);
    console.log(`- 삭제된 시그널: ${deletedCount}개`);
    console.log(`- 거부된 시그널: ${rejectedCount}개`);
    console.log(`- 최종 시그널: ${processedSignals.length}개`);

    // 6. TypeScript 파일 저장
    console.log('\n💾 TypeScript 파일 저장 중...');
    
    // 백업 생성
    const originalPath = path.join(__dirname, 'src', 'data', 'corinpapa-signals.ts');
    const backupPath = path.join(__dirname, `src/data/corinpapa-signals-backup-${new Date().toISOString().split('T')[0]}.ts`);
    
    try {
        fs.copyFileSync(originalPath, backupPath);
        console.log(`💾 백업 생성: ${backupPath}`);
    } catch (error) {
        console.warn('⚠️  백업 생성 실패:', error.message);
    }

    // 새 파일 저장
    saveSignalsToTS(processedSignals, originalPath);

    // 7. 리뷰 상태 업데이트 (동기화 반영)
    const updatedReviewsPath = path.join(__dirname, '_matched_reviews_synced.json');
    fs.writeFileSync(updatedReviewsPath, JSON.stringify(mergedReviews, null, 2), 'utf8');
    console.log(`💾 동기화된 리뷰 상태 저장: ${updatedReviewsPath}`);

    console.log('\n✅ 동기화 완료!');
    console.log('\n📋 다음 단계:');
    console.log('1. cd ../smtr-web (또는 Next.js 프로젝트 디렉토리로 이동)');
    console.log('2. npm run build (사이트 빌드)');
    console.log('3. GitHub Pages에 배포');
    console.log('\n💡 변경사항이 정상적으로 반영되었는지 확인하세요.');
}

// 실행
if (require.main === module) {
    main();
}