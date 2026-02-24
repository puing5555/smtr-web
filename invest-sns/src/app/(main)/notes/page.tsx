'use client';

import { useState, useEffect } from 'react';
import { Search, Trash2, Edit3, Heart, StickyNote, X } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useScrapsStore } from '@/stores/scraps';

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

export default function NotesPage() {
  const { scraps, watchlistStocks, watchlistInfluencers, loadFromStorage, removeScrap, updateScrapMemo } = useScrapsStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'stock' | 'influencer'>('all');
  const [filterValue, setFilterValue] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editMemo, setEditMemo] = useState('');

  useEffect(() => {
    loadFromStorage();
  }, [loadFromStorage]);

  const filteredScraps = scraps.filter(scrap => {
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      if (!scrap.stockName.toLowerCase().includes(q) &&
          !scrap.influencer.toLowerCase().includes(q) &&
          !scrap.memo.toLowerCase().includes(q) &&
          !scrap.content.toLowerCase().includes(q)) return false;
    }
    if (filterType === 'stock' && filterValue && scrap.stock !== filterValue) return false;
    if (filterType === 'influencer' && filterValue && scrap.influencer !== filterValue) return false;
    return true;
  });

  // 유니크 종목/인플루언서
  const uniqueStocks = [...new Set(scraps.map(s => JSON.stringify({ stock: s.stock, name: s.stockName })))].map(s => JSON.parse(s));
  const uniqueInfluencers = [...new Set(scraps.map(s => s.influencer))];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <StickyNote className="w-6 h-6" /> 메모
        </h1>
        <p className="text-gray-600 mt-1">스크랩한 시그널과 메모를 관리하세요</p>
      </div>

      {/* 관심 요약 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">⭐ 관심종목 ({watchlistStocks.length})</h3>
          <div className="flex flex-wrap gap-1">
            {watchlistStocks.length === 0 ? (
              <p className="text-xs text-gray-400">시그널을 스크랩하면 자동 추가됩니다</p>
            ) : watchlistStocks.map(s => (
              <span key={s.ticker} className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">{s.name}</span>
            ))}
          </div>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">👤 관심 인플루언서 ({watchlistInfluencers.length})</h3>
          <div className="flex flex-wrap gap-1">
            {watchlistInfluencers.length === 0 ? (
              <p className="text-xs text-gray-400">시그널을 스크랩하면 자동 추가됩니다</p>
            ) : watchlistInfluencers.map(i => (
              <span key={i.id} className="px-2 py-1 bg-purple-50 text-purple-700 text-xs rounded-full">{i.name}</span>
            ))}
          </div>
        </div>
      </div>

      {/* 검색 + 필터 */}
      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder="종목, 인플루언서, 메모 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <select
          value={filterType === 'all' ? 'all' : `${filterType}:${filterValue}`}
          onChange={(e) => {
            const v = e.target.value;
            if (v === 'all') { setFilterType('all'); setFilterValue(''); }
            else {
              const [type, val] = v.split(':');
              setFilterType(type as 'stock' | 'influencer');
              setFilterValue(val);
            }
          }}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white"
        >
          <option value="all">전체</option>
          <optgroup label="종목별">
            {uniqueStocks.map((s: { stock: string; name: string }) => (
              <option key={s.stock} value={`stock:${s.stock}`}>{s.name}</option>
            ))}
          </optgroup>
          <optgroup label="인플루언서별">
            {uniqueInfluencers.map(name => (
              <option key={name} value={`influencer:${name}`}>{name}</option>
            ))}
          </optgroup>
        </select>
      </div>

      {/* 스크랩 리스트 */}
      <div className="space-y-3">
        {filteredScraps.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <Heart className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-lg font-medium">스크랩한 메모가 없습니다</p>
            <p className="text-sm mt-1">인플루언서 시그널에서 ❤️를 눌러 스크랩해보세요</p>
          </div>
        ) : filteredScraps.map(scrap => (
          <div key={scrap.id} className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-sm transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-900">{scrap.stockName}</span>
                <Badge className={`${SIGNAL_TYPES[scrap.signalType]?.color || 'bg-gray-500'} ${SIGNAL_TYPES[scrap.signalType]?.textColor || 'text-white'} text-xs`}>
                  {SIGNAL_TYPES[scrap.signalType]?.label || scrap.signalType}
                </Badge>
                <span className="text-xs text-gray-500">by {scrap.influencer}</span>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => { setEditingId(scrap.id); setEditMemo(scrap.memo); }}
                  className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                  title="수정"
                >
                  <Edit3 className="w-4 h-4 text-gray-400" />
                </button>
                <button
                  onClick={() => removeScrap(scrap.id)}
                  className="p-1.5 hover:bg-red-50 rounded-lg transition-colors"
                  title="삭제"
                >
                  <Trash2 className="w-4 h-4 text-gray-400 hover:text-red-500" />
                </button>
              </div>
            </div>

            <p className="text-sm text-gray-600 mb-2 italic">&quot;{scrap.content}&quot;</p>

            {editingId === scrap.id ? (
              <div className="mt-3 space-y-2">
                <textarea
                  value={editMemo}
                  onChange={(e) => setEditMemo(e.target.value)}
                  className="w-full p-3 border border-blue-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-300"
                  rows={3}
                  autoFocus
                />
                <div className="flex gap-2 justify-end">
                  <button onClick={() => setEditingId(null)} className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">취소</button>
                  <button
                    onClick={() => { updateScrapMemo(scrap.id, editMemo); setEditingId(null); }}
                    className="px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                  >저장</button>
                </div>
              </div>
            ) : scrap.memo ? (
              <div className="mt-2 bg-pink-50 border border-pink-100 rounded-lg p-3">
                <p className="text-sm text-gray-700">📝 {scrap.memo}</p>
              </div>
            ) : null}

            <div className="flex items-center gap-3 mt-3 text-xs text-gray-400">
              <span>{scrap.videoDate}</span>
              <span>스크랩: {new Date(scrap.createdAt).toLocaleDateString('ko-KR')}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
