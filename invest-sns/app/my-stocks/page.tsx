'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getLatestInfluencerSignals } from '@/lib/supabase';

// 관심종목 칩 데이터
const stockChips = [
  { name: '전체', code: '', change: '', isPositive: true, isActive: true },
  { name: '삼성전자', code: '005930', change: '+0.8%', isPositive: true, isActive: false },
  { name: '현대차', code: '005380', change: '+2.1%', isPositive: true, isActive: false },
  { name: '카카오', code: '035720', change: '-1.2%', isPositive: false, isActive: false },
  { name: 'SK하이닉스', code: '000660', change: '+1.5%', isPositive: true, isActive: false },
  { name: 'LG에너지', code: '373220', change: '+0.5%', isPositive: true, isActive: false },
  { name: 'NAVER', code: '035420', change: '-0.3%', isPositive: false, isActive: false },
];

// 통합 피드 아이템 타입
interface FeedItem {
  id: string;
  type: 'influencer' | 'analyst' | 'disclosure' | 'news';
  icon: string;
  categoryName: string;
  stockName: string;
  stockCode: string;
  title: string;
  subtitle?: string;
  time: string;
  date: string;
  timestamp: number; // 정렬용
  source: string;
  signal?: string;
  keyQuote?: string;
  reasoning?: string;
  profileLink?: string;
  detailLink?: string;
}

// 더미 애널리스트 리포트 데이터
const dummyAnalystReports = [
  {
    id: 'analyst_1',
    stockName: '삼성전자',
    stockCode: '005930',
    firm: '한국투자증권',
    analyst: '김선우',
    rating: 'BUY',
    targetPrice: '85,000원',
    summary: '3분기 실적 서프라이즈, HBM 수요 증가',
    publishedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5시간 전
  },
  {
    id: 'analyst_2',
    stockName: '현대차',
    stockCode: '005380',
    firm: '미래에셋증권',
    analyst: '박자동차',
    rating: 'BUY',
    targetPrice: '220,000원',
    summary: '전기차 판매 증가, 인도법인 호조',
    publishedAt: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(), // 3시간 전
  },
  {
    id: 'analyst_3',
    stockName: 'SK하이닉스',
    stockCode: '000660',
    firm: 'KB증권',
    analyst: '이메모리',
    rating: 'BUY',
    targetPrice: '190,000원',
    summary: 'AI 반도체 수요 지속, D램 가격 회복',
    publishedAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), // 1시간 전
  }
];

// 더미 공시 데이터
const dummyDisclosures = [
  {
    id: 'disclosure_1',
    stockName: '삼성전자',
    stockCode: '005930',
    title: '자사주 500만주 취득 결정',
    grade: 'A',
    amount: '3조원',
    publishedAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4시간 전
  },
  {
    id: 'disclosure_2',
    stockName: '카카오',
    stockCode: '035720',
    title: '3분기 실적 공시',
    grade: 'A',
    amount: '매출 1.8조원',
    publishedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2시간 전
  }
];

// 더미 뉴스 데이터
const dummyNews = [
  {
    id: 'news_1',
    stockName: 'LG에너지',
    stockCode: '373220',
    title: 'GM과 배터리 공급계약 연장 협의',
    source: '서울경제',
    publishedAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6시간 전
  },
  {
    id: 'news_2',
    stockName: 'NAVER',
    stockCode: '035420',
    title: 'AI 클로바X 글로벌 확장 계획 발표',
    source: '매일경제',
    publishedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30분 전
  }
];

// Fallback 더미 시그널 데이터 (Supabase 연결 실패시 사용)
const getDummySignals = () => [
  {
    id: 1,
    stock: '삼성전자',
    ticker: '005930',
    signal: '매수',
    key_quote: '3분기 실적이 시장 기대치를 상회했습니다',
    reasoning: 'HBM 수요 증가와 메모리 반도체 회복세',
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    speakers: { name: '코린이아빠' },
    influencer_videos: {
      influencer_channels: {
        channel_name: '코린이아빠',
        channel_handle: '@korini_papa'
      },
      published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
    }
  },
  {
    id: 2,
    stock: '현대차',
    ticker: '005380',
    signal: '긍정',
    key_quote: '전기차 판매량이 전년대비 50% 증가',
    reasoning: '인도 법인 호조와 전기차 라인업 확대',
    created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    speakers: { name: '삼프로TV' },
    influencer_videos: {
      influencer_channels: {
        channel_name: '삼프로TV',
        channel_handle: '@3protv'
      },
      published_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
    }
  },
  {
    id: 3,
    stock: 'SK하이닉스',
    ticker: '000660',
    signal: '매수',
    key_quote: 'AI 반도체 수요가 계속 증가하고 있어요',
    reasoning: 'D램 가격 회복과 HBM 시장 확대',
    created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    speakers: { name: '슈카월드' },
    influencer_videos: {
      influencer_channels: {
        channel_name: '슈카월드',
        channel_handle: '@syuka'
      },
      published_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
    }
  },
  // 더 많은 더미 데이터 추가
  {
    id: 4,
    stock: '카카오',
    ticker: '035720',
    signal: '중립',
    key_quote: '단기적으로는 관망하는 것이 좋겠습니다',
    reasoning: '규제 불확실성과 AI 투자 부담',
    created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    speakers: { name: '코린이아빠' },
    influencer_videos: {
      influencer_channels: {
        channel_name: '코린이아빠',
        channel_handle: '@korini_papa'
      },
      published_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString()
    }
  },
  {
    id: 5,
    stock: 'LG에너지솔루션',
    ticker: '373220',
    signal: '긍정',
    key_quote: 'GM과의 계약 연장이 긍정적입니다',
    reasoning: '북미 전기차 시장 확대와 배터리 수요 증가',
    created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    speakers: { name: '삼프로TV' },
    influencer_videos: {
      influencer_channels: {
        channel_name: '삼프로TV',
        channel_handle: '@3protv'
      },
      published_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString()
    }
  }
];

