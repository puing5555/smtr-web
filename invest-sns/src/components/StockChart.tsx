'use client';

import { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, IChartApi, ISeriesApi, LineData, UTCTimestamp } from 'lightweight-charts';
import { getCoinId, formatReturn, getReturnColor } from '@/lib/api/coingecko';

interface Signal {
  id: number;
  influencer: string;
  stock: string;
  stockName: string;
  signalType: 'STRONG_BUY' | 'BUY' | 'POSITIVE' | 'HOLD' | 'NEUTRAL' | 'CONCERN' | 'SELL' | 'STRONG_SELL';
  content: string;
  timestamp: string;
  price: number;
  youtubeLink?: string;
  analysis: {
    summary: string;
    detail: string;
  };
  videoDate: string;
  videoTitle?: string;
  confidence?: string;
  timeframe?: string;
  conditional?: boolean;
  skinInGame?: boolean;
  context?: string;
  videoSummary?: string;
}

interface StockChartProps {
  stockName: string;
  signals: Signal[];
  className?: string;
}

interface MarkerData {
  time: UTCTimestamp;
  position: 'aboveBar' | 'belowBar' | 'inBar';
  color: string;
  shape: 'circle' | 'square' | 'arrowUp' | 'arrowDown';
  size: number;
  text?: string;
  signal: Signal;
}

// 시그널 타입별 색상 매핑 (라이트 테마)
const SIGNAL_COLORS: Record<string, string> = {
  'STRONG_BUY': '#16a34a', // green-600
  'BUY': '#22c55e', // green-500  
  'POSITIVE': '#3b82f6', // blue-500
  'HOLD': '#06b6d4', // cyan-500
  'NEUTRAL': '#6b7280', // gray-500
  'CONCERN': '#f59e0b', // amber-500
  'SELL': '#ea580c', // orange-600
  'STRONG_SELL': '#dc2626', // red-600
};

// 시그널 타입별 한글명
const SIGNAL_NAMES: Record<string, string> = {
  'STRONG_BUY': '강력매수',
  'BUY': '매수',
  'POSITIVE': '긍정적',
  'HOLD': '보유',
  'NEUTRAL': '중립',
  'CONCERN': '우려',
  'SELL': '매도',
  'STRONG_SELL': '강력매도',
};

// 가격 데이터 생성 (모의 데이터 또는 실제 API 데이터)
function generatePriceData(stockName: string, days: number = 365): LineData[] {
  // CoinGecko ID 확인
  const coinId = getCoinId(stockName);
  
  // TODO: 실제 CoinGecko API를 사용한 가격 데이터 가져오기
  // 현재는 모의 데이터를 사용
  
  const data: LineData[] = [];
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  
  let price = 100 + Math.random() * 50; // 시작 가격
  
  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    
    // 주말 제외
    if (date.getDay() === 0 || date.getDay() === 6) continue;
    
    // 가격 변동 (-3% ~ +3%)
    const change = (Math.random() - 0.5) * 0.06;
    price = price * (1 + change);
    
    data.push({
      time: (date.getTime() / 1000) as UTCTimestamp,
      value: Math.round(price * 100) / 100,
    });
  }
  
  return data;
}

