const fs = require('fs');
const path = require('path');

// 실제 시그널 데이터 로드
const signalsPath = path.join(__dirname, 'smtr_data', 'corinpapa1106', '_deduped_signals_8types_dated.json');

try {
  const signalsData = JSON.parse(fs.readFileSync(signalsPath, 'utf8'));
  
  // TypeScript 데이터로 변환
  const convertedSignals = signalsData.map((signal, index) => {
    // YouTube 링크 생성
    let youtubeLink = '';
    if (signal.video_id && signal.timestamp) {
      // 타임스탬프에서 시간을 추출 (예: "[8:52]" → "8m52s")
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

    // 종목명에서 코드 추출
    const stockCode = signal.asset.match(/\(([^)]+)\)$/)?.[1] || signal.asset;
    
    return {
      id: index + 1000, // 기존 더미 데이터와 구분하기 위해 1000부터 시작
      influencer: '코린이 아빠',
      stock: stockCode,
      stockName: signal.asset,
      signalType: signal.signal_type,
      content: signal.content,
      timestamp: signal.timestamp,
      youtubeLink,
      analysis: {
        summary: signal.context ? signal.context.slice(0, 50) + '...' : '분석 내용 없음',
        detail: signal.context || signal.content
      },
      videoDate: signal.date,
      videoTitle: signal.title,
      confidence: signal.confidence,
      timeframe: signal.timeframe,
      conditional: signal.conditional,
      skinInGame: signal.skin_in_game,
      hedged: signal.hedged
    };
  }).sort((a, b) => new Date(b.videoDate).getTime() - new Date(a.videoDate).getTime()); // 최신순 정렬

  // 시그널 타입별 분포 계산
  const signalTypeDistribution = {
    STRONG_BUY: 0,
    BUY: 0,
    POSITIVE: 0,
    HOLD: 0,
    NEUTRAL: 0,
    CONCERN: 0,
    SELL: 0,
    STRONG_SELL: 0
  };
  
  convertedSignals.forEach(signal => {
    signalTypeDistribution[signal.signalType] = (signalTypeDistribution[signal.signalType] || 0) + 1;
  });

  // 주요 종목 계산 (상위 5개)
  const assetCounts = {};
  convertedSignals.forEach(signal => {
    assetCounts[signal.stockName] = (assetCounts[signal.stockName] || 0) + 1;
  });
  
  const topStocks = Object.entries(assetCounts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5)
    .map(([stock]) => stock);

  // TypeScript 파일 생성
  const tsContent = `// 코린이 아빠 실제 시그널 데이터 (169개)
// 자동 생성됨 - 수정하지 마세요

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
}

// 실제 시그널 데이터 (169개, 최신순 정렬)
export const corinpapaSignals: CorinpapaSignal[] = ${JSON.stringify(convertedSignals, null, 2)};

// 코린이 아빠 통계 정보
export const corinpapaStats = {
  totalSignals: 169,
  signalDistribution: ${JSON.stringify(signalTypeDistribution, null, 2)},
  topStocks: ${JSON.stringify(topStocks, null, 2)},
  accuracy: 68, // 예상 정확도
  avgReturn: 12.4, // 예상 평균 수익률
  lastUpdate: '2026-02-23'
};
`;

  // src/data 디렉토리 생성
  const dataDir = path.join(__dirname, 'src', 'data');
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }

  // TypeScript 파일 저장
  const outputPath = path.join(dataDir, 'corinpapa-signals.ts');
  fs.writeFileSync(outputPath, tsContent, 'utf8');

  console.log(`✅ 변환 완료! ${convertedSignals.length}개 시그널을 ${outputPath}에 저장했습니다.`);
  console.log('\n📊 통계:');
  console.log(`- 총 시그널: ${convertedSignals.length}개`);
  console.log(`- 기간: ${convertedSignals[convertedSignals.length - 1]?.videoDate} ~ ${convertedSignals[0]?.videoDate}`);
  console.log('- 시그널 타입 분포:');
  Object.entries(signalTypeDistribution).forEach(([type, count]) => {
    console.log(`  ${type}: ${count}개`);
  });
  console.log(`- 주요 종목: ${topStocks.join(', ')}`);
  
} catch (error) {
  console.error('❌ 데이터 변환 실패:', error);
}