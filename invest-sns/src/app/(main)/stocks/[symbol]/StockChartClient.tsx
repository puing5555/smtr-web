'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import { ArrowLeft, TrendingUp, Users, Info } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { useInfluencersStore } from '@/stores/influencers';
import { getCoinId, COIN_MAPPING } from '@/lib/api/coingecko';

const SUPPORTED_SYMBOLS = ['BTC', 'ETH', 'XRP', 'SOL', 'ADA', 'DOT'];

// guru_tracker_v24 스타일 색상 적용
const SIGNAL_COLORS = {
  STRONG_BUY: '#34d399',
  BUY: '#86efac',
  POSITIVE: '#60a5fa', 
  HOLD: '#22d3ee',
  NEUTRAL: '#94a3b8',
  CONCERN: '#fdba74',
  SELL: '#fb923c',
  STRONG_SELL: '#f87171',
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

  // lightweight-charts 렌더링 (guru_tracker 도트 마커 스타일 적용)
  useEffect(() => {
    if (!chartContainerRef.current || chartData.length === 0) return;
    const container = chartContainerRef.current;
    let cancelled = false;
    let markerOverlayRef: HTMLDivElement | null = null;
    let markerTooltipRef: HTMLDivElement | null = null;
    let resizeObserver: ResizeObserver | null = null;

    (async () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.remove();
        chartInstanceRef.current = null;
      }

      // 기존 마커 오버레이 제거
      const existingOverlay = container.querySelector('.marker-overlay-container');
      if (existingOverlay) {
        existingOverlay.remove();
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

      // guru_tracker_v24 스타일 도트 마커 오버레이 생성
      markerOverlayRef = document.createElement('div');
      markerOverlayRef.className = 'marker-overlay-container';
      markerOverlayRef.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        overflow: hidden;
        z-index: 50;
      `;
      
      const svgContainer = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svgContainer.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 49;
      `;
      
      markerOverlayRef.appendChild(svgContainer);
      container.appendChild(markerOverlayRef);

      // 툴팁 생성
      markerTooltipRef = document.createElement('div');
      markerTooltipRef.className = 'marker-tooltip';
      markerTooltipRef.style.cssText = `
        position: absolute;
        z-index: 60;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 0;
        min-width: 300px;
        max-width: 400px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        pointer-events: auto;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.2s, visibility 0.2s;
      `;
      container.appendChild(markerTooltipRef);

      chart.timeScale().fitContent();
      chartInstanceRef.current = chart;

      // 도트 마커 생성 및 위치 업데이트 함수
      const createMarkerDots = () => {
        if (!markerOverlayRef || !svgContainer) return;
        
        // 기존 도트들 제거
        const existingDots = markerOverlayRef.querySelectorAll('.marker-dot');
        existingDots.forEach(dot => dot.remove());
        
        svgContainer.innerHTML = '';

        filteredSignals.forEach((signal, index) => {
          if (!signal.videoDate) return;

          // 도트 생성
          const dot = document.createElement('div');
          dot.className = `marker-dot type-${signal.signalType.toLowerCase().replace('_', '-')}`;
          dot.style.cssText = `
            position: absolute;
            pointer-events: auto;
            cursor: pointer;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 2px solid rgba(255,255,255,0.3);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            transition: transform 0.15s, box-shadow 0.15s;
            z-index: 51;
            background: ${SIGNAL_COLORS[signal.signalType as keyof typeof SIGNAL_COLORS] || '#94a3b8'};
          `;

          // SVG 대시 라인 생성
          const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
          line.setAttribute('stroke', SIGNAL_COLORS[signal.signalType as keyof typeof SIGNAL_COLORS] || '#94a3b8');
          line.setAttribute('stroke-width', '2');
          line.setAttribute('stroke-dasharray', '4,3');
          line.style.opacity = '0';
          line.style.transition = 'opacity 0.2s';
          svgContainer.appendChild(line);

          // 프리뷰 생성
          const preview = document.createElement('div');
          preview.className = 'dot-preview';
          preview.style.cssText = `
            position: absolute;
            z-index: 56;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 6px 10px;
            white-space: nowrap;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.15s;
            font-size: 12px;
            color: #374151;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          `;
          preview.innerHTML = `<span style="font-weight: 700; color: #3b82f6; margin-right: 6px;">${symbol}</span><span style="font-weight: 600;">${SIGNAL_LABELS[signal.signalType as keyof typeof SIGNAL_LABELS] || signal.signalType}</span>`;
          container.appendChild(preview);

          // 호버 이벤트
          dot.addEventListener('mouseenter', () => {
            dot.style.transform = 'scale(1.6)';
            dot.style.boxShadow = '0 0 12px rgba(59,130,246,0.3)';
            dot.style.zIndex = '55';
            line.style.opacity = '0.7';
            
            const rect = dot.getBoundingClientRect();
            const containerRect = container.getBoundingClientRect();
            preview.style.left = `${rect.left - containerRect.left + 12}px`;
            preview.style.top = `${rect.top - containerRect.top - 35}px`;
            preview.style.opacity = '1';
          });

          dot.addEventListener('mouseleave', () => {
            dot.style.transform = 'scale(1)';
            dot.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
            dot.style.zIndex = '51';
            line.style.opacity = '0';
            preview.style.opacity = '0';
          });

          // 클릭 이벤트 - 툴팁 표시
          dot.addEventListener('click', (e) => {
            e.stopPropagation();
            if (!markerTooltipRef) return;

            markerTooltipRef.innerHTML = `
              <button onclick="this.parentElement.style.opacity='0'; this.parentElement.style.visibility='hidden';" style="position: absolute; top: 10px; right: 12px; background: rgba(0,0,0,0.06); border: none; color: #6b7280; cursor: pointer; font-size: 14px; width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">✕</button>
              <div style="padding: 16px 18px 12px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #f3f4f6;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background: ${SIGNAL_COLORS[signal.signalType as keyof typeof SIGNAL_COLORS] || '#94a3b8'}; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 14px;">${signal.influencer.charAt(0)}</div>
                <div style="flex: 1;">
                  <div style="font-weight: 700; font-size: 15px; color: #111827;">${signal.influencer}</div>
                  <div style="font-size: 11px; color: #6b7280; margin-top: 1px;">${signal.videoDate}</div>
                </div>
                <span style="padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 800; color: white; background: ${SIGNAL_COLORS[signal.signalType as keyof typeof SIGNAL_COLORS] || '#94a3b8'};">${SIGNAL_LABELS[signal.signalType as keyof typeof SIGNAL_LABELS] || signal.signalType}</span>
              </div>
              <div style="padding: 14px 18px;">
                <div style="color: #374151; font-size: 13px; line-height: 1.6; margin-bottom: 14px; padding-left: 14px; border-left: 3px solid #3b82f6; border-radius: 2px;">${signal.content || '내용 없음'}</div>
                ${signal.youtubeLink ? `<a href="${signal.youtubeLink}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; color: #dc2626; font-size: 13px; text-decoration: none; padding: 8px 14px; background: rgba(220,38,38,0.08); border-radius: 10px; font-weight: 600;">▶ YouTube에서 보기</a>` : ''}
              </div>
            `;

            const rect = dot.getBoundingClientRect();
            const containerRect = container.getBoundingClientRect();
            markerTooltipRef.style.left = `${rect.left - containerRect.left + 15}px`;
            markerTooltipRef.style.top = `${rect.top - containerRect.top - 10}px`;
            markerTooltipRef.style.opacity = '1';
            markerTooltipRef.style.visibility = 'visible';
            
            line.style.opacity = '1';
          });

          markerOverlayRef.appendChild(dot);

          // 도트에 참조 저장 (위치 업데이트용)
          (dot as any)._signal = signal;
          (dot as any)._line = line;
          (dot as any)._preview = preview;
        });
      };

      // 도트 위치 업데이트 함수
      const updateDotPositions = () => {
        if (!markerOverlayRef) return;
        
        const dots = markerOverlayRef.querySelectorAll('.marker-dot');
        dots.forEach((dot) => {
          const signal = (dot as any)._signal;
          const line = (dot as any)._line;
          if (!signal || !signal.videoDate) return;

          try {
            const timeCoord = chart.timeScale().timeToCoordinate(signal.videoDate as any);
            if (timeCoord === null) {
              (dot as HTMLElement).style.display = 'none';
              if (line) line.style.display = 'none';
              return;
            }

            // 해당 날짜의 캔들 데이터 찾기
            const candleData = chartData.find(d => d.time === signal.videoDate) || 
                              chartData.find(d => Math.abs(new Date(d.time).getTime() - new Date(signal.videoDate).getTime()) < 24 * 60 * 60 * 1000) ||
                              chartData[Math.floor(chartData.length / 2)]; // fallback

            const priceCoord = series.priceToCoordinate(candleData.close);
            if (priceCoord === null) {
              (dot as HTMLElement).style.display = 'none';
              if (line) line.style.display = 'none';
              return;
            }

            const dotX = timeCoord - 6; // 도트 중심점 맞추기
            const dotY = priceCoord - 18 - 6; // 18px 위 + 도트 중심점

            (dot as HTMLElement).style.left = `${dotX}px`;
            (dot as HTMLElement).style.top = `${dotY}px`;
            (dot as HTMLElement).style.display = 'block';

            // SVG 라인 업데이트
            if (line) {
              line.setAttribute('x1', `${timeCoord}`);
              line.setAttribute('y1', `${priceCoord}`);
              line.setAttribute('x2', `${timeCoord}`);
              line.setAttribute('y2', `${dotY + 6}`);
              line.style.display = 'block';
            }
          } catch (error) {
            (dot as HTMLElement).style.display = 'none';
            if (line) line.style.display = 'none';
          }
        });
      };

      // 도트 생성
      createMarkerDots();
      updateDotPositions();

      // 차트 이벤트 구독
      chart.timeScale().subscribeVisibleLogicalRangeChange(updateDotPositions);

      // 툴팁 닫기 (전역 클릭)
      const closeTooltip = (e: MouseEvent) => {
        if (markerTooltipRef && !markerTooltipRef.contains(e.target as Node)) {
          markerTooltipRef.style.opacity = '0';
          markerTooltipRef.style.visibility = 'hidden';
          
          // 모든 라인 숨기기
          const svgLines = svgContainer.querySelectorAll('line');
          svgLines.forEach(line => {
            if (line.style.opacity === '1') {
              line.style.opacity = '0';
            }
          });
        }
      };
      document.addEventListener('click', closeTooltip);

      // 리사이즈 대응
      resizeObserver = new ResizeObserver(() => {
        if (chartInstanceRef.current && container.clientWidth > 0) {
          chartInstanceRef.current.applyOptions({
            width: container.clientWidth,
            height: Math.max(container.clientHeight, window.innerHeight - 300, 500),
          });
          setTimeout(updateDotPositions, 100);
        }
      });
      resizeObserver.observe(container);

      return () => {
        document.removeEventListener('click', closeTooltip);
      };
    })();

    return () => {
      cancelled = true;
      if (chartInstanceRef.current) {
        chartInstanceRef.current.remove();
        chartInstanceRef.current = null;
      }
      if (markerOverlayRef) {
        markerOverlayRef.remove();
      }
      if (markerTooltipRef) {
        markerTooltipRef.remove();
      }
      if (resizeObserver) {
        resizeObserver.disconnect();
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
          <div ref={chartContainerRef} style={{ width: '100%', height: 'calc(100vh - 280px)', minHeight: 400, position: 'relative' }} />
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
