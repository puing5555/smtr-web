'use client';

import { useState, useEffect, use } from 'react';
import { ArrowLeft, ExternalLink, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { useInfluencersStore } from '@/stores/influencers';

const SIGNAL_TYPES: Record<string, { label: string; color: string; textColor: string }> = {
  STRONG_BUY: { label: '적극매수', color: 'bg-green-600', textColor: 'text-green-100' },
  BUY: { label: '매수', color: 'bg-green-500', textColor: 'text-green-100' },
  POSITIVE: { label: '긍정', color: 'bg-blue-500', textColor: 'text-blue-100' },
  HOLD: { label: '보유', color: 'bg-yellow-500', textColor: 'text-yellow-100' },
  NEUTRAL: { label: '중립', color: 'bg-gray-500', textColor: 'text-gray-100' },
  CONCERN: { label: '우려', color: 'bg-orange-500', textColor: 'text-orange-100' },
  SELL: { label: '매도', color: 'bg-red-500', textColor: 'text-red-100' },
  STRONG_SELL: { label: '적극매도', color: 'bg-red-600', textColor: 'text-red-100' },
};

export default function InfluencerDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [signalFilter, setSignalFilter] = useState('ALL');
  const { influencers, signals, loadInfluencers, loadSignals } = useInfluencersStore();

  useEffect(() => {
    loadInfluencers();
    loadSignals();
  }, [loadInfluencers, loadSignals]);

  const influencer = influencers.find((inf) => inf.id === Number(id));
  const influencerSignals = signals
    .filter((s) => s.influencer === influencer?.name)
    .filter((s) => signalFilter === 'ALL' || s.signalType === signalFilter);

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
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back button */}
      <Link href="/influencers" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
        <ArrowLeft className="w-4 h-4" />
        인플루언서 목록으로
      </Link>

      {/* Profile Header */}
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <div className="flex items-center gap-4">
          <div className="text-5xl">{influencer.avatar}</div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold">{influencer.name}</h1>
              {influencer.verified && <span className="text-blue-500 text-xl">✓</span>}
            </div>
            <p className="text-gray-500 mt-1">최근 활동: {influencer.recentActivity}</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-900">{influencer.totalSignals}</p>
            <p className="text-sm text-gray-600">총 시그널</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">{influencer.accuracy}%</p>
            <p className="text-sm text-gray-600">정확도</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-900">
              {Object.values(influencer.signalDistribution).filter(v => v > 0).length}
            </p>
            <p className="text-sm text-gray-600">시그널 타입</p>
          </div>
        </div>

        {/* Signal Distribution Bar */}
        <div className="mt-6">
          <p className="text-sm text-gray-600 mb-2">시그널 분포</p>
          <div className="flex rounded-full overflow-hidden h-3">
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
          <div className="flex flex-wrap gap-3 mt-2">
            {Object.entries(influencer.signalDistribution)
              .filter(([_, count]) => count > 0)
              .map(([type, count]) => (
                <div key={type} className="flex items-center gap-1">
                  <div className={`w-3 h-3 rounded ${SIGNAL_TYPES[type]?.color || 'bg-gray-300'}`}></div>
                  <span className="text-xs text-gray-600">{SIGNAL_TYPES[type]?.label}: {count}개</span>
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* Signals Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">시그널 / 발언</h2>
          <span className="text-sm text-gray-500">{influencerSignals.length}개</span>
        </div>

        {/* Filter */}
        <div className="flex flex-wrap gap-2 mb-4">
          <Button
            variant={signalFilter === 'ALL' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSignalFilter('ALL')}
          >
            전체
          </Button>
          {Object.entries(SIGNAL_TYPES).map(([type, config]) => (
            <Button
              key={type}
              variant={signalFilter === type ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSignalFilter(type)}
              className={signalFilter === type ? `${config.color} ${config.textColor}` : ''}
            >
              {config.label}
            </Button>
          ))}
        </div>

        {/* Signal List */}
        <div className="space-y-4">
          {influencerSignals.length === 0 ? (
            <div className="bg-white rounded-lg p-8 border border-gray-200 text-center text-gray-500">
              해당 필터에 맞는 시그널이 없습니다.
            </div>
          ) : (
            influencerSignals.map((signal) => (
              <div key={signal.id} className="bg-white rounded-lg p-5 border border-gray-200 hover:shadow-sm transition-shadow">
                <div className="flex items-center gap-3 mb-2">
                  <Badge className={`${SIGNAL_TYPES[signal.signalType].color} ${SIGNAL_TYPES[signal.signalType].textColor}`}>
                    {SIGNAL_TYPES[signal.signalType].label}
                  </Badge>
                  <span className="font-medium text-gray-900">{signal.stock}</span>
                  <span className="text-sm text-gray-500">- {signal.stockName}</span>
                  <span className="text-sm text-gray-500 ml-auto">${signal.price}</span>
                </div>
                <p className="text-gray-700 mb-2">{signal.content}</p>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span>{signal.timestamp}</span>
                  {signal.youtubeLink && (
                    <a
                      href={signal.youtubeLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-blue-600 hover:text-blue-800"
                    >
                      <ExternalLink className="w-3 h-3" />
                      유튜브 보기
                    </a>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
