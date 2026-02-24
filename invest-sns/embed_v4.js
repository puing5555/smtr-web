// embed_v4.js - 데이터 임베딩 및 Opus diff 기능
const fs = require('fs');
const path = require('path');

function loadJSON(filepath) {
    try {
        const fullPath = path.resolve(filepath);
        return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
    } catch (error) {
        console.error(`❌ 파일 로드 실패: ${filepath}`, error.message);
        return null;
    }
}

function generateDiffDisplay(original, opus) {
    if (!original || !opus || !opus.signal_data) return null;
    
    const originalData = original;
    const opusData = opus.signal_data;
    
    const differences = [];
    
    // 시그널 타입 비교
    if (originalData.signal_type !== opusData.signal_type) {
        differences.push({
            field: 'Signal Type',
            original: originalData.signal_type,
            opus: opusData.signal_type,
            type: 'change'
        });
    }
    
    // Content 비교
    if (originalData.content !== opusData.content) {
        differences.push({
            field: 'Content',
            original: originalData.content,
            opus: opusData.content,
            type: 'change'
        });
    }
    
    // Context 비교
    if (originalData.context !== opusData.context) {
        differences.push({
            field: 'Context',
            original: originalData.context || '없음',
            opus: opusData.context || '없음',
            type: 'change'
        });
    }
    
    // Confidence 비교
    if (originalData.confidence !== opusData.confidence) {
        differences.push({
            field: 'Confidence',
            original: originalData.confidence,
            opus: opusData.confidence,
            type: 'change'
        });
    }
    
    // Timestamp 비교
    if (originalData.timestamp !== opusData.timestamp) {
        differences.push({
            field: 'Timestamp',
            original: originalData.timestamp,
            opus: opusData.timestamp,
            type: 'change'
        });
    }
    
    return differences.length > 0 ? differences : null;
}

