'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import { ArrowLeft, TrendingUp, Users, Info } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { useInfluencersStore } from '@/stores/influencers';
import { getCoinId, COIN_MAPPING } from '@/lib/api/coingecko';

const SUPPORTED_SYMBOLS = ['BTC', 'ETH', 'XRP', 'SOL', 'ADA', 'DOT'];

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

export default function StockChartClient({ symbol }: { symbol: string }) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartInstanceRef = useRef<any>(null);
  
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedInfluencer, setSelectedInfluencer] = useState('ALL');
  const [selectedSignalType, setSelectedSignalType] = useState('ALL');

  const { signals, loadSignals } = useInfluencersStore();

  useEffect(() => { loadSignals(); }, [loadSignals]);

  const stockSignals = useMemo(() => {
    return signals.filter(s => s.stock === symbol || s.stockName === symbol);
  }, [signals, symbol]);

  const filteredSignals = useMemo(() => {
    let filtered = stockSignals;
    if (selectedInfluencer !== 'ALL') filtered = filtered.filter(s => s.influencer === selectedInfluencer);
    if (selectedSignalType !== 'ALL') filtered = filtered.filter(s => s.signalType === selectedSignalType);
    return filtered;
  }, [stockSignals, selectedInfluencer, selectedSignalType]);

  const influencers = useMemo(() => {
    return [...new Set(stockSignals.map(s => s.influencer))];
  }, [stockSignals]);

  const stockName = stockSignals[0]?.stockName || symbol;
  const isSupported = SUPPORTED_SYMBOLS.includes(symbol);

  // 차트 데이터 로드
  useEffect(() => {
    if (!isSupported) { setLoading(false); return; }
    (async () => {
      try {
        setLoading(true);
        const res = await fetch(`https://min-api.cryptocompare.com/data/v2/histoday?fsym=${symbol}&tsym=USD&limit=180`);
        const json = await res.json();
        if (json.Response === 'Error') throw new Error(json.Message);
        const data = (json.Data?.Data || []).map((d: any) => ({
          time: new Date(d.time * 1000).toISOString().split('T')[0],
          open: d.open, high: d.high, low: d.low, close: d.close,
        }));
        setChartData(data);
      } catch (err: any) {
        setError(err.message || '차트 데이터 로드 실패');
      } finally {
        setLoading(false);
      }
    })();
  }, [symbol, isSupported]);

  // lightweight-charts 렌더링
  useEffect(() => {
    if (!chartContainerRef.current || chartData.length === 0) return;
    const container = chartContainerRef.current;
    let cancelled = false;

    (async () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.remove();
        chartInstanceRef.current = null;
      }

      const { createChart, ColorType } = await import('lightweight-charts');
      if (cancelled) return;

      const w = container.clientWidth || 800;
      const h = Math.max(container.clientHeight, window.innerHeight - 300, 500);

      const chart = createChart(container, {
        width: w,
        height: h,
        layout: {
          background: { type: ColorType.Solid, color: '#ffffff' },
          textColor: '#333',
        },
        grid: {
          vertLines: { color: '#f0f0f0' },
          horzLines: { color: '#f0f0f0' },
        },
        rightPriceScale: { borderColor: '#ddd' },
        timeScale: { borderColor: '#ddd', timeVisible: false },
      });

      const series = chart.addCandlestickSeries({
        upColor: '#22c55e',
        downColor: '#ef4444',
        borderUpColor: '#16a34a',
        borderDownColor: '#dc2626',
        wickUpColor: '#16a34a',
        wickDownColor: '#dc2626',
      });

      series.setData(chartData.map(d => ({
        time: d.time as string,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      })));

      // 시그널 마커 추가 (v4 API)
      const markers = filteredSignals
        .filter(s => s.videoDate)
        .map(signal => {
          const isBuy = ['STRONG_BUY', 'BUY', 'POSITIVE'].includes(signal.signalType);
          return {
            time: signal.videoDate as string,
            position: isBuy ? 'belowBar' : 'aboveBar' as any,
            color: SIGNAL_COLORS[signal.signalType as keyof typeof SIGNAL_COLORS] || '#9ca3af',
            shape: isBuy ? 'arrowUp' : 'arrowDown' as any,
            text: `${signal.influencer}: ${SIGNAL_LABELS[signal.signalType as keyof typeof SIGNAL_LABELS] || signal.signalType}`,
            size: 2,
          };
        })
        .sort((a: any, b: any) => a.time.localeCompare(b.time));

      if (markers.length > 0) {
        series.setMarkers(markers as any);
      }

      chart.timeScale().fitContent();
      chartInstanceRef.current = chart;

      // 리사이즈 대응
      const ro = new ResizeObserver(() => {
        if (chartInstanceRef.current && container.clientWidth > 0) {
          chartInstanceRef.current.applyOptions({
            width: container.clientWidth,
            height: Math.max(container.clientHeight, window.innerHeight - 300, 500),
          });
        }
      });
      ro.observe(container);
    })();

    return () => {
      cancelled = true;
      if (chartInstanceRef.current) {
        chartInstanceRef.current.remove();
        chartInstanceRef.current = null;
      }
    };
  }, [chartData, filteredSignals]);

  if (!isSupported) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Link href="/influencers" className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6">
          <ArrowLeft className="w-4 h-4" />뒤로가기
        </Link>
        <div className="text-center py-12">
          <p className="text-gray-500">지원하지 않는 종목입니다.</p>
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
            <ArrowLeft className="w-4 h-4" />뒤로가기
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{stockName}</h1>
            <p className="text-sm text-gray-500">{symbol}/USD</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Users className="w-4 h-4" />{stockSignals.length}개 시그널
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <TrendingUp className="w-4 h-4" />{influencers.length}명 인플루언서
          </div>
        </div>
      </div>

      {/* 필터 */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex flex-wrap gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">인플루언서</label>
            <div className="flex flex-wrap gap-2">
              <button onClick={() => setSelectedInfluencer('ALL')}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${selectedInfluencer === 'ALL' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
                전체 ({stockSignals.length})
              </button>
              {influencers.map(inf => {
                const count = stockSignals.filter(s => s.influencer === inf).length;
                return (
                  <button key={inf} onClick={() => setSelectedInfluencer(inf)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${selectedInfluencer === inf ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
                    {inf} ({count})
                  </button>
                );
              })}
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">시그널 타입</label>
            <div className="flex flex-wrap gap-2">
              <button onClick={() => setSelectedSignalType('ALL')}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${selectedSignalType === 'ALL' ? 'bg-purple-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
                전체
              </button>
              {Object.entries(SIGNAL_LABELS).map(([type, label]) => {
                const count = stockSignals.filter(s => s.signalType === type).length;
                if (count === 0) return null;
                return (
                  <button key={type} onClick={() => setSelectedSignalType(type)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${selectedSignalType === type ? 'text-white' : 'text-gray-700 hover:bg-gray-200'}`}
                    style={{ backgroundColor: selectedSignalType === type ? SIGNAL_COLORS[type as keyof typeof SIGNAL_COLORS] : undefined }}>
                    {label} ({count})
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* 차트 영역 - lightweight-charts + 시그널 마커 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {loading ? (
          <div style={{ height: 'calc(100vh - 280px)', minHeight: 400 }} className="flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-500">차트 로딩중...</p>
            </div>
          </div>
        ) : error ? (
          <div style={{ height: 'calc(100vh - 280px)', minHeight: 400 }} className="flex items-center justify-center">
            <p className="text-red-500">{error}</p>
          </div>
        ) : (
          <div ref={chartContainerRef} style={{ width: '100%', height: 'calc(100vh - 280px)', minHeight: 400 }} />
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
                <Badge className="text-white text-xs font-bold shrink-0"
                  style={{ backgroundColor: SIGNAL_COLORS[signal.signalType as keyof typeof SIGNAL_COLORS] }}>
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
                    <a href={signal.youtubeLink} target="_blank" rel="noopener noreferrer"
                      className="text-red-600 hover:text-red-700 text-xs font-medium">
                      YouTube에서 보기 →
                    </a>
                  )}
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
