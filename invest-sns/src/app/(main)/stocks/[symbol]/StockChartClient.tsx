'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import { ArrowLeft, TrendingUp, Users, Info } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { useInfluencersStore } from '@/stores/influencers';
import { getCoinId, COIN_MAPPING } from '@/lib/api/coingecko';

// 종목별 데이터 소스 매핑 (확장된 버전)
interface SymbolMapping {
  type: 'crypto' | 'stock' | 'category';
  symbol: string;
  source: 'cryptocompare' | 'yahoo' | 'coingecko' | 'none';
}

const SYMBOL_MAPPING: Record<string, SymbolMapping> = {
  // 암호화폐 (CryptoCompare)
  '비트코인': { type: 'crypto', symbol: 'BTC', source: 'cryptocompare' },
  'BTC': { type: 'crypto', symbol: 'BTC', source: 'cryptocompare' },
  '이더리움': { type: 'crypto', symbol: 'ETH', source: 'cryptocompare' },
  'ETH': { type: 'crypto', symbol: 'ETH', source: 'cryptocompare' },
  'XRP': { type: 'crypto', symbol: 'XRP', source: 'cryptocompare' },
  '리플': { type: 'crypto', symbol: 'XRP', source: 'cryptocompare' },
  '솔라나': { type: 'crypto', symbol: 'SOL', source: 'cryptocompare' },
  'SOL': { type: 'crypto', symbol: 'SOL', source: 'cryptocompare' },
  'BNB': { type: 'crypto', symbol: 'BNB', source: 'cryptocompare' },
  '체인링크': { type: 'crypto', symbol: 'LINK', source: 'cryptocompare' },
  'LINK': { type: 'crypto', symbol: 'LINK', source: 'cryptocompare' },
  '모네로': { type: 'crypto', symbol: 'XMR', source: 'cryptocompare' },
  'XMR': { type: 'crypto', symbol: 'XMR', source: 'cryptocompare' },
  '월드코인': { type: 'crypto', symbol: 'WLD', source: 'cryptocompare' },
  'WLD': { type: 'crypto', symbol: 'WLD', source: 'cryptocompare' },
  'CC': { type: 'crypto', symbol: 'CC', source: 'cryptocompare' },
  '캔톤네트워크': { type: 'crypto', symbol: 'CC', source: 'cryptocompare' },
  '캐톤네트워크': { type: 'crypto', symbol: 'CC', source: 'cryptocompare' },
  'PENGU': { type: 'crypto', symbol: 'PENGU', source: 'cryptocompare' },

  // 미국 주식 (Yahoo Finance)
  'MSTR': { type: 'stock', symbol: 'MSTR', source: 'yahoo' },
  'NVDA': { type: 'stock', symbol: 'NVDA', source: 'yahoo' },
  'PLTR': { type: 'stock', symbol: 'PLTR', source: 'yahoo' },
  'GOOGL': { type: 'stock', symbol: 'GOOGL', source: 'yahoo' },
  'ATNF': { type: 'stock', symbol: 'ATNF', source: 'yahoo' },
  'BMNR': { type: 'stock', symbol: 'BMNR', source: 'yahoo' },
  'CNTN': { type: 'stock', symbol: 'CNTN', source: 'yahoo' },
  'THAR': { type: 'stock', symbol: 'THAR', source: 'yahoo' },
  '알파벳': { type: 'stock', symbol: 'GOOGL', source: 'yahoo' },
  '엔비디아': { type: 'stock', symbol: 'NVDA', source: 'yahoo' },
  '마이크로스트래티지': { type: 'stock', symbol: 'MSTR', source: 'yahoo' },
  
  // 일본/기타 주식 (Yahoo Finance)
  'SBI': { type: 'stock', symbol: '8473.T', source: 'yahoo' },
  'SBI 홀딩스': { type: 'stock', symbol: '8473.T', source: 'yahoo' },

  // 한국 주식 (Yahoo Finance .KS/.KQ)
  '오뚜기': { type: 'stock', symbol: '007310.KS', source: 'yahoo' },
  '율촌화학': { type: 'stock', symbol: '008730.KS', source: 'yahoo' },
  'SK': { type: 'stock', symbol: '034730.KS', source: 'yahoo' },
  '코스피': { type: 'stock', symbol: '^KS11', source: 'yahoo' },
  
  // 기타 (상장 안됨/매핑 가능한 것들)
  '라이나스 희토류': { type: 'stock', symbol: 'LYC.AX', source: 'yahoo' }, // 호주

  // 카테고리/차트 불가
  '알트코인': { type: 'category', symbol: '', source: 'none' },
  '스테이블코인': { type: 'category', symbol: '', source: 'none' },
  '암호화폐': { type: 'category', symbol: '', source: 'none' },
  '기술주': { type: 'category', symbol: '', source: 'none' },
  '미국 주식': { type: 'category', symbol: '', source: 'none' },
  '금': { type: 'category', symbol: '', source: 'none' },
  'WLFI': { type: 'crypto', symbol: 'WLFI', source: 'coingecko' },
  '월드리버티파이낸셜': { type: 'crypto', symbol: 'WLFI', source: 'coingecko' },
  '월드리버티파이낸셜 (WLFI)': { type: 'crypto', symbol: 'WLFI', source: 'coingecko' },
  '블리시': { type: 'category', symbol: '', source: 'none' },
  '샤프링크': { type: 'category', symbol: '', source: 'none' },
  'ChatGPT': { type: 'category', symbol: '', source: 'none' },
  'Circle': { type: 'category', symbol: '', source: 'none' }, // CRCL 아직 상장 안됨
  '삼성ENA': { type: 'category', symbol: '', source: 'none' }, // 정확한 티커 불명
};

