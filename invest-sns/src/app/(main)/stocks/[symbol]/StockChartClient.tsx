'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import { ArrowLeft, TrendingUp, Users, Info } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { useInfluencersStore } from '@/stores/influencers';
import { getCoinId, COIN_MAPPING } from '@/lib/api/coingecko';

// CryptoCompare 심볼 (한국에서도 접속 가능)
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

// TradingView 심볼 매핑
const TV_SYMBOLS: Record<string, string> = {
  BTC: 'BINANCE:BTCUSDT',
  ETH: 'BINANCE:ETHUSDT',
  XRP: 'BINANCE:XRPUSDT',
  SOL: 'BINANCE:SOLUSDT',
  ADA: 'BINANCE:ADAUSDT',
  DOT: 'BINANCE:DOTUSDT',
};

export default function StockChartClient({ symbol }: { symbol: string }) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  
  const [selectedInfluencer, setSelectedInfluencer] = useState('ALL');
  const [selectedSignalType, setSelectedSignalType] = useState('ALL');

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

  const stockName = stockSignals[0]?.stockName || symbol;
  const isSupported = SUPPORTED_SYMBOLS.includes(symbol);
  const tvSymbol = TV_SYMBOLS[symbol] || `BINANCE:${symbol}USDT`;

  // TradingView 위젯 삽입
  useEffect(() => {
    if (!chartContainerRef.current || !isSupported) return;
    const container = chartContainerRef.current;
    container.innerHTML = '';

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: tvSymbol,
      interval: 'D',
      timezone: 'Asia/Seoul',
      theme: 'light',
      style: '1',
      locale: 'kr',
      hide_top_toolbar: false,
      hide_legend: false,
      allow_symbol_change: false,
      save_image: false,
      calendar: false,
      hide_volume: false,
      support_host: 'https://www.tradingview.com',
    });

    const widgetDiv = document.createElement('div');
    widgetDiv.className = 'tradingview-widget-container__widget';
    widgetDiv.style.height = '100%';
    widgetDiv.style.width = '100%';

    container.appendChild(widgetDiv);
    container.appendChild(script);

    return () => {
      container.innerHTML = '';
    };
  }, [tvSymbol, isSupported]);

  if (!isSupported) {
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
            <p className="text-sm text-gray-500">{symbol}/USD</p>
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

      {/* 차트 영역 - TradingView 위젯 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div ref={chartContainerRef} className="tradingview-widget-container w-full" style={{ height: 400 }} />
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

    </div>
  );
}