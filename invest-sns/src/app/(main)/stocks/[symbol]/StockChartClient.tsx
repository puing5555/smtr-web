'use client';

import { useState, useEffect, use, useRef, useMemo } from 'react';
import { ArrowLeft, TrendingUp, Users, Filter, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { useInfluencersStore } from '@/stores/influencers';
import { coinGeckoAPI, getCoinId, COIN_MAPPING } from '@/lib/api/coingecko';
import { createChart, ColorType, IChartApi, ISeriesApi, CandlestickData, Time } from 'lightweight-charts';

const SIGNAL_COLORS = {
  STRONG_BUY: '#16a34a',
  BUY: '#22c55e', 
  POSITIVE: '#86efac',
  HOLD: '#eab308',
  NEUTRAL: '#9ca3af',
  CONCERN: '#f97316',
  SELL: '#ef4444',
  STRONG_SELL: '#dc2626',
} as const;

const SIGNAL_LABELS = {
  STRONG_BUY: '적극매수',
  BUY: '매수',
  POSITIVE: '긍정',
  HOLD: '보유', 
  NEUTRAL: '중립',
  CONCERN: '우려',
  SELL: '매도',
  STRONG_SELL: '적극매도',
} as const;

interface ChartData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface SignalMarker {
  time: string;
  position: 'aboveBar' | 'belowBar';
  color: string;
  shape: 'circle' | 'square' | 'arrowUp' | 'arrowDown';
  text: string;
  size: number;
  signal: any;
}

export default function StockChartClient({ symbol }: { symbol: string }) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedInfluencer, setSelectedInfluencer] = useState('ALL');
  const [selectedSignalType, setSelectedSignalType] = useState('ALL');
  const [tooltip, setTooltip] = useState<{ visible: boolean; x: number; y: number; content: string }>({
    visible: false, x: 0, y: 0, content: ''
  });

  const { signals, loadSignals } = useInfluencersStore();

  useEffect(() => {
    loadSignals();
  }, [loadSignals]);

  // 해당 종목의 시그널들 필터링
  const stockSignals = useMemo(() => {
    return signals.filter(s => s.stock === symbol || s.stockName === symbol);
  }, [signals, symbol]);

  // 필터링된 시그널들
  const filteredSignals = useMemo(() => {
    let filtered = stockSignals;
    
    if (selectedInfluencer !== 'ALL') {
      filtered = filtered.filter(s => s.influencer === selectedInfluencer);
    }
    
    if (selectedSignalType !== 'ALL') {
      filtered = filtered.filter(s => s.signalType === selectedSignalType);
    }
    
    return filtered;
  }, [stockSignals, selectedInfluencer, selectedSignalType]);

  // 인플루언서 목록
  const influencers = useMemo(() => {
    const uniqueInfluencers = [...new Set(stockSignals.map(s => s.influencer))];
    return uniqueInfluencers;
  }, [stockSignals]);

  // CoinGecko ID 가져오기
  const coinId = getCoinId(symbol);
  const stockName = stockSignals[0]?.stockName || symbol;

  // 차트 데이터 로드
  useEffect(() => {
    const loadChartData = async () => {
      if (!coinId) {
        setError('지원하지 않는 종목입니다.');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        // 최근 90일 OHLC 데이터 가져오기
        const response = await fetch(
          `https://api.coingecko.com/api/v3/coins/${coinId}/ohlc?vs_currency=usd&days=90`
        );

        if (!response.ok) {
          throw new Error('차트 데이터를 가져올 수 없습니다.');
        }

        const ohlcData = await response.json();
        
        const formattedData: ChartData[] = ohlcData.map((item: number[]) => ({
          time: new Date(item[0]).toISOString().split('T')[0],
          open: item[1],
          high: item[2], 
          low: item[3],
          close: item[4],
        }));

        setChartData(formattedData);
      } catch (err) {
        console.error('차트 데이터 로드 오류:', err);
        setError(err instanceof Error ? err.message : '차트 데이터를 가져올 수 없습니다.');
      } finally {
        setLoading(false);
      }
    };

    loadChartData();
  }, [coinId]);

  // 차트 초기화 및 업데이트
  useEffect(() => {
    if (!chartContainerRef.current || chartData.length === 0) return;

    // 기존 차트 정리
    if (chartRef.current) {
      chartRef.current.remove();
    }

    // 새 차트 생성
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 500,
      layout: {
        background: { type: ColorType.Solid, color: 'white' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      rightPriceScale: {
        borderColor: '#cccccc',
      },
      timeScale: {
        borderColor: '#cccccc',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    // 캔들스틱 시리즈 추가
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444', 
      borderUpColor: '#16a34a',
      borderDownColor: '#dc2626',
      wickUpColor: '#16a34a',
      wickDownColor: '#dc2626',
    });

    // 차트 데이터 설정
    const chartPoints: CandlestickData[] = chartData.map(item => ({
      time: item.time as Time,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    }));

    candlestickSeries.setData(chartPoints);

    // 시그널 마커 추가
    const markers = filteredSignals.map(signal => {
      const signalColor = SIGNAL_COLORS[signal.signalType as keyof typeof SIGNAL_COLORS] || '#9ca3af';
      const isBuySignal = ['STRONG_BUY', 'BUY', 'POSITIVE'].includes(signal.signalType);
      
      return {
        time: signal.videoDate as Time,
        position: isBuySignal ? 'belowBar' : 'aboveBar' as const,
        color: signalColor,
        shape: isBuySignal ? 'arrowUp' : 'arrowDown' as const,
        text: SIGNAL_LABELS[signal.signalType as keyof typeof SIGNAL_LABELS] || signal.signalType,
        size: 1,
        id: signal.id,
      };
    });

    candlestickSeries.setMarkers(markers);

    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;

    // 차트 클릭 이벤트 (마커 툴팁)
    chart.subscribeClick((param) => {
      if (param.point && param.time) {
        const clickedSignals = filteredSignals.filter(s => s.videoDate === param.time);
        if (clickedSignals.length > 0) {
          const signal = clickedSignals[0];
          setTooltip({
            visible: true,
            x: param.point.x,
            y: param.point.y,
            content: `${signal.influencer}: ${signal.content.slice(0, 100)}...`
          });
          
          setTimeout(() => setTooltip(prev => ({ ...prev, visible: false })), 3000);
        }
      }
    });

    // 반응형 처리
    const resizeObserver = new ResizeObserver(entries => {
      if (entries.length === 0 || !chartRef.current) return;
      const newRect = entries[0].contentRect;
      chartRef.current.applyOptions({ width: newRect.width });
    });

    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  }, [chartData, filteredSignals]);

  if (!coinId) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Link href="/influencers" className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6">
          <ArrowLeft className="w-4 h-4" />
          뒤로가기
        </Link>
        <div className="text-center py-12">
          <p className="text-gray-500">지원하지 않는 종목입니다.</p>
          <p className="text-sm text-gray-400 mt-2">현재 지원 종목: {Object.keys(COIN_MAPPING).filter(k => COIN_MAPPING[k]).join(', ')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/influencers" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
            <ArrowLeft className="w-4 h-4" />
            뒤로가기
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{stockName}</h1>
            <p className="text-sm text-gray-500">{symbol} • CoinGecko ID: {coinId}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Users className="w-4 h-4" />
            {stockSignals.length}개 시그널
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <TrendingUp className="w-4 h-4" />
            {influencers.length}명 인플루언서
          </div>
        </div>
      </div>

      {/* 필터 */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex flex-wrap gap-4">
          {/* 인플루언서 필터 */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">인플루언서</label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedInfluencer('ALL')}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  selectedInfluencer === 'ALL' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                전체 ({stockSignals.length})
              </button>
              {influencers.map(influencer => {
                const count = stockSignals.filter(s => s.influencer === influencer).length;
                return (
                  <button
                    key={influencer}
                    onClick={() => setSelectedInfluencer(influencer)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      selectedInfluencer === influencer
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {influencer} ({count})
                  </button>
                );
              })}
            </div>
          </div>

          {/* 시그널 타입 필터 */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">시그널 타입</label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedSignalType('ALL')}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  selectedSignalType === 'ALL'
                    ? 'bg-purple-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                전체
              </button>
              {Object.entries(SIGNAL_LABELS).map(([type, label]) => {
                const count = stockSignals.filter(s => s.signalType === type).length;
                if (count === 0) return null;
                
                return (
                  <button
                    key={type}
                    onClick={() => setSelectedSignalType(type)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      selectedSignalType === type
                        ? 'text-white'
                        : 'text-gray-700 hover:bg-gray-200'
                    }`}
                    style={{
                      backgroundColor: selectedSignalType === type ? SIGNAL_COLORS[type as keyof typeof SIGNAL_COLORS] : undefined
                    }}
                  >
                    {label} ({count})
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* 차트 영역 */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        {loading ? (
          <div className="h-[500px] flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-500">차트 데이터 로딩중...</p>
            </div>
          </div>
        ) : error ? (
          <div className="h-[500px] flex items-center justify-center">
            <div className="text-center">
              <p className="text-red-500 mb-2">{error}</p>
              <Button onClick={() => window.location.reload()} variant="outline" size="sm">
                다시 시도
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">가격 차트</h3>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Info className="w-4 h-4" />
                마커를 클릭하면 상세 정보를 확인할 수 있습니다
              </div>
            </div>
            <div ref={chartContainerRef} className="relative h-[500px]" />
          </div>
        )}
      </div>

      {/* 시그널 목록 */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <h3 className="text-lg font-semibold mb-4">시그널 목록 ({filteredSignals.length}개)</h3>
        <div className="space-y-3 max-h-80 overflow-y-auto">
          {filteredSignals
            .sort((a, b) => new Date(b.videoDate).getTime() - new Date(a.videoDate).getTime())
            .map(signal => (
              <div key={signal.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <Badge 
                  className="text-white text-xs font-bold shrink-0"
                  style={{ backgroundColor: SIGNAL_COLORS[signal.signalType as keyof typeof SIGNAL_COLORS] }}
                >
                  {SIGNAL_LABELS[signal.signalType as keyof typeof SIGNAL_LABELS]}
                </Badge>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-gray-900">{signal.influencer}</span>
                    <span className="text-sm text-gray-500">{signal.videoDate}</span>
                    <span className="text-xs text-gray-400">{signal.timestamp}</span>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{signal.content}</p>
                  {signal.youtubeLink && (
                    <a
                      href={signal.youtubeLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-red-600 hover:text-red-700 text-xs font-medium"
                    >
                      YouTube에서 보기 →
                    </a>
                  )}
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* 툴팁 */}
      {tooltip.visible && (
        <div 
          className="fixed bg-black text-white text-sm p-2 rounded shadow-lg z-50 max-w-xs"
          style={{ left: tooltip.x, top: tooltip.y - 10 }}
        >
          {tooltip.content}
        </div>
      )}
    </div>
  );
}