function getSymbolMapping(sym: string): SymbolMapping | null {
  // 직접 매핑
  if (SYMBOL_MAPPING[sym]) return SYMBOL_MAPPING[sym];
  
  // 괄호 안 티커 추출: "캔톤네트워크 (CC)" → CC
  const match = sym.match(/\(([^)]+)\)/);
  if (match) {
    const ticker = match[1];
    if (SYMBOL_MAPPING[ticker]) return SYMBOL_MAPPING[ticker];
    // 매핑에 없는 티커는 주식으로 가정하고 시도
    return { type: 'stock', symbol: ticker, source: 'yahoo' };
  }
  
  // 매핑에 없는 경우 주식으로 가정
  return { type: 'stock', symbol: sym, source: 'yahoo' };
}

// guru_tracker_v24 스타일 색상 - 8가지 시그널별 뚜렷한 색상
const SIGNAL_COLORS = {
  STRONG_BUY: '#10b981',  // 진한 에메랄드
  BUY: '#22c55e',          // 초록
  POSITIVE: '#3b82f6',     // 파랑
  HOLD: '#06b6d4',         // 시안
  NEUTRAL: '#6b7280',      // 회색
  CONCERN: '#f59e0b',      // 노랑/앰버
  SELL: '#ef4444',         // 빨강
  STRONG_SELL: '#dc2626',  // 진한 빨강
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

export default function StockChartClient({ symbol: rawSymbol }: { symbol: string }) {
  const symbol = decodeURIComponent(rawSymbol);
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
  const symbolMapping = getSymbolMapping(symbol);
  const isSupported = symbolMapping && symbolMapping.source !== 'none';

  // Yahoo Finance API 호출 함수 (allorigins 프록시 사용)
  const fetchYahooFinanceData = async (ticker: string) => {
    const yahooUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?range=2y&interval=1d`;
    const proxyUrl = `https://corsproxy.io/?${encodeURIComponent(yahooUrl)}`;
    
    const response = await fetch(proxyUrl);
    if (!response.ok) throw new Error(`Yahoo Finance API 오류: ${response.status}`);
    
    const data = await response.json();
    if (data.chart?.error) throw new Error(data.chart.error.description || 'Yahoo Finance 데이터 오류');
    
    const result = data.chart?.result?.[0];
    if (!result) throw new Error('차트 데이터 없음');
    
    const { timestamp, indicators } = result;
    const quote = indicators?.quote?.[0];
    if (!timestamp || !quote) throw new Error('가격 데이터 없음');
    
    // 데이터 변환
    const chartData = timestamp.map((time: number, index: number) => {
      const date = new Date(time * 1000);
      return {
        time: date.toISOString().split('T')[0],
        open: quote.open[index] || 0,
        high: quote.high[index] || 0,
        low: quote.low[index] || 0,
        close: quote.close[index] || 0,
      };
    }).filter((candle: any) => candle.open > 0 && candle.close > 0); // 유효한 데이터만 필터링
    
    return chartData;
  };

  // CoinGecko OHLC API 호출 함수
  const fetchCoinGeckoData = async (symbol: string) => {
    const coinId = getCoinId(symbol) || getCoinId(stockName);
    if (!coinId) throw new Error('CoinGecko ID를 찾을 수 없습니다');
    
    // 최대 365일 OHLC 데이터
    const response = await fetch(`https://api.coingecko.com/api/v3/coins/${coinId}/ohlc?vs_currency=usd&days=365`);
    if (!response.ok) throw new Error(`CoinGecko API 오류: ${response.status}`);
    
    const data = await response.json();
    if (!Array.isArray(data) || data.length === 0) throw new Error('CoinGecko OHLC 데이터 없음');
    
    // CoinGecko OHLC: [timestamp, open, high, low, close]
    // 같은 날짜 데이터를 일봉으로 합치기
    const dailyMap = new Map<string, any>();
    for (const [ts, open, high, low, close] of data) {
      const date = new Date(ts).toISOString().split('T')[0];
      const existing = dailyMap.get(date);
      if (!existing) {
        dailyMap.set(date, { time: date, open, high, low, close });
      } else {
        existing.high = Math.max(existing.high, high);
        existing.low = Math.min(existing.low, low);
        existing.close = close; // 마지막 close
      }
    }
    
    return Array.from(dailyMap.values()).sort((a, b) => a.time.localeCompare(b.time));
  };

  // CryptoCompare API 호출 함수
  const fetchCryptoCompareData = async (symbol: string) => {
    const response = await fetch(`https://min-api.cryptocompare.com/data/v2/histoday?fsym=${symbol}&tsym=USD&limit=730`);
    const data = await response.json();
    
    if (data.Response === 'Error') throw new Error(data.Message || 'CryptoCompare API 오류');
    
    const priceData = data.Data?.Data || [];
    return priceData.map((d: any) => ({
      time: new Date(d.time * 1000).toISOString().split('T')[0],
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));
  };

  // 차트 데이터 로드 (다중 데이터 소스 지원)
  useEffect(() => {
    if (!symbolMapping || symbolMapping.source === 'none') { 
      setLoading(false); 
      return; 
    }

    (async () => {
      try {
        setLoading(true);
        setError(null);
        
        let data: any[] = [];
        
        if (symbolMapping.source === 'coingecko') {
          data = await fetchCoinGeckoData(symbolMapping.symbol);
        } else if (symbolMapping.source === 'cryptocompare') {
          data = await fetchCryptoCompareData(symbolMapping.symbol);
        } else if (symbolMapping.source === 'yahoo') {
          data = await fetchYahooFinanceData(symbolMapping.symbol);
        }
        
        if (data.length === 0) {
          throw new Error('차트 데이터가 없습니다');
        }
        
        setChartData(data);
      } catch (err: any) {
        console.error('차트 데이터 로드 오류:', err);
        setError(err.message || '차트 데이터 로드 실패');
      } finally {
        setLoading(false);
      }
    })();
  }, [symbol, symbolMapping]);

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
        handleScroll: { mouseWheel: true, pressedMouseMove: false, horzTouchDrag: true, vertTouchDrag: false },
        handleScale: { mouseWheel: true, pinch: true, axisPressedMouseMove: false },
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

      // Google Finance 스타일 드래그-투-셀렉트 범위 기능
      let isDragging = false;
      let dragStartTime: string | null = null;
      let dragStartX = 0;
      let dragStartY = 0;
      let selectionOverlay: HTMLDivElement | null = null;
      let rangeBadge: HTMLDivElement | null = null;

      // 선택 오버레이 생성
      const createSelectionOverlay = () => {
        if (selectionOverlay) return selectionOverlay;
        
        selectionOverlay = document.createElement('div');
        selectionOverlay.style.cssText = `
          position: absolute;
          background: rgba(66, 165, 245, 0.15);
          border: 1px solid rgba(66, 165, 245, 0.4);
          border-radius: 4px;
          pointer-events: none;
          z-index: 45;
          display: none;
        `;
        container.appendChild(selectionOverlay);
        return selectionOverlay;
      };

      // 범위 배지 생성
      const createRangeBadge = () => {
        if (rangeBadge) return rangeBadge;
        
        rangeBadge = document.createElement('div');
        rangeBadge.style.cssText = `
          position: absolute;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 12px 16px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.15);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          white-space: nowrap;
          z-index: 60;
          pointer-events: auto;
          cursor: pointer;
          display: none;
        `;
        container.appendChild(rangeBadge);
        return rangeBadge;
      };

      // 날짜를 한국어 형식으로 포맷 (YYYY년 M월 D일)
      const formatKoreanDate = (dateStr: string) => {
        const date = new Date(dateStr);
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return `${year}년 ${month}월 ${day}일`;
      };

      // 가장 가까운 캔들 찾기 (정확한 날짜가 없을 때 대비)
      const findClosestCandle = (targetTime: string) => {
        let exact = chartData.find(d => d.time === targetTime);
        if (exact) return exact;
        // 가장 가까운 날짜 찾기
        let closest = chartData[0];
        let minDiff = Math.abs(new Date(chartData[0].time).getTime() - new Date(targetTime).getTime());
        for (const d of chartData) {
          const diff = Math.abs(new Date(d.time).getTime() - new Date(targetTime).getTime());
          if (diff < minDiff) { minDiff = diff; closest = d; }
        }
        return closest;
      };

      // 가격 변화 계산 및 배지 표시
      const showRangeBadge = (startTime: string, endTime: string, x: number, y: number) => {
        const startCandle = findClosestCandle(startTime);
        const endCandle = findClosestCandle(endTime);
        
        if (!startCandle || !endCandle) return;

        const startPrice = startCandle.close;
        const endPrice = endCandle.close;
        const priceChange = endPrice - startPrice;
        const percentChange = (priceChange / startPrice) * 100;
        
        const isPositive = priceChange >= 0;
        const changeColor = isPositive ? '#10b981' : '#ef4444';
        const arrow = isPositive ? '↑' : '↓';
        
        const badge = createRangeBadge();
        badge.innerHTML = `
          <div style="color: ${changeColor}; font-size: 16px; font-weight: 700; line-height: 1.2; margin-bottom: 4px;">
            ${priceChange >= 0 ? '+' : ''}$${Math.abs(priceChange).toFixed(2)} (${percentChange >= 0 ? '+' : ''}${percentChange.toFixed(2)}%) ${arrow}
          </div>
          <div style="color: #6b7280; font-size: 13px;">
            ${formatKoreanDate(startTime)} - ${formatKoreanDate(endTime)}
          </div>
        `;
        
        // 배지 위치 조정 (화면 경계 고려)
        const badgeWidth = 300; // 예상 배지 너비
        const badgeHeight = 60; // 예상 배지 높이
        const containerRect = container.getBoundingClientRect();
        
        let badgeX = x + 10;
        let badgeY = y - badgeHeight - 10;
        
        // 오른쪽 경계 체크
        if (badgeX + badgeWidth > containerRect.width) {
          badgeX = x - badgeWidth - 10;
        }
        
        // 상단 경계 체크
        if (badgeY < 0) {
          badgeY = y + 20;
        }
        
        badge.style.left = `${Math.max(10, badgeX)}px`;
        badge.style.top = `${Math.max(10, badgeY)}px`;
        badge.style.display = 'block';
        
        // 배지 클릭으로 닫기
        badge.onclick = () => {
          badge.style.display = 'none';
          if (selectionOverlay) {
            selectionOverlay.style.display = 'none';
          }
        };
      };

      // 마우스 다운 이벤트 - 드래그 시작
      const handleMouseDown = (e: MouseEvent) => {
        // 기존 마커 도트나 툴팁 영역이 아닌 경우만 드래그 시작
        const target = e.target as HTMLElement;
        if (target.closest('.marker-dot') || target.closest('.marker-tooltip') || target.closest('.dot-preview')) {
          return;
        }

        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // 차트 영역 내부인지 확인 (대략적인 패딩 고려)
        if (x < 60 || x > rect.width - 60 || y < 20 || y > rect.height - 40) {
          return;
        }

        const timeCoordinate = chart.timeScale().coordinateToTime(x);
        if (!timeCoordinate) return;

        isDragging = true;
        dragStartTime = timeCoordinate as string;
        dragStartX = x;
        dragStartY = y;

        // 기존 선택 영역 및 배지 제거
        if (selectionOverlay) selectionOverlay.style.display = 'none';
        if (rangeBadge) rangeBadge.style.display = 'none';

        e.preventDefault();
      };

      // 마우스 이동 이벤트 - 드래그 중 선택 영역 업데이트
      const handleMouseMove = (e: MouseEvent) => {
        if (!isDragging || !dragStartTime) return;

        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const overlay = createSelectionOverlay();
        
        const startX = Math.min(dragStartX, x);
        const endX = Math.max(dragStartX, x);
        const startY = 20; // 차트 상단
        const endY = rect.height - 40; // 차트 하단 (시간축 제외)

        overlay.style.left = `${startX}px`;
        overlay.style.top = `${startY}px`;
        overlay.style.width = `${endX - startX}px`;
        overlay.style.height = `${endY - startY}px`;
        overlay.style.display = 'block';

        e.preventDefault();
      };

      // 마우스 업 이벤트 - 드래그 완료 및 결과 표시
      const handleMouseUp = (e: MouseEvent) => {
        if (!isDragging || !dragStartTime) return;

        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        
        const endTimeCoordinate = chart.timeScale().coordinateToTime(x);
        if (!endTimeCoordinate) {
          isDragging = false;
          return;
        }

        const endTime = endTimeCoordinate as string;
        
        // 시작점과 끝점이 다른 경우에만 계산
        if (Math.abs(x - dragStartX) > 10 && dragStartTime !== endTime) {
          // 시간 순서 정렬 (시작점이 끝점보다 이후일 수 있음)
          const startTime = dragStartTime <= endTime ? dragStartTime : endTime;
          const finalEndTime = dragStartTime <= endTime ? endTime : dragStartTime;
          
          showRangeBadge(startTime, finalEndTime, (dragStartX + x) / 2, Math.min(dragStartY, e.clientY - rect.top));
        } else {
          // 선택 영역이 너무 작으면 제거
          if (selectionOverlay) {
            selectionOverlay.style.display = 'none';
          }
        }

        isDragging = false;
        dragStartTime = null;
        e.preventDefault();
      };

      // 전역 클릭으로 선택 해제
      const handleGlobalClick = (e: MouseEvent) => {
        const target = e.target as HTMLElement;
        
        // 차트 컨테이너 밖을 클릭하거나, 마커 관련 요소가 아닌 곳을 클릭한 경우
        if (!container.contains(target) || 
            (!target.closest('.marker-dot') && 
             !target.closest('.marker-tooltip') && 
             !target.closest('.dot-preview') &&
             target !== rangeBadge &&
             !rangeBadge?.contains(target))) {
          
          if (selectionOverlay) selectionOverlay.style.display = 'none';
          if (rangeBadge) rangeBadge.style.display = 'none';
        }
      };

      // 이벤트 리스너 등록
      container.addEventListener('mousedown', handleMouseDown);
      container.addEventListener('mousemove', handleMouseMove);
      container.addEventListener('mouseup', handleMouseUp);
      document.addEventListener('click', handleGlobalClick);

      // 드래그 선택 정리 함수
      const cleanupDragSelection = () => {
        container.removeEventListener('mousedown', handleMouseDown);
        container.removeEventListener('mousemove', handleMouseMove);
        container.removeEventListener('mouseup', handleMouseUp);
        document.removeEventListener('click', handleGlobalClick);
        
        if (selectionOverlay) {
          selectionOverlay.remove();
          selectionOverlay = null;
        }
        if (rangeBadge) {
          rangeBadge.remove();
          rangeBadge = null;
        }
      };

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
            width: 14px;
            height: 14px;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 0 8px ${SIGNAL_COLORS[signal.signalType as keyof typeof SIGNAL_COLORS] || '#94a3b8'}80, 0 2px 6px rgba(0,0,0,0.2);
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
        cleanupDragSelection();
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

  if (!symbolMapping && stockSignals.length === 0) {
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
        </div>
      </div>

      {/* 차트 영역 - lightweight-charts + 시그널 마커 */}
      {isSupported && (
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
      )}
      {!isSupported && (
      <div className="bg-white rounded-xl border border-gray-200 p-6 text-center">
        <Info className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-500">이 종목은 차트 데이터를 지원하지 않습니다.</p>
        <p className="text-sm text-gray-400 mt-1">시그널 정보는 아래에서 확인하세요.</p>
      </div>
      )}

      {/* 시그널 타입 필터 */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
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
