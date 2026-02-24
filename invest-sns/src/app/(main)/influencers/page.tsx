'use client';

import { useState, useEffect } from 'react';
import { Users, TrendingUp, Filter, Search, ChevronRight, ExternalLink } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useInfluencersStore } from '@/stores/influencers';

// 시그널 타입 정의 (8가지) - 요구사항에 맞는 색상
const SIGNAL_TYPES = {
  STRONG_BUY: { label: '적극매수', color: 'bg-green-700', textColor: 'text-white', hexColor: '#16a34a' },
  BUY: { label: '매수', color: 'bg-green-500', textColor: 'text-white', hexColor: '#22c55e' },
  POSITIVE: { label: '긍정', color: 'bg-green-300', textColor: 'text-green-900', hexColor: '#86efac' },
  HOLD: { label: '보유', color: 'bg-yellow-500', textColor: 'text-yellow-900', hexColor: '#eab308' },
  NEUTRAL: { label: '중립', color: 'bg-gray-500', textColor: 'text-white', hexColor: '#9ca3af' },
  CONCERN: { label: '우려', color: 'bg-orange-500', textColor: 'text-white', hexColor: '#f97316' },
  SELL: { label: '매도', color: 'bg-red-500', textColor: 'text-white', hexColor: '#ef4444' },
  STRONG_SELL: { label: '적극매도', color: 'bg-red-700', textColor: 'text-white', hexColor: '#dc2626' },
};

// 시그널 타입별 색상과 라벨 정의

export default function InfluencersPage() {
  const [activeTab, setActiveTab] = useState('overview');
  
  const {
    influencers,
    signals,
    stocks,
    isLoading,
    isLoadingSignals,
    isLoadingStocks,
    signalFilter,
    searchQuery,
    loadInfluencers,
    loadSignals,
    loadStocks,
    setSignalFilter,
    setSearchQuery,
    getFilteredSignals,
    getFilteredInfluencers,
    getFilteredStocks,
  } = useInfluencersStore();

  useEffect(() => {
    loadInfluencers();
    loadSignals();
    loadStocks();
  }, [loadInfluencers, loadSignals, loadStocks]);

  // 필터링된 데이터
  const filteredSignals = getFilteredSignals();
  const filteredInfluencers = getFilteredInfluencers();
  const filteredStocks = getFilteredStocks();

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">인플루언서</h1>
          <p className="text-gray-600 mt-1">
            투자 인플루언서들의 시그널과 발언을 추적해보세요
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="인플루언서, 종목 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 w-64"
            />
          </div>
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            필터
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="influencers">인플루언서</TabsTrigger>
          <TabsTrigger value="stocks">종목</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 최근 시그널 */}
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-4">최근 시그널</h3>
              <div className="space-y-4">
                {signals.slice(0, 3).map((signal) => (
                  <div key={signal.id} className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium text-sm">{signal.influencer}</span>
                        <Badge 
                          className={`${SIGNAL_TYPES[signal.signalType].color} ${SIGNAL_TYPES[signal.signalType].textColor} text-xs`}
                        >
                          {SIGNAL_TYPES[signal.signalType].label}
                        </Badge>
                        <span className="text-xs text-gray-500">{signal.stock}</span>
                      </div>
                      <p className="text-sm text-gray-700 line-clamp-2">{signal.content}</p>
                      <p className="text-xs text-gray-500 mt-1">{signal.timestamp}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 인기 인플루언서 */}
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-4">인기 인플루언서</h3>
              <div className="space-y-4">
                {influencers.slice(0, 3).map((influencer) => (
                  <Link key={influencer.id} href={`/influencers/${influencer.id}`}>
                    <div className="flex items-center space-x-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer">
                      <div className="text-2xl">{influencer.avatar}</div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{influencer.name}</span>
                          {influencer.verified && <span className="text-blue-500">✓</span>}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span>시그널 {influencer.totalSignals}개</span>
                          <span>정확도 {influencer.accuracy}%</span>
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="influencers" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredInfluencers.map((influencer) => (
              <div key={influencer.id} className="bg-white rounded-lg p-6 border border-gray-200 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="text-3xl">{influencer.avatar}</div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">{influencer.name}</h3>
                        {influencer.verified && <span className="text-blue-500">✓</span>}
                      </div>
                      <p className="text-sm text-gray-500">최근 활동: {influencer.recentActivity}</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">총 시그널</span>
                    <span className="font-medium">{influencer.totalSignals}개</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">정확도</span>
                    <span className="font-medium text-green-600">{influencer.accuracy}%</span>
                  </div>

                  {/* 시그널 분포 */}
                  <div className="mt-4">
                    <p className="text-sm text-gray-600 mb-2">시그널 분포</p>
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(influencer.signalDistribution).filter(([_, count]) => count > 0).map(([type, count]) => (
                        <div key={type} className="flex items-center gap-1">
                          <div className={`w-2 h-2 rounded ${SIGNAL_TYPES[type as keyof typeof SIGNAL_TYPES]?.color || 'bg-gray-300'}`}></div>
                          <span className="text-xs text-gray-600">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <Link href={`/influencers/${influencer.id}`}>
                  <Button variant="outline" size="sm" className="w-full mt-4">
                    자세히 보기
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="stocks" className="mt-6">
          <div className="grid gap-4">
            {filteredStocks.map((stock) => (
              <div key={stock.symbol} className="bg-white rounded-lg p-6 border border-gray-200">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">{stock.symbol} - {stock.name}</h3>
                    <p className="text-sm text-gray-600">관련 시그널 {stock.totalSignals}개</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500">최근:</span>
                    <Badge className={`${SIGNAL_TYPES[stock.recentSignal as keyof typeof SIGNAL_TYPES]?.color || 'bg-gray-500'} ${SIGNAL_TYPES[stock.recentSignal as keyof typeof SIGNAL_TYPES]?.textColor || 'text-white'}`}>
                      {SIGNAL_TYPES[stock.recentSignal as keyof typeof SIGNAL_TYPES]?.label || stock.recentSignal}
                    </Badge>
                  </div>
                </div>

                <div className="flex items-center gap-4 mb-3">
                  <span className="text-sm text-gray-600">관련 인플루언서:</span>
                  {stock.influencers.map((influencer) => (
                    <Badge key={influencer} variant="secondary" className="text-xs">
                      {influencer}
                    </Badge>
                  ))}
                </div>

                {/* 시그널 분포 */}
                <div className="mt-4">
                  <p className="text-sm text-gray-600 mb-2">시그널 분포</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(stock.signalDistribution).filter(([_, count]) => count > 0).map(([type, count]) => (
                      <div key={type} className="flex items-center gap-1">
                        <div className={`w-3 h-3 rounded ${SIGNAL_TYPES[type as keyof typeof SIGNAL_TYPES]?.color || 'bg-gray-300'}`}></div>
                        <span className="text-sm text-gray-600">{SIGNAL_TYPES[type as keyof typeof SIGNAL_TYPES]?.label || type}: {count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}