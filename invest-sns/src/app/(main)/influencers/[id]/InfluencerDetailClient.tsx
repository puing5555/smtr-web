'use client';

import React, { useState, useEffect, use, useMemo, useCallback } from 'react';
import { ArrowLeft, ExternalLink, Filter, Star, Globe, TrendingUp, Activity, ChevronDown, ChevronRight, Play, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { useInfluencersStore } from '@/stores/influencers';
import { useSignalReturns } from '@/lib/hooks/useSignalReturns';
import { formatReturn, getReturnColor } from '@/lib/api/coingecko';

const SIGNAL_TYPES: Record<string, { label: string; color: string; textColor: string }> = {
  STRONG_BUY: { label: '적극매수', color: 'bg-green-700', textColor: 'text-white' },
  BUY: { label: '매수', color: 'bg-green-500', textColor: 'text-white' },
  POSITIVE: { label: '긍정', color: 'bg-green-300', textColor: 'text-green-900' },
  HOLD: { label: '보유', color: 'bg-yellow-500', textColor: 'text-yellow-900' },
  NEUTRAL: { label: '중립', color: 'bg-gray-500', textColor: 'text-white' },
  CONCERN: { label: '우려', color: 'bg-orange-500', textColor: 'text-white' },
  SELL: { label: '매도', color: 'bg-red-500', textColor: 'text-white' },
  STRONG_SELL: { label: '적극매도', color: 'bg-red-700', textColor: 'text-white' },
};

export default function InfluencerDetailClient({ id }: { id: string }) {
  const [stockFilter, setStockFilter] = useState('ALL');
  const [displayCount, setDisplayCount] = useState(20); // 처음에 20개 표시
  const [modalSignal, setModalSignal] = useState<typeof influencerSignals[0] | null>(null); // 모달
  const [showSummary, setShowSummary] = useState(false); // 영상요약 토글에 표시할 시그널
  const { influencers, signals, loadInfluencers, loadSignals } = useInfluencersStore();

  const loadedRef = React.useRef(false);
  useEffect(() => {
    if (loadedRef.current) return;
    loadedRef.current = true;
    loadInfluencers();
    loadSignals();
  }, [loadInfluencers, loadSignals]);

  const influencer = influencers.find((inf) => inf.id === Number(id) || (id === 'corinpapa1106' && inf.name === '코린이 아빠'));
  const influencerSignals = useMemo(() => signals.filter((s) => s.influencer === influencer?.name), [signals, influencer?.name]);
  
  // 수익률 데이터 - CoinGecko API 비활성화 (화면 흔들림 방지)
  // const { returns, loading: returnsLoading } = useSignalReturns(influencerSignals as any);
  const returns: Record<number, any> = {};
  const returnsLoading = false;
  
  // 종목별 필터링된 시그널
  const filteredSignals = useMemo(() => {
    if (stockFilter === 'ALL') return influencerSignals;
    return influencerSignals.filter((s) => s.stock === stockFilter);
  }, [influencerSignals, stockFilter]);

  // 표시할 시그널들 (displayCount만큼)
  const displayedSignals = useMemo(() => {
    return filteredSignals.slice(0, displayCount);
  }, [filteredSignals, displayCount]);

  // 월별로 그룹핑된 시그널들 (주요 발언 타임라인용)
  const signalsByMonth = useMemo(() => {
    const grouped: { [key: string]: typeof influencerSignals } = {};
    
    influencerSignals
      .sort((a, b) => new Date(b.videoDate).getTime() - new Date(a.videoDate).getTime())
      .slice(0, 50) // 최근 50개만 표시
      .forEach(signal => {
        const date = new Date(signal.videoDate);
        const monthKey = `${date.getFullYear()}년 ${date.getMonth() + 1}월`;
        
        if (!grouped[monthKey]) {
          grouped[monthKey] = [];
        }
        grouped[monthKey].push(signal);
      });
    
    return Object.entries(grouped);
  }, [influencerSignals]);

  // 종목별 카운트 생성
  const stockCounts = useMemo(() => {
    const counts = influencerSignals.reduce((acc, signal) => {
      acc[signal.stock] = (acc[signal.stock] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return Object.entries(counts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 8); // 상위 8개만
  }, [influencerSignals]);

  if (!influencer) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Link href="/influencers" className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6">
          <ArrowLeft className="w-4 h-4" />
          인플루언서 목록으로
        </Link>
        <p className="text-gray-500">인플루언서를 찾을 수 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Back button */}
      <Link href="/influencers" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
        <ArrowLeft className="w-4 h-4" />
        인플루언서 목록으로
      </Link>

      {/* SMTR Style Profile Header */}
      <div className="bg-gradient-to-br from-white to-gray-50 border border-gray-200 rounded-2xl p-8 shadow-sm">
        <div className="flex flex-wrap items-center gap-8">
          {/* Avatar and Basic Info */}
          <div className="flex items-center gap-6">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-3xl font-bold text-white shadow-lg">
              {influencer.avatar}
            </div>
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold text-gray-900">{influencer.name}</h1>
                {influencer.verified && (
                  <div className="flex items-center justify-center w-6 h-6 bg-blue-500 rounded-full">
                    <Star className="w-3 h-3 text-white fill-white" />
                  </div>
                )}
                <span className="text-lg">{influencer.country}</span>
              </div>
              <p className="text-gray-600 flex items-center gap-2 mb-1">
                <Globe className="w-4 h-4" />
                {influencer.channelName}
              </p>
              <p className="text-sm text-gray-500">최근 활동: {influencer.recentActivity}</p>
            </div>
          </div>

          {/* Key Stats */}
          <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600 flex items-center justify-center gap-1">
                <TrendingUp className="w-5 h-5" />
                +{influencer.avgReturn}%
              </div>
              <p className="text-xs text-gray-600 mt-1">평균 수익률</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{influencer.totalSignals}</div>
              <p className="text-xs text-gray-600 mt-1">총 발언 수</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{influencer.accuracy}%</div>
              <p className="text-xs text-gray-600 mt-1">적중률</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600 flex items-center justify-center gap-1">
                <Activity className="w-5 h-5" />
                {influencer.radarStats.activity}
              </div>
              <p className="text-xs text-gray-600 mt-1">활동성</p>
            </div>
          </div>
        </div>

        {/* Top Stocks */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">관심 종목</h3>
          <div className="flex flex-wrap gap-2">
            {influencer.topStocks.map((stock, index) => (
              <span 
                key={stock} 
                className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full"
              >
                #{index + 1} {stock}
              </span>
            ))}
          </div>
        </div>

        {/* Major Statements Timeline */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">📋 주요 발언 요약</h3>
          {(() => {
            // 가장 강한 시그널 우선: STRONG_BUY/STRONG_SELL > HIGH confidence > 최신순
            const strengthOrder: Record<string, number> = {
              STRONG_BUY: 6, STRONG_SELL: 6, BUY: 4, SELL: 4, POSITIVE: 2, CONCERN: 2, HOLD: 1, NEUTRAL: 0
            };
            const confOrder: Record<string, number> = { HIGH: 3, MEDIUM: 2, LOW: 1 };
            const sorted = [...influencerSignals]
              .sort((a, b) => {
                const sa = strengthOrder[a.signalType] || 0;
                const sb = strengthOrder[b.signalType] || 0;
                if (sb !== sa) return sb - sa;
                const ca = confOrder[a.confidence || ''] || 0;
                const cb = confOrder[b.confidence || ''] || 0;
                if (cb !== ca) return cb - ca;
                return new Date(b.videoDate).getTime() - new Date(a.videoDate).getTime();
              });
            const seenStocks = new Set<string>();
            const topSignals: typeof sorted = [];
            for (const s of sorted) {
              if (!seenStocks.has(s.stock) && topSignals.length < 3) {
                seenStocks.add(s.stock);
                topSignals.push(s);
              }
            }
            return topSignals.length === 0 ? (
              <p className="text-sm text-gray-500">발언 이력이 없습니다.</p>
            ) : (
              <div className="space-y-2">
                {topSignals.map((signal) => {
                  const date = new Date(signal.videoDate);
                  const dateStr = `${date.getFullYear()}.${date.getMonth() + 1}/${date.getDate()}`;
                  return (
                    <div key={signal.id} className="flex items-center gap-3 text-sm">
                      <span className="text-gray-400 font-mono text-xs w-16">{dateStr}</span>
                      <span className="font-medium text-gray-900">{signal.stockName}</span>
                      <Badge className={`${SIGNAL_TYPES[signal.signalType]?.color || 'bg-gray-500'} ${SIGNAL_TYPES[signal.signalType]?.textColor || 'text-white'} text-xs`}>
                        {SIGNAL_TYPES[signal.signalType]?.label || signal.signalType}
                      </Badge>
                      <span className="text-gray-600 truncate">"{signal.content.slice(0, 40)}..."</span>
                    </div>
                  );
                })}
              </div>
            );
          })()}
        </div>
      </div>

      {/* Signals Section */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold">📋 발언 이력</h2>
            <span className="text-sm text-gray-500">{filteredSignals.length}개</span>
            <span className="text-xs text-gray-400 font-italic">• 최신순 정렬</span>
          </div>
        </div>

        {/* Stock Filter Tabs - SMTR Style */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setStockFilter('ALL')}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              stockFilter === 'ALL' 
                ? 'bg-blue-500 text-white shadow-md' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            전체 {influencerSignals.length}
          </button>
          {stockCounts.map(([stock, count]) => {
            const signal = influencerSignals.find(s => s.stock === stock);
            return (
              <button
                key={stock}
                onClick={() => setStockFilter(stock)}
                className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 ${
                  stockFilter === stock 
                    ? 'bg-blue-500 text-white shadow-md' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {signal?.stockName || stock}
                <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                  stockFilter === stock ? 'bg-white text-blue-500' : 'bg-blue-500 text-white'
                }`}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* SMTR Style Table */}
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">종목</th>
                  <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">신호</th>
                  <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">분석</th>
                  <th className="text-left py-4 px-3 text-sm font-semibold text-gray-700 whitespace-nowrap">날짜</th>
                  <th className="text-left py-4 px-3 text-sm font-semibold text-gray-700">수익률</th>
                  <th className="text-left py-4 px-2 text-sm font-semibold text-gray-700">영상</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredSignals.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-gray-500">
                      선택한 종목의 시그널이 없습니다.
                    </td>
                  </tr>
                ) : (
                  displayedSignals
                    .sort((a, b) => new Date(b.videoDate).getTime() - new Date(a.videoDate).getTime())
                    .map((signal) => (
                      <tr key={signal.id} className="hover:bg-gray-50 transition-colors cursor-pointer" onClick={() => { setModalSignal(signal); setShowSummary(false); }}>
                        <td className="py-4 px-6">
                          <div className="font-medium text-blue-600">{signal.stockName}</div>
                          <div className="text-xs text-gray-500">{signal.stock}</div>
                        </td>
                        <td className="py-4 px-6">
                          <Badge className={`${SIGNAL_TYPES[signal.signalType].color} ${SIGNAL_TYPES[signal.signalType].textColor} text-xs font-bold`}>
                            {SIGNAL_TYPES[signal.signalType].label}
                          </Badge>
                        </td>
                        <td className="py-4 px-6">
                          <div className="text-sm font-medium text-gray-900 mb-1">
                            {signal.analysis.summary}
                          </div>
                          <div className="text-xs text-gray-500 italic">
                            &quot;{signal.content}&quot;
                          </div>
                        </td>
                        <td className="py-4 px-3 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{signal.videoDate}</div>
                          <div className="text-xs text-gray-500">{signal.timestamp}</div>
                        </td>
                        <td className="py-4 px-3" style={{ minWidth: '60px' }}>
                          {(() => {
                            const returnData = returns[signal.id];
                            if (returnsLoading || returnData?.loading) {
                              return <span className="text-xs text-gray-400">로딩중...</span>;
                            }
                            if (returnData?.error) {
                              return <span className="text-xs text-gray-400">-</span>;
                            }
                            if (returnData?.returnRate !== null && returnData?.returnRate !== undefined) {
                              return (
                                <span className={`text-sm font-bold ${getReturnColor(returnData.returnRate)}`}>
                                  {formatReturn(returnData.returnRate)}
                                </span>
                              );
                            }
                            return <span className="text-xs text-gray-400">-</span>;
                          })()}
                        </td>
                        <td className="py-4 px-2">
                          {signal.youtubeLink && (
                            <a
                              href={signal.youtubeLink}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-red-600 hover:text-red-700 text-xs font-medium whitespace-nowrap"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <ExternalLink className="w-3 h-3" />
                              YT
                            </a>
                          )}
                        </td>
                      </tr>
                    ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* 더보기 버튼 */}
        {filteredSignals.length > displayCount && (
          <div className="text-center mt-6">
            <Button 
              onClick={() => setDisplayCount(prev => prev + 20)}
              variant="outline" 
              className="px-8 py-2"
            >
              더보기 ({filteredSignals.length - displayCount}개 더)
            </Button>
          </div>
        )}
      </div>

      {/* 영상 분석 모달 */}
      {modalSignal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setModalSignal(null)}>
          <div 
            className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto relative"
            onClick={(e) => e.stopPropagation()}
          >
            {/* 헤더 */}
            <div className="sticky top-0 bg-white border-b border-gray-200 rounded-t-2xl px-6 py-4 flex items-center justify-between z-10">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <Play className="w-4 h-4 text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-900">영상 분석</h3>
              </div>
              <button 
                onClick={() => setModalSignal(null)}
                className="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-6 space-y-5">
              {/* 2번째줄: 종목 + 신호 + 영상제목(한글) + 날짜 */}
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-xl font-bold text-gray-900">{modalSignal.stockName}</span>
                <Badge className={`${SIGNAL_TYPES[modalSignal.signalType].color} ${SIGNAL_TYPES[modalSignal.signalType].textColor} text-sm font-bold`}>
                  {SIGNAL_TYPES[modalSignal.signalType].label}
                </Badge>
                {modalSignal.videoTitle && (
                  <span className="text-sm text-gray-600">{modalSignal.videoTitle}</span>
                )}
                <span className="text-sm text-gray-500">{modalSignal.videoDate}</span>
              </div>

              {/* 3~4번째줄: 발언내용 */}
              <div>
                <h5 className="text-sm font-semibold text-gray-700 mb-2">💬 발언 내용</h5>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-800 leading-relaxed">{modalSignal.content}</p>
                  <div className="mt-2 text-xs text-gray-500">타임스탬프: {modalSignal.timestamp}</div>
                </div>
              </div>

              {/* 5~6번째줄: 영상요약 (항상 표시) */}
              <div>
                <h5 className="text-sm font-semibold text-gray-700 mb-2">📋 영상 요약</h5>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  {modalSignal.videoSummary ? (
                    <p className="text-gray-800 leading-relaxed whitespace-pre-line">{modalSignal.videoSummary}</p>
                  ) : (
                    <p className="text-gray-800 leading-relaxed">{modalSignal.analysis.detail}</p>
                  )}
                </div>
              </div>

              {/* 차트보기 + 영상보기 버튼 */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <a
                  href={`/smtr-web/guru_tracker_v24.html`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 inline-flex items-center justify-center gap-2 px-5 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                >
                  📊 차트보기
                </a>
                {modalSignal.youtubeLink && (
                  <a
                    href={modalSignal.youtubeLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 inline-flex items-center justify-center gap-2 px-5 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
                  >
                    ▶ 영상보기
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}