function parseCorinpapaSignals() {
    console.log('📊 데이터 파싱 시작...');
    
    // JSON 파일들 로드
    const matchedReviews = loadJSON('./_matched_reviews.json') || {};
    const opusResults = loadJSON('./_opus_review_results.json') || {};
    
    // 중복제거된 시그널 데이터 로드
    const dedupedPath = path.join(__dirname, 'smtr_data', 'corinpapa1106', '_deduped_signals_8types_dated.json');
    const dedupedSignals = loadJSON(dedupedPath) || [];
    
    if (!dedupedSignals.length) {
        console.error('❌ 중복제거된 시그널 데이터를 찾을 수 없습니다');
        return { signals: [], stats: {} };
    }
    
    console.log(`📊 데이터 로드 완료: ${dedupedSignals.length}개 시그널`);
    
    // 8가지 시그널 타입만 허용
    const allowedSignalTypes = ['STRONG_BUY', 'BUY', 'POSITIVE', 'HOLD', 'NEUTRAL', 'CONCERN', 'SELL', 'STRONG_SELL'];
    
    const processedSignals = dedupedSignals
        .filter(signal => allowedSignalTypes.includes(signal.signal_type))
        .map((signal, index) => {
            // 키 생성 (여러 패턴 시도)
            const possibleKeys = [
                `${signal.video_id}_${signal.asset}_${index}`,
                `${signal.video_id}_${signal.asset}`,
                `${signal.video_id}_${signal.asset.split('(')[0].trim()}_${index}`,
                `${signal.video_id}_${signal.asset.split('(')[0].trim()}`
            ];
            
            // 매칭되는 리뷰 상태 찾기
            let reviewStatus = { status: 'pending' };
            for (const key of possibleKeys) {
                if (matchedReviews[key]) {
                    reviewStatus = matchedReviews[key];
                    break;
                }
            }
            
            // 매칭되는 Opus 결과 찾기
            let opusResult = null;
            for (const key of possibleKeys) {
                if (opusResults[key]) {
                    opusResult = opusResults[key];
                    break;
                }
            }
            
            // Diff 데이터 생성
            let diffData = null;
            if (opusResult && opusResult.verdict === 'approve') {
                diffData = generateDiffDisplay(signal, opusResult);
            }
            
            // YouTube 링크 생성
            let youtubeLink = '';
            if (signal.video_id && signal.timestamp) {
                const timeMatch = signal.timestamp.match(/\[(\d+):(\d+)\]/);
                if (timeMatch) {
                    const minutes = parseInt(timeMatch[1]);
                    const seconds = parseInt(timeMatch[2]);
                    const totalSeconds = minutes * 60 + seconds;
                    youtubeLink = `https://youtube.com/watch?v=${signal.video_id}&t=${totalSeconds}s`;
                } else {
                    youtubeLink = `https://youtube.com/watch?v=${signal.video_id}`;
                }
            }
            
            return {
                id: `signal_${index}`,
                influencer: '코린이 아빠',
                stock: signal.asset.match(/\(([^)]+)\)$/)?.[1] || signal.asset,
                stockName: signal.asset,
                signalType: signal.signal_type,
                content: signal.content,
                timestamp: signal.timestamp,
                youtubeLink: youtubeLink,
                videoDate: signal.upload_date,
                videoTitle: signal.title,
                confidence: signal.confidence,
                timeframe: signal.timeframe,
                conditional: signal.conditional,
                skinInGame: signal.skin_in_game,
                hedged: signal.hedged,
                context: signal.context,
                reviewStatus: reviewStatus.status,
                reviewTime: reviewStatus.time,
                reviewReason: reviewStatus.reason,
                opusResult: opusResult,
                hasDiff: !!diffData,
                diffData: diffData
            };
        })
        // 최신순 정렬 (영상 날짜 기준)
        .sort((a, b) => new Date(b.videoDate).getTime() - new Date(a.videoDate).getTime());
    
    // 통계 계산
    const stats = {
        total: processedSignals.length,
        pending: processedSignals.filter(s => s.reviewStatus === 'pending').length,
        approved: processedSignals.filter(s => s.reviewStatus === 'approved').length,
        rejected: processedSignals.filter(s => s.reviewStatus === 'rejected').length,
        withOpusChanges: processedSignals.filter(s => s.hasDiff).length
    };
    
    // 시그널 타입별 분포
    const signalDistribution = {};
    allowedSignalTypes.forEach(type => {
        signalDistribution[type] = processedSignals.filter(s => s.signalType === type).length;
    });
    stats.signalDistribution = signalDistribution;
    
    console.log(`✅ 시그널 처리 완료: ${processedSignals.length}개`);
    console.log(`📊 통계: 대기 ${stats.pending}개, 승인 ${stats.approved}개, 거부 ${stats.rejected}개`);
    console.log(`🔄 Opus 수정사항: ${stats.withOpusChanges}개`);
    
    return { signals: processedSignals, stats };
}

function embedIntoHTML() {
    const { signals, stats } = parseCorinpapaSignals();
    
    const htmlTemplatePath = './signal-review-v4.html';
    const outputPath = './signal-review-v4-embedded.html';
    
    try {
        let htmlContent = fs.readFileSync(htmlTemplatePath, 'utf8');
        
        // JavaScript 데이터 삽입
        const dataScript = `
        <script>
        // 임베딩된 시그널 데이터 (v4)
        window.signalData = ${JSON.stringify(signals, null, 2)};
        window.signalStats = ${JSON.stringify(stats, null, 2)};
        
        console.log('✅ 시그널 데이터 로드 완료:', window.signalData.length, '개');
        console.log('📊 통계:', window.signalStats);
        </script>
        </body>`;
        
        htmlContent = htmlContent.replace('</body>', dataScript);
        
        fs.writeFileSync(outputPath, htmlContent, 'utf8');
        
        console.log(`✅ HTML 임베딩 완료: ${outputPath}`);
        console.log(`📊 최종 데이터: ${signals.length}개 시그널`);
        
        return true;
    } catch (error) {
        console.error('❌ HTML 임베딩 실패:', error);
        return false;
    }
}

// CLI 실행
if (require.main === module) {
    console.log('🚀 embed_v4.js 실행 시작...');
    const success = embedIntoHTML();
    process.exit(success ? 0 : 1);
}

module.exports = { parseCorinpapaSignals, embedIntoHTML, generateDiffDisplay };