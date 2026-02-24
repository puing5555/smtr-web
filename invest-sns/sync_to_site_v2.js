const fs = require('fs');
const path = require('path');

console.log('🚀 SMTR 원본 데이터 기반 동기화 시작...');

function loadJSON(filepath) {
    try {
        const fullPath = path.resolve(filepath);
        return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
    } catch (error) {
        console.error(`❌ 파일 로드 실패: ${filepath}`, error.message);
        return null;
    }
}

function extractStock(asset) {
    // 괄호 안 티커 추출: "월드리버티파이낸셜 (WLFI)" → "WLFI"
    const match = asset.match(/\(([^)]+)\)$/);
    return match ? match[1] : asset;
}

function convertToCorinpapaSignal(originalSignal, index) {
    const stock = extractStock(originalSignal.asset);
    const stockName = originalSignal.asset;
    
    return {
        id: 1000 + index,
        influencer: originalSignal.channel,
        stock: stock,
        stockName: stockName,
        signalType: originalSignal.signal_type,
        content: originalSignal.content,
        timestamp: originalSignal.timestamp,
        youtubeLink: `https://youtube.com/watch?v=${originalSignal.video_id}`,
        analysis: {
            summary: originalSignal.context || '',
            detail: originalSignal.context || ''
        },
        videoDate: originalSignal.upload_date,
        videoTitle: originalSignal.title,
        confidence: originalSignal.confidence,
        timeframe: originalSignal.timeframe,
        conditional: originalSignal.conditional,
        skinInGame: originalSignal.skin_in_game,
        hedged: originalSignal.hedged,
        videoSummary: originalSignal.video_summary || ''
    };
}

function getSignalKey(signal, isOriginal = false) {
    if (isOriginal) {
        return `${signal.video_id}_${signal.asset}`;
    } else {
        return `${signal.youtubeLink.split('/').pop()}_${signal.stockName}`;
    }
}

function saveSignalsToTS(signalsData, outputPath) {
    const tsContent = `// 코린이 아빠 실제 시그널 데이터 (${signalsData.length}개)
// 자동 생성됨 - 수정하지 마세요
// 원본 데이터 기반 동기화: ${new Date().toISOString()}

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

function main() {
    // 1. 원본 데이터 로드 (177개)
    console.log('📖 원본 시그널 데이터 로드 중...');
    const originalSignalsPath = path.join(__dirname, 'smtr_data', 'corinpapa1106', '_deduped_signals_8types_dated.json');
    const originalSignals = loadJSON(originalSignalsPath);
    
    if (!originalSignals) {
        console.error('❌ 원본 시그널 데이터를 불러올 수 없습니다.');
        return;
    }
    console.log(`✅ 원본 시그널: ${originalSignals.length}개`);

    // 2. 리뷰 상태 로드
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

    // 4. 원본 데이터를 TypeScript 형식으로 변환
    console.log('🔧 데이터 변환 및 리뷰 상태 적용 중...');
    
    let approvedCount = 0;
    let rejectedCount = 0;
    let modifiedCount = 0;
    let deletedCount = 0;

    const processedSignals = [];

    originalSignals.forEach((originalSignal, index) => {
        // 원본 데이터를 TypeScript 형식으로 변환
        const convertedSignal = convertToCorinpapaSignal(originalSignal, index);
        
        // 리뷰 상태 확인 (원본 키 형식과 변환된 키 형식 모두 확인)
        const originalKey = getSignalKey(originalSignal, true);
        const convertedKey = getSignalKey(convertedSignal, false);
        
        const review = mergedReviews[originalKey] || mergedReviews[convertedKey];
        
        // 디버깅: 처음 몇 개 시그널 출력
        if (index < 5) {
            console.log(`🔍 [${index}] 원본 키: ${originalKey}`);
            console.log(`🔍 [${index}] 변환 키: ${convertedKey}`);
            console.log(`🔍 [${index}] 리뷰: ${review?.status || 'undefined'}`);
        }
        
        if (!review) {
            // 리뷰 정보가 없으면 기본적으로 승인으로 처리
            approvedCount++;
            processedSignals.push(convertedSignal);
        } else if (review.status === 'approved') {
            approvedCount++;
            processedSignals.push(convertedSignal);
        } else if (review.status === 'rejected') {
            if (review.action === 'delete') {
                console.log(`❌ 삭제 처리: ${originalKey} (${originalSignal.asset})`);
                deletedCount++;
                // 삭제 - 배열에 추가하지 않음
            } else if (review.action === 'modify' && review.signalType) {
                console.log(`🔄 수정 처리: ${originalKey} (${originalSignal.asset}) ${originalSignal.signal_type} → ${review.signalType}`);
                modifiedCount++;
                convertedSignal.signalType = review.signalType; // 시그널 타입 수정
                processedSignals.push(convertedSignal);
            } else {
                console.log(`🚫 거부 처리: ${originalKey} (${originalSignal.asset})`);
                rejectedCount++;
                // 기본 거부 - 배열에 추가하지 않음
            }
        } else {
            // pending 상태는 승인으로 처리
            approvedCount++;
            processedSignals.push(convertedSignal);
        }
    });

    // 최신순 정렬 (videoDate 기준)
    processedSignals.sort((a, b) => new Date(b.videoDate) - new Date(a.videoDate));

    // 5. 결과 통계
    console.log('\n📊 동기화 결과:');
    console.log(`- 원본 시그널: ${originalSignals.length}개`);
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
        if (fs.existsSync(originalPath)) {
            fs.copyFileSync(originalPath, backupPath);
            console.log(`💾 백업 생성: ${backupPath}`);
        }
    } catch (error) {
        console.warn('⚠️  백업 생성 실패:', error.message);
    }

    // 새 파일 저장
    saveSignalsToTS(processedSignals, originalPath);

    // 7. 변환된 리뷰 키 매핑 저장
    const convertedReviews = {};
    originalSignals.forEach((originalSignal, index) => {
        const originalKey = getSignalKey(originalSignal, true);
        const convertedSignal = convertToCorinpapaSignal(originalSignal, index);
        const convertedKey = getSignalKey(convertedSignal, false);
        
        const review = mergedReviews[originalKey];
        if (review) {
            convertedReviews[convertedKey] = review;
        }
    });

    const updatedReviewsPath = path.join(__dirname, '_matched_reviews_converted.json');
    fs.writeFileSync(updatedReviewsPath, JSON.stringify(convertedReviews, null, 2), 'utf8');
    console.log(`💾 변환된 리뷰 상태 저장: ${updatedReviewsPath}`);

    console.log('\n✅ 원본 데이터 기반 동기화 완료!');
    console.log('\n📋 다음 단계:');
    console.log('1. signal-review-v4 다시 생성 (원본 데이터 기준)');
    console.log('2. cd ../smtr-web');
    console.log('3. npm run build (사이트 빌드)');
    console.log('4. GitHub Pages에 배포');
    console.log('\n💡 이제 원본 데이터와 완전히 동기화되었습니다.');

    // 8. 샘플 데이터 출력
    console.log('\n📋 변환된 데이터 샘플:');
    console.log(JSON.stringify(processedSignals[0], null, 2));
}

// 실행
if (require.main === module) {
    main();
}