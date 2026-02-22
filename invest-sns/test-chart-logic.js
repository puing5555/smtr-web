// Test script for chart logic validation

// 종목명 → API 심볼 매핑 테이블 (test)
const STOCK_SYMBOLS = {
    '비트코인': { type: 'crypto', id: 'bitcoin' },
    'XRP': { type: 'crypto', id: 'ripple' },
    '이더리움': { type: 'crypto', id: 'ethereum' },
    '엔비디아': { type: 'stock', symbol: 'NVDA' },
    '솔라나': { type: 'crypto', id: 'solana' }
};

// Mock 시그널 데이터
const mockSignals = [
    { stock: '비트코인', date: '2025-12-01' },
    { stock: '비트코인', date: '2025-11-15' },
    { stock: '비트코인', date: '2025-10-20' },
    { stock: '엔비디아', date: '2026-01-10' },
    { stock: '엔비디아', date: '2025-12-15' }
];

// 더미 데이터 생성 함수 (간소화)
function generateDummyOHLC(stockName, startDate, endDate) {
    const data = [];
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    let basePrice = stockName.includes('비트코인') ? 95000 : 150;
    let currentPrice = basePrice;
    const current = new Date(start);

    while (current <= end) {
        const dateStr = current.toISOString().split('T')[0];
        
        const changeRate = (Math.random() - 0.5) * 0.1;
        const open = currentPrice;
        const close = open * (1 + changeRate);
        const high = Math.max(open, close) * (1 + Math.random() * 0.03);
        const low = Math.min(open, close) * (1 - Math.random() * 0.03);

        data.push({
            time: dateStr,
            open: open,
            high: high,
            low: low,
            close: close
        });

        currentPrice = close;
        current.setDate(current.getDate() + 7); // 매주 (테스트용)
    }

    return data;
}

// 시그널 날짜 범위 계산
function getSignalDateRange(stockName) {
    const signals = mockSignals.filter(stmt => stmt.stock === stockName);
    if (signals.length === 0) {
        const end = new Date();
        const start = new Date();
        start.setMonth(start.getMonth() - 6);
        return { start: start.toISOString().split('T')[0], end: end.toISOString().split('T')[0] };
    }

    const dates = signals.map(s => new Date(s.date));
    const minDate = new Date(Math.min(...dates));
    const maxDate = new Date(Math.max(...dates));
    
    minDate.setDate(minDate.getDate() - 30);
    const today = new Date();
    
    return {
        start: minDate.toISOString().split('T')[0],
        end: today.toISOString().split('T')[0]
    };
}

// 테스트 실행
function runTests() {
    console.log('=== 차트 로직 테스트 ===');
    
    // 1. 매핑 테이블 테스트
    console.log('\n1. 종목 매핑 테스트:');
    console.log('비트코인:', STOCK_SYMBOLS['비트코인']);
    console.log('엔비디아:', STOCK_SYMBOLS['엔비디아']);
    console.log('존재하지 않는 종목:', STOCK_SYMBOLS['존재하지않음']);
    
    // 2. 날짜 범위 계산 테스트
    console.log('\n2. 날짜 범위 계산:');
    const btcRange = getSignalDateRange('비트코인');
    const nvdaRange = getSignalDateRange('엔비디아');
    console.log('비트코인 범위:', btcRange);
    console.log('엔비디아 범위:', nvdaRange);
    
    // 3. 더미 데이터 생성 테스트
    console.log('\n3. 더미 데이터 생성:');
    const btcData = generateDummyOHLC('비트코인', btcRange.start, btcRange.end);
    console.log('비트코인 데이터 포인트 수:', btcData.length);
    console.log('첫 번째 데이터:', btcData[0]);
    console.log('마지막 데이터:', btcData[btcData.length - 1]);
    
    console.log('\n테스트 완료! ✅');
}

// 브라우저에서 실행될 경우
if (typeof window !== 'undefined') {
    runTests();
} else {
    // Node.js에서 실행될 경우
    runTests();
}