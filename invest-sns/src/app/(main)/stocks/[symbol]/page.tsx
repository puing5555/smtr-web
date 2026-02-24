import StockChartClient from './StockChartClient';

export async function generateStaticParams(): Promise<{ symbol: string }[]> {
  // 시그널 데이터의 모든 종목을 정적으로 생성
  const symbols = [
    'ATNF', 'BNB', 'CC', 'CNTN', 'ChatGPT', 'Circle',
    'GOOGL', 'MSTR', 'NVDA', 'PENGU', 'PLTR', 'SBI',
    'SBI 홀딩스', 'SK', 'WLFI', 'XRP',
    '금', '기술주', '라이나스 희토류', '모네로', '미국 주식',
    '블리시', '비트코인', '삼성ENA', '샤프링크', '솔라나',
    '스테이블코인', '알트코인', '알파벳', '암호화폐', '엔비디아',
    '오뚜기', '월드코인', '율촌화학', '이더리움', '체인링크', '코스피',
    // 영문 티커 별칭
    'BTC', 'ETH', 'SOL', 'ADA', 'DOT',
  ];

  return symbols.map(symbol => ({ symbol }));
}

export default async function StockChartPage({ 
  params 
}: { 
  params: Promise<{ symbol: string }> 
}) {
  const { symbol } = await params;
  
  return <StockChartClient symbol={symbol} />;
}