export default function MyStocksPage() {
  const [selectedChip, setSelectedChip] = useState('전체');
  const router = useRouter();
  const [feedItems, setFeedItems] = useState<FeedItem[]>([]);
  const [loading, setLoading] = useState(true);

  // 통합 피드 데이터 로드
  useEffect(() => {
    const loadIntegratedFeed = async () => {
      try {
        setLoading(true);
        console.log('Loading integrated feed...');
        
        // 1. 인플루언서 시그널 가져오기 (31개 모두)
        let influencerSignals = [];
        try {
          influencerSignals = await getLatestInfluencerSignals(50);
          console.log('✅ Supabase connection successful! Loaded signals:', influencerSignals.length);
        } catch (supabaseError) {
          console.error('❌ Supabase connection failed:', supabaseError);
          // Fallback: 더미 데이터 사용
          influencerSignals = getDummySignals();
          console.log('🔄 Using fallback dummy signals:', influencerSignals.length);
        }
        
        // 2. 모든 데이터 소스를 통합 피드 아이템으로 변환
        const allItems: FeedItem[] = [];
        
        // 인플루언서 시그널 변환
        influencerSignals.forEach((signal, index) => {
          const channelName = signal.influencer_videos?.influencer_channels?.channel_name || 
                            signal.influencer_videos?.influencer_channels?.channel_handle || 
                            '알 수 없는 채널';
          const speakerName = signal.speakers?.name || channelName;
          const publishedAt = signal.created_at || signal.influencer_videos?.published_at || signal.timestamp;
          
          console.log(`Signal ${index}:`, {
            id: signal.id,
            stock: signal.stock,
            signal: signal.signal,
            speaker: speakerName,
            channel: channelName,
            publishedAt: publishedAt,
            created_at: signal.created_at
          });
          
          allItems.push({
            id: `influencer_${signal.id || index}`,
            type: 'influencer',
            icon: getSignalIcon(signal.signal),
            categoryName: '인플루언서',
            stockName: signal.stock || '알 수 없는 종목',
            stockCode: signal.ticker || '',
            title: `${speakerName} → ${signal.stock} ${signal.signal}`,
            subtitle: signal.key_quote || '',
            time: getTimeAgo(publishedAt),
            date: formatDate(publishedAt),
            timestamp: new Date(publishedAt || 0).getTime(),
            source: speakerName,
            signal: signal.signal,
            keyQuote: signal.key_quote,
            reasoning: signal.reasoning,
            profileLink: `/profile/${getInfluencerSlug(channelName)}`,
            detailLink: `/stock/${signal.ticker}?tab=influencer`
          });
        });
        
        // 애널리스트 리포트 변환
        dummyAnalystReports.forEach((report) => {
          allItems.push({
            id: report.id,
            type: 'analyst',
            icon: '📊',
            categoryName: '애널리스트',
            stockName: report.stockName,
            stockCode: report.stockCode,
            title: `${report.firm} ${report.analyst} → ${report.stockName} 목표가 ${report.targetPrice}`,
            subtitle: report.summary,
            time: getTimeAgo(report.publishedAt),
            date: formatDate(report.publishedAt),
            timestamp: new Date(report.publishedAt).getTime(),
            source: `${report.firm} ${report.analyst}`,
            signal: report.rating,
            detailLink: `/stock/${report.stockCode}?tab=analyst`
          });
        });
        
        // 공시 변환
        dummyDisclosures.forEach((disclosure) => {
          allItems.push({
            id: disclosure.id,
            type: 'disclosure',
            icon: '📋',
            categoryName: '공시',
            stockName: disclosure.stockName,
            stockCode: disclosure.stockCode,
            title: `${disclosure.stockName} ${disclosure.title} (${disclosure.grade}등급)`,
            subtitle: disclosure.amount,
            time: getTimeAgo(disclosure.publishedAt),
            date: formatDate(disclosure.publishedAt),
            timestamp: new Date(disclosure.publishedAt).getTime(),
            source: 'DART',
            detailLink: `/stock/${disclosure.stockCode}?tab=disclosure`
          });
        });
        
        // 뉴스 변환
        dummyNews.forEach((news) => {
          allItems.push({
            id: news.id,
            type: 'news',
            icon: '📢',
            categoryName: '뉴스',
            stockName: news.stockName,
            stockCode: news.stockCode,
            title: news.title,
            subtitle: '',
            time: getTimeAgo(news.publishedAt),
            date: formatDate(news.publishedAt),
            timestamp: new Date(news.publishedAt).getTime(),
            source: news.source,
            detailLink: `/stock/${news.stockCode}?tab=feed`
          });
        });
        
        // 시간순 정렬 (최신순)
        allItems.sort((a, b) => b.timestamp - a.timestamp);
        
        console.log('Integrated feed loaded:', allItems.length, 'items');
        setFeedItems(allItems);
      } catch (error) {
        console.error('❌ Critical error loading integrated feed:', error);
        // 완전한 fallback: 더미 데이터만 사용
        const fallbackItems: FeedItem[] = [];
        
        // 더미 시그널을 피드 아이템으로 변환
        getDummySignals().forEach((signal, index) => {
          fallbackItems.push({
            id: `fallback_${signal.id}`,
            type: 'influencer',
            icon: getSignalIcon(signal.signal),
            categoryName: '인플루언서',
            stockName: signal.stock,
            stockCode: signal.ticker,
            title: `${signal.speakers?.name} → ${signal.stock} ${signal.signal}`,
            subtitle: signal.key_quote,
            time: getTimeAgo(signal.created_at),
            date: formatDate(signal.created_at),
            timestamp: new Date(signal.created_at).getTime(),
            source: signal.speakers?.name || '알 수 없음',
            signal: signal.signal,
            keyQuote: signal.key_quote,
            reasoning: signal.reasoning,
            profileLink: `/profile/korini_papa`,
            detailLink: `/stock/${signal.ticker}`
          });
        });
        
        console.log('🔄 Using complete fallback data:', fallbackItems.length, 'items');
        setFeedItems(fallbackItems);
      } finally {
        setLoading(false);
      }
    };

    loadIntegratedFeed();
  }, []);

  // 유틸리티 함수들
  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case '매수': return '🔵';
      case '긍정': return '🟢';
      case '중립': return '🟡';
      case '경계': return '🟠';
      case '매도': return '🔴';
      default: return '⚪';
    }
  };

  const getInfluencerSlug = (channelName: string) => {
    if (channelName.includes('슈카') || channelName.includes('syuka')) return 'syuka';
    if (channelName.includes('삼프로') || channelName.includes('3pro')) return '3protv';
    if (channelName.includes('코린이') || channelName.includes('korini')) return 'korini_papa';
    return 'unknown';
  };

  const getTimeAgo = (dateString: string | undefined) => {
    if (!dateString) return '시간 미상';
    
    try {
      const date = new Date(dateString);
      // Invalid Date 체크
      if (isNaN(date.getTime())) return '시간 미상';
      
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      
      const minutes = Math.floor(diff / (1000 * 60));
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      
      if (days > 0) return `${days}일 전`;
      if (hours > 0) return `${hours}시간 전`;
      if (minutes > 0) return `${minutes}분 전`;
      return '방금 전';
    } catch (error) {
      console.error('Error parsing date:', dateString, error);
      return '시간 미상';
    }
  };

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return '날짜 미상';
    
    try {
      const date = new Date(dateString);
      // Invalid Date 체크
      if (isNaN(date.getTime())) return '날짜 미상';
      
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      console.error('Error formatting date:', dateString, error);
      return '날짜 미상';
    }
  };

  // 종목 칩 클릭 핸들러
  const handleChipClick = (chip: typeof stockChips[0]) => {
    if (chip.name === '전체') {
      setSelectedChip('전체');
    } else if (chip.code) {
      // 종목 상세 페이지로 이동
      console.log('Navigating to stock page:', chip.code);
      router.push(`/stock/${chip.code}`);
    }
  };

  // 피드 아이템 클릭 핸들러
  const handleFeedItemClick = (item: FeedItem) => {
    if (item.detailLink) {
      router.push(item.detailLink);
    }
  };

  // 소스 클릭 핸들러 (프로필 페이지로 이동)
  const handleSourceClick = (item: FeedItem, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (item.profileLink) {
      router.push(item.profileLink);
    }
  };

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-[#191f28]">⭐ 내 종목</h1>
          <div className="text-sm text-[#8b95a1]">
            {loading ? '로딩 중...' : `${feedItems.length}개 업데이트`}
          </div>
        </div>
        <p className="text-sm text-[#8b95a1] mt-2">
          관심 종목의 실시간 통합 피드입니다. 종목을 클릭하면 상세 페이지로 이동합니다.
        </p>
      </div>

      {/* 관심종목 칩 */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1">
          {stockChips.map((chip, index) => (
            <button
              key={index}
              onClick={() => handleChipClick(chip)}
              className={`flex-shrink-0 px-4 py-2.5 rounded-full text-sm font-medium transition-colors ${
                selectedChip === chip.name
                  ? 'bg-[#3182f6] text-white'
                  : 'bg-[#f8f9fa] text-[#191f28] hover:bg-[#e9ecef]'
              }`}
            >
              <div className="flex items-center gap-1">
                <span>{chip.name}</span>
                {chip.change && (
                  <span className={`text-xs font-medium ${
                    selectedChip === chip.name 
                      ? 'text-white/90' 
                      : chip.isPositive 
                        ? 'text-[#f44336]' 
                        : 'text-[#3182f6]'
                  }`}>
                    {chip.change}
                  </span>
                )}
                {chip.name !== '전체' && (
                  <span className="text-xs text-gray-400 ml-1">→</span>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 통합 피드 리스트 */}
      <div className="px-4 py-4">
        <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <div className="text-lg text-[#8b95a1]">통합 피드를 불러오는 중...</div>
            </div>
          ) : feedItems.length > 0 ? (
            <div className="divide-y divide-[#f0f0f0]">
              {feedItems.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleFeedItemClick(item)}
                  className="px-4 py-4 hover:bg-[#f8f9fa] cursor-pointer transition-colors"
                >
                  <div className="flex items-start gap-3">
                    {/* 타입별 아이콘 */}
                    <div className="w-10 h-10 rounded-full bg-[#f8f9fa] flex items-center justify-center text-lg flex-shrink-0">
                      {item.icon}
                    </div>
                    
                    {/* 피드 내용 */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`text-sm font-medium px-2 py-0.5 rounded ${
                          item.type === 'influencer' ? 'text-[#8b95a1] bg-[#f2f4f6]' :
                          item.type === 'analyst' ? 'text-blue-700 bg-blue-50' :
                          item.type === 'disclosure' ? 'text-green-700 bg-green-50' :
                          'text-purple-700 bg-purple-50'
                        }`}>
                          {item.categoryName}
                        </span>
                        <span className="text-sm font-bold text-[#191f28]">
                          {item.stockName}
                        </span>
                        {item.signal && (
                          <span className={`text-xs font-medium px-2 py-0.5 rounded ${
                            item.signal === '매수' || item.signal === 'BUY' ? 'text-blue-600 bg-blue-50' :
                            item.signal === '긍정' ? 'text-green-600 bg-green-50' :
                            item.signal === '중립' ? 'text-yellow-600 bg-yellow-50' :
                            item.signal === '경계' ? 'text-orange-600 bg-orange-50' :
                            item.signal === '매도' ? 'text-red-600 bg-red-50' :
                            'text-gray-600 bg-gray-50'
                          }`}>
                            {item.signal}
                          </span>
                        )}
                      </div>

                      <h3 className="text-[15px] font-medium text-[#191f28] leading-[1.4] mb-2">
                        {item.title}
                      </h3>

                      {/* 부제목/요약 */}
                      {item.subtitle && (
                        <div className="mb-2">
                          <div className="text-sm text-[#191f28] bg-[#f8f9fa] px-2 py-1 rounded line-clamp-2">
                            {item.subtitle}
                          </div>
                        </div>
                      )}

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-[#8b95a1]">
                            {item.time}
                          </span>
                          <span className="text-xs text-[#8b95a1]">•</span>
                          <button
                            onClick={(e) => handleSourceClick(item, e)}
                            className="text-sm text-[#3182f6] hover:underline"
                          >
                            {item.source}
                          </button>
                        </div>
                        <div className="text-[#8b95a1] text-sm">
                          →
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center">
              <div className="text-4xl mb-4">📱</div>
              <div className="text-lg font-medium text-[#191f28] mb-2">
                아직 업데이트가 없습니다
              </div>
              <div className="text-sm text-[#8b95a1]">
                관심 종목의 새로운 소식이 업데이트될 때까지 기다려주세요
              </div>
            </div>
          )}
        </div>

        {/* 하단 설명 */}
        {feedItems.length > 0 && (
          <div className="mt-4 text-center">
            <p className="text-sm text-[#8b95a1]">
              항목을 클릭하면 해당 종목의 상세 페이지로 이동합니다
            </p>
          </div>
        )}
      </div>
    </div>
  );
}