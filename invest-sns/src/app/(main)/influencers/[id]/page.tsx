'use client';

import { useState, useEffect, use, useMemo } from 'react';
import { ArrowLeft, ExternalLink, Filter, Star, Globe, TrendingUp, Activity } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { useInfluencersStore } from '@/stores/influencers';

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

export default function InfluencerDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [stockFilter, setStockFilter] = useState('ALL');
  const [displayCount, setDisplayCount] = useState(20); // 처음에 20개 표시
  const { influencers, signals, loadInfluencers, loadSignals } = useInfluencersStore();

  useEffect(() => {
    loadInfluencers();
    loadSignals();
  }, [loadInfluencers, loadSignals]);

  const influencer = influencers.find((inf) => inf.id === Number(id) || (id === 'corinpapa1106' && inf.name === '코린이 아빠'));
  const influencerSignals = signals.filter((s) => s.influencer === influencer?.name);
  
  // 종목별 필터링된 시그널
  const filteredSignals = useMemo(() => {
    if (stockFilter === 'ALL') return influencerSignals;
    return influencerSignals.filter((s) => s.stock === stockFilter);
  }, [influencerSignals, stockFilter]);

  // 표시할 시그널들 (displayCount만큼)
  const displayedSignals = useMemo(() => {
    return filteredSignals.slice(0, displayCount);
  }, [filteredSignals, displayCount]);

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
          <h3 className="text-sm font-semibold text-gray-700 mb-3">주력 종목</h3>
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

        {/* Signal Distribution */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">시그널 분포</h3>
          <div className="flex rounded-full overflow-hidden h-2 bg-gray-100 mb-3">
            {Object.entries(influencer.signalDistribution)
              .filter(([_, count]) => count > 0)
              .map(([type, count]) => (
                <div
                  key={type}
                  className={`${SIGNAL_TYPES[type]?.color || 'bg-gray-300'}`}
                  style={{ width: `${(count / influencer.totalSignals) * 100}%` }}
                  title={`${SIGNAL_TYPES[type]?.label}: ${count}개`}
                />
              ))}
          </div>
          <div className="flex flex-wrap gap-3">
            {Object.entries(influencer.signalDistribution)
              .filter(([_, count]) => count > 0)
              .slice(0, 4) // 주요 4개만 표시
              .map(([type, count]) => (
                <div key={type} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${SIGNAL_TYPES[type]?.color || 'bg-gray-300'}`}></div>
                  <span className="text-xs text-gray-600 font-medium">
                    {SIGNAL_TYPES[type]?.label} {count}개
                  </span>
                </div>
              ))}
          </div>
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
                  <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">날짜</th>
                  <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">수익률</th>
                  <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">영상</th>
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
                      <tr key={signal.id} className="hover:bg-gray-50 transition-colors">
                        <td className="py-4 px-6">
                          <div className="font-medium text-gray-900">{signal.stockName}</div>
                          <div className="text-xs text-gray-500">{signal.stock}</div>
                        </td>
                        <td className="py-4 px-6">
                          <Badge className={`${SIGNAL_TYPES[signal.signalType].color} ${SIGNAL_TYPES[signal.signalType].textColor} text-xs font-bold`}>
                            {SIGNAL_TYPES[signal.signalType].label}
                          </Badge>
                        </td>
                        <td className="py-4 px-6 max-w-md">
                          <div className="text-sm font-medium text-gray-900 mb-1">{signal.analysis.summary}</div>
                          <div className="text-xs text-gray-600 line-clamp-2">{signal.analysis.detail}</div>
                        </td>
                        <td className="py-4 px-6">
                          <div className="text-sm text-gray-900">{signal.videoDate}</div>
                          <div className="text-xs text-gray-500">{signal.timestamp}</div>
                        </td>
                        <td className="py-4 px-6">
                          {signal.returnRate ? (
                            <span className={`text-sm font-bold ${signal.returnRate > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {signal.returnRate > 0 ? '+' : ''}{signal.returnRate}%
                            </span>
                          ) : (
                            <span className="text-xs text-gray-400">-</span>
                          )}
                        </td>
                        <td className="py-4 px-6">
                          {signal.youtubeLink && (
                            <a
                              href={signal.youtubeLink}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-red-600 hover:text-red-700 text-xs font-medium"
                            >
                              <ExternalLink className="w-3 h-3" />
                              YouTube
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
    </div>
  );
}