export default function StockChart({ stockName, signals, className = '' }: StockChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<number>(0); // 0: 전체, 1: 1개월, 6: 6개월, 12: 1년, 36: 3년
  const [currentPrice, setCurrentPrice] = useState<number | null>(null);
  const [priceChange, setPriceChange] = useState<number | null>(null);
  const [selectedMarker, setSelectedMarker] = useState<Signal | null>(null);

  const [chartError, setChartError] = useState<string | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    try {
    // 차트 생성 (라이트 테마)
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#374151', // gray-700
        fontSize: 12,
        fontFamily: '"Noto Sans KR", sans-serif',
      },
      grid: {
        vertLines: { color: '#f3f4f6' }, // gray-100
        horzLines: { color: '#f3f4f6' }, // gray-100
      },
      crosshair: {
        mode: 0, // Normal
        vertLine: {
          color: '#9ca3af', // gray-400
          width: 1,
          style: 2, // Dashed
        },
        horzLine: {
          color: '#9ca3af', // gray-400
          width: 1,
          style: 2, // Dashed
        },
      },
      rightPriceScale: {
        borderColor: '#e5e7eb', // gray-200
        textColor: '#6b7280', // gray-500
      },
      timeScale: {
        borderColor: '#e5e7eb', // gray-200
        textColor: '#6b7280', // gray-500
        timeVisible: true,
        secondsVisible: false,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
    });

    // 라인 시리즈 생성
    const series = chart.addLineSeries({
      color: '#3b82f6', // blue-500
      lineWidth: 2,
      lastValueVisible: true,
      priceLineVisible: true,
      crosshairMarkerVisible: true,
      priceLineColor: '#3b82f6',
      priceLineWidth: 1,
      priceLineStyle: 2, // Dashed
    });

    chartRef.current = chart;
    seriesRef.current = series;

    // 시그널 중 가장 오래된 날짜 기준으로 데이터 기간 결정
    const oldestSignalDate = signals.length > 0
      ? Math.min(...signals.map(s => new Date(s.videoDate).getTime()))
      : Date.now() - 365 * 86400000;
    const daysSinceOldest = Math.max(365, Math.ceil((Date.now() - oldestSignalDate) / 86400000) + 60);
    const priceData = generatePriceData(stockName, daysSinceOldest);
    series.setData(priceData);

    // 현재 가격 설정
    if (priceData.length > 0) {
      const lastPrice = priceData[priceData.length - 1].value;
      const prevPrice = priceData.length > 1 ? priceData[priceData.length - 2].value : lastPrice;
      setCurrentPrice(lastPrice);
      setPriceChange(((lastPrice - prevPrice) / prevPrice) * 100);
    }

    // 전체 기간 표시
    chart.timeScale().fitContent();

    // 시그널 마커 생성
    const markers: MarkerData[] = signals.map((signal) => {
      const signalDate = new Date(signal.videoDate);
      const timestamp = (signalDate.getTime() / 1000) as UTCTimestamp;
      
      return {
        time: timestamp,
        position: 'aboveBar',
        color: SIGNAL_COLORS[signal.signalType] || '#6b7280',
        shape: signal.signalType.includes('BUY') ? 'arrowUp' : 
               signal.signalType.includes('SELL') ? 'arrowDown' : 'circle',
        size: 1,
        text: signal.influencer.substring(0, 2),
        signal,
      };
    });

    // 마커 설정
    if (markers.length > 0) {
      series.setMarkers(markers as any);
    }

    // 클릭 이벤트 처리
    chart.subscribeClick((param) => {
      if (param.point && param.time) {
        // 해당 시점의 시그널 찾기
        const clickTime = param.time as number;
        const clickedSignal = signals.find(signal => {
          const signalTime = new Date(signal.videoDate).getTime() / 1000;
          return Math.abs(signalTime - clickTime) < 86400; // 1일 오차 허용
        });
        
        if (clickedSignal) {
          setSelectedMarker(clickedSignal);
        } else {
          setSelectedMarker(null);
        }
      }
    });

    // 반응형 처리
    const handleResize = () => {
      if (chartContainerRef.current && chart) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
    } catch (err) {
      console.error('Chart error:', err);
      setChartError(err instanceof Error ? err.message : 'Chart failed to load');
    }
  }, [stockName, signals]);

  // 기간 필터 적용
  const applyPeriodFilter = (months: number) => {
    if (!chartRef.current) return;
    
    setSelectedPeriod(months);
    
    if (months === 0) {
      // 전체 기간
      chartRef.current.timeScale().fitContent();
    } else {
      // 특정 기간
      const now = new Date();
      const from = new Date();
      from.setMonth(from.getMonth() - months);
      
      chartRef.current.timeScale().setVisibleRange({
        from: (from.getTime() / 1000) as UTCTimestamp,
        to: (now.getTime() / 1000) as UTCTimestamp,
      });
    }
  };

  if (chartError) {
    return (
      <div className={`bg-white rounded-xl border border-red-200 p-6 text-center ${className}`}>
        <p className="text-red-500 text-sm">차트를 불러올 수 없습니다: {chartError}</p>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl border border-gray-200 overflow-hidden ${className}`}>
      {/* 헤더 */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div>
            <h3 className="text-lg font-bold text-gray-900">{stockName}</h3>
            <div className="flex items-center gap-2 mt-1">
              {currentPrice && (
                <span className="text-2xl font-bold text-gray-900">
                  ${currentPrice.toFixed(2)}
                </span>
              )}
              {priceChange !== null && (
                <span className={`text-sm font-semibold ${getReturnColor(priceChange)}`}>
                  {formatReturn(priceChange)}
                </span>
              )}
            </div>
          </div>
          <div className="text-xs text-gray-500">
            📌 시그널 {signals.length}건 • 클릭하여 상세보기
          </div>
        </div>
        
        {/* 기간 버튼 */}
        <div className="flex gap-2 mt-3">
          {[
            { label: '1개월', value: 1 },
            { label: '6개월', value: 6 },
            { label: '1년', value: 12 },
            { label: '3년', value: 36 },
            { label: '전체', value: 0 },
          ].map((period) => (
            <button
              key={period.value}
              onClick={() => applyPeriodFilter(period.value)}
              className={`px-3 py-1 text-xs rounded-full font-medium transition-colors ${
                selectedPeriod === period.value
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {period.label}
            </button>
          ))}
        </div>
      </div>

      {/* 차트 */}
      <div className="relative">
        <div ref={chartContainerRef} className="w-full h-[400px]" />
        
        {/* 마커 툴팁 */}
        {selectedMarker && (
          <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-w-sm z-10">
            <button
              onClick={() => setSelectedMarker(null)}
              className="absolute top-2 right-2 w-6 h-6 rounded-full hover:bg-gray-100 flex items-center justify-center text-gray-400"
            >
              ✕
            </button>
            
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center font-bold text-sm">
                {selectedMarker.influencer.substring(0, 2)}
              </div>
              <div>
                <div className="font-bold text-gray-900">{selectedMarker.influencer}</div>
                <div className="text-xs text-gray-500">
                  {new Date(selectedMarker.videoDate).toLocaleDateString('ko-KR')}
                </div>
              </div>
              <span 
                className="px-2 py-1 rounded-full text-xs font-bold text-white"
                style={{ backgroundColor: SIGNAL_COLORS[selectedMarker.signalType] || '#6b7280' }}
              >
                {SIGNAL_NAMES[selectedMarker.signalType] || selectedMarker.signalType}
              </span>
            </div>
            
            <div className="text-sm text-gray-700 mb-3 leading-relaxed border-l-3 pl-3"
                 style={{ borderLeftColor: SIGNAL_COLORS[selectedMarker.signalType] || '#6b7280' }}>
              {selectedMarker.content}
            </div>
            
            {selectedMarker.youtubeLink && (
              <a
                href={selectedMarker.youtubeLink}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-red-600 text-sm font-semibold hover:text-red-700 transition-colors"
              >
                ▶ YouTube 타임스탬프로 이동
              </a>
            )}
            
            <div className="text-xs text-gray-400 mt-2">
              시그널 #{selectedMarker.id}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}