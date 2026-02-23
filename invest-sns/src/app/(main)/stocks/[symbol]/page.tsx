import StockChartClient from './StockChartClient';

export async function generateStaticParams(): Promise<{ symbol: string }[]> {
  // 주요 종목들을 미리 정적으로 생성
  return [
    { symbol: 'BTC' },
    { symbol: 'ETH' },
    { symbol: 'SOL' },
    { symbol: 'ADA' },
    { symbol: 'DOT' }
  ];
}

export default async function StockChartPage({ 
  params 
}: { 
  params: Promise<{ symbol: string }> 
}) {
  const { symbol } = await params;
  
  return <StockChartClient symbol={symbol} />;
}