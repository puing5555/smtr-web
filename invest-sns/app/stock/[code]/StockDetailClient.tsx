'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import StockChart from '@/components/StockChart';
import StockDisclosureTab from '@/components/stock/StockDisclosureTab';

interface StockDetailClientProps {
  code: string;
}

// 종목별 타임라인 이벤트
interface StockTimelineEvent {
  id: number;
  type: string;
  icon: string;
  categoryName: string;
  title: string;
  time: string;
  tab: string;
}

const getStockTimeline = (code: string): StockTimelineEvent[] => {
  const timelines: { [key: string]: StockTimelineEvent[] } = {
    '005930': [
      { id: 1, type: 'disclosure', icon: '🔵', categoryName: '공시', title: 'A등급 공시 - 3분기 실적 컨센서스 상회', time: '3분 전', tab: 'disclosure' },
      { id: 2, type: 'influencer', icon: '🟢', categoryName: '인플루언서', title: '슈카월드 긍정 신호', time: '1시간 전', tab: 'influencer' },
      { id: 3, type: 'report', icon: '📊', categoryName: '리포트', title: '한국투자증권 목표가 상향', time: '2시간 전', tab: 'reports' },
      { id: 4, type: 'insider', icon: '👔', categoryName: '임원매매', title: '이재용 사장 매수 5만주', time: '3시간 전', tab: 'insider' },
      { id: 5, type: 'earnings', icon: '📈', categoryName: '실적', title: '3분기 영업이익 컨센서스 상회', time: '5시간 전', tab: 'earnings' },
      { id: 6, type: 'influencer', icon: '🟢', categoryName: '인플루언서', title: '코린이아빠 매수 신호', time: '8시간 전', tab: 'influencer' },
      { id: 7, type: 'disclosure', icon: '🔵', categoryName: '공시', title: '자사주 매입 결정', time: '1일 전', tab: 'disclosure' },
    ],
    '005380': [
      { id: 1, type: 'report', icon: '📊', categoryName: '리포트', title: '한국투자증권 목표가 상향', time: '2시간 전', tab: 'reports' },
      { id: 2, type: 'earnings', icon: '📈', categoryName: '실적', title: '3분기 영업이익 컨센서스 상회', time: '5시간 전', tab: 'earnings' },
      { id: 3, type: 'disclosure', icon: '🔵', categoryName: '공시', title: '전기차 신모델 출시 공시', time: '1일 전', tab: 'disclosure' },
    ],
  };
  return timelines[code] || [
    { id: 1, type: 'disclosure', icon: '🔵', categoryName: '공시', title: '최근 공시 없음', time: '-', tab: 'disclosure' },
  ];
};

// 9개 탭 정의
const tabs = [
  { id: 'feed', label: '실시간', icon: '📱' },
  { id: 'influencer', label: '인플루언서', icon: '📈' },
  { id: 'analyst', label: '애널리스트', icon: '📊' },
  { id: 'disclosure', label: '공시', icon: '📋' },
  { id: 'earnings', label: '실적', icon: '📈' },
  { id: 'reports', label: '리포트', icon: '📄' },
  { id: 'insider', label: '임원매매', icon: '💼' },
  { id: 'calendar', label: '일정', icon: '📅' },
  { id: 'memo', label: '메모', icon: '📝' },
];

// 종목 데이터
const getStockData = (code: string) => {
  const stockMap: { [key: string]: any } = {
    '005930': { name: '삼성전자', price: 68500, change: 1200, changePercent: 1.78 },
    '000660': { name: 'SK하이닉스', price: 178000, change: -2100, changePercent: -1.16 },
    '035420': { name: 'NAVER', price: 185500, change: 3200, changePercent: 1.76 },
    '051910': { name: 'LG화학', price: 412000, change: -5500, changePercent: -1.32 },
    '005380': { name: '현대차', price: 221000, change: 4500, changePercent: 2.08 },
    '399720': { name: 'AION', price: 15200, change: 800, changePercent: 5.56 },
    '009540': { name: 'HD한국조선해양', price: 167000, change: -3000, changePercent: -1.76 },
    '086520': { name: '에코프로', price: 89400, change: 2100, changePercent: 2.41 },
  };

  return stockMap[code] || { name: `종목 ${code}`, price: 50000, change: 0, changePercent: 0 };
};

export default function StockDetailClient({ code }: StockDetailClientProps) {
  const [activeTab, setActiveTab] = useState('feed');
  const [isWatched, setIsWatched] = useState(false);
  const [showComments, setShowComments] = useState<{ [key: number]: boolean }>({});
  const [commentInputs, setCommentInputs] = useState<{ [key: number]: string }>({});
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const searchParams = useSearchParams();
  const router = useRouter();
  
  // 안전하게 데이터 로드
  let stockData, timeline;
  try {
    stockData = getStockData(code);
    timeline = getStockTimeline(code);
    console.log('✅ Stock data loaded successfully for code:', code);
  } catch (error) {
    console.error('❌ Error loading stock data:', error);
    setHasError(true);
    setErrorMessage('종목 정보를 불러오는 중 오류가 발생했습니다.');
    stockData = { 
      name: '알 수 없는 종목', 
      price: '---', 
      change: '0.00', 
      changePercent: '0.00%', 
      isPositive: true 
    };
    timeline = [];
  }

  // URL 쿼리 파라미터에서 탭 설정
  useEffect(() => {
    try {
      const tabParam = searchParams.get('tab');
      if (tabParam && tabs.some(tab => tab.id === tabParam)) {
        setActiveTab(tabParam);
      }
    } catch (error) {
      console.error('Error reading tab parameter:', error);
    }
  }, [searchParams]);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'feed':
        return (
          <div className="space-y-6">
            {/* 주가 차트 */}
            <StockChart 
              stockCode={code}
              stockName={stockData.name}
              signals={[]}
            />
            
            {/* 타임라인 이벤트 */}
            <div className="space-y-4">
            {timeline.map((event) => (
              <div key={event.id} className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
                <div
                  onClick={() => setActiveTab(event.tab)}
                  className="px-4 py-4 hover:bg-[#f8f9fa] cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-[#f8f9fa] flex items-center justify-center text-lg flex-shrink-0">
                      {event.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium text-[#8b95a1] bg-[#f2f4f6] px-2 py-0.5 rounded">
                          {event.categoryName}
                        </span>
                        <span className="text-xs text-[#8b95a1]">{event.time}</span>
                      </div>
                      <h3 className="text-sm font-medium text-[#191f28] leading-[1.4] mb-2">
                        {event.title}
                      </h3>
                      
                      {/* 액션 버튼들 */}
                      <div className="flex items-center gap-4 text-xs text-[#8b95a1]">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setShowComments(prev => ({
                              ...prev,
                              [event.id]: !prev[event.id]
                            }));
                          }}
                          className="hover:text-[#191f28] transition-colors"
                        >
                          💬 댓글 {Math.floor(Math.random() * 10) + 1}개
                        </button>
                        <button className="hover:text-[#191f28] transition-colors">
                          ❤️ 좋아요 {Math.floor(Math.random() * 50) + 5}개
                        </button>
                      </div>
                      
                      {/* 댓글 입력란 */}
                      {showComments[event.id] && (
                        <div className="mt-4 pt-4 border-t border-[#f0f0f0]">
                          <div className="flex gap-2">
                            <input
                              type="text"
                              placeholder="댓글을 입력하세요..."
                              value={commentInputs[event.id] || ''}
                              onChange={(e) => {
                                setCommentInputs(prev => ({
                                  ...prev,
                                  [event.id]: e.target.value
                                }));
                              }}
                              onClick={(e) => e.stopPropagation()}
                              className="flex-1 px-3 py-2 text-sm border border-[#e8e8e8] rounded-lg focus:outline-none focus:border-[#3182f6]"
                            />
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                if (commentInputs[event.id]?.trim()) {
                                  alert('댓글이 등록되었습니다: ' + commentInputs[event.id]);
                                  setCommentInputs(prev => ({
                                    ...prev,
                                    [event.id]: ''
                                  }));
                                }
                              }}
                              className="px-4 py-2 bg-[#3182f6] text-white text-sm rounded-lg hover:bg-[#2171e5] transition-colors"
                            >
                              등록
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="text-[#8b95a1] text-sm">
                      →
                    </div>
                  </div>
                </div>
                
                {/* 댓글 목록 */}
                {showComments[event.id] && (
                  <div className="px-4 pb-4 space-y-3">
                    {[1, 2, 3].map(commentIndex => (
                      <div key={commentIndex} className="flex gap-3 p-3 bg-[#f8f9fa] rounded-lg">
                        <div className="w-8 h-8 bg-[#3182f6] rounded-full flex items-center justify-center text-white text-xs font-bold">
                          U{commentIndex}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-[#191f28]">사용자{commentIndex}</span>
                            <span className="text-xs text-[#8b95a1]">{commentIndex}분 전</span>
                          </div>
                          <p className="text-xs text-[#191f28]">
                            {commentIndex === 1 && "좋은 정보네요! 감사합니다."}
                            {commentIndex === 2 && "이런 시점에서 매수하는게 맞을까요?"}
                            {commentIndex === 3 && "저도 같은 생각입니다. 긍정적으로 보고 있어요."}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            </div>
          </div>
        );

      case 'influencer':
        return <InfluencerTab code={code} />;
      
      case 'analyst':
        return <AnalystTab code={code} />;
        
      case 'disclosure':
        return <StockDisclosureTab code={code} />;
        
      case 'earnings':
        return (
          <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
            <h3 className="text-lg font-bold mb-4">📈 실적 정보</h3>
            <p className="text-gray-500">실적 데이터를 준비 중입니다.</p>
          </div>
        );
        
      case 'reports':
        return (
          <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
            <h3 className="text-lg font-bold mb-4">📄 리포트</h3>
            <p className="text-gray-500">리포트 데이터를 준비 중입니다.</p>
          </div>
        );
        
      case 'insider':
        return (
          <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
            <h3 className="text-lg font-bold mb-4">💼 임원매매</h3>
            <p className="text-gray-500">임원매매 데이터를 준비 중입니다.</p>
          </div>
        );
        
      case 'calendar':
        return (
          <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
            <h3 className="text-lg font-bold mb-4">📅 일정</h3>
            <p className="text-gray-500">일정 데이터를 준비 중입니다.</p>
          </div>
        );
        
      case 'memo':
        return (
          <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
            <h3 className="text-lg font-bold mb-4">📝 메모</h3>
            <div className="space-y-4">
              <textarea
                placeholder="이 종목에 대한 메모를 작성하세요..."
                className="w-full h-32 p-3 border border-gray-200 rounded-lg resize-none focus:outline-none focus:border-blue-500"
              />
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                메모 저장
              </button>
            </div>
          </div>
        );
        
      default:
        return <div>준비중</div>;
    }
  };

  // 에러 상태일 때 fallback UI 표시
  if (hasError) {
    return (
      <div className="min-h-screen bg-[#f4f4f4] flex items-center justify-center">
        <div className="text-center p-8">
          <div className="text-4xl mb-4">⚠️</div>
          <div className="text-lg font-medium text-[#191f28] mb-2">
            오류가 발생했습니다
          </div>
          <div className="text-sm text-[#8b95a1] mb-4">
            {errorMessage}
          </div>
          <button
            onClick={() => {
              setHasError(false);
              window.location.reload();
            }}
            className="px-4 py-2 bg-[#3182f6] text-white rounded-lg hover:bg-[#2171e5] transition-colors"
          >
            다시 시도
          </button>
          <div className="mt-4">
            <button
              onClick={() => router.push('/my-stocks')}
              className="text-[#3182f6] hover:underline text-sm"
            >
              내 종목으로 돌아가기
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Stock Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-6">
        <div>
          {/* 뒤로가기 버튼 */}
          <div className="mb-4">
            <button
              onClick={() => router.push('/my-stocks')}
              className="flex items-center gap-2 text-[#8b95a1] hover:text-[#191f28] transition-colors"
            >
              <span className="text-lg">←</span>
              <span className="text-sm">내 종목</span>
            </button>
          </div>

          {/* 종목 정보 */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-[#191f28] mb-2">{stockData.name}</h1>
              <div className="flex items-baseline gap-4">
                <span className="text-3xl font-bold text-[#191f28]">
                  {stockData.price.toLocaleString()}원
                </span>
                <span className={`text-lg font-medium ${
                  stockData.change >= 0 ? 'text-[#f44336]' : 'text-[#3182f6]'
                }`}>
                  {stockData.change >= 0 ? '+' : ''}{stockData.change.toLocaleString()}원
                  ({stockData.change >= 0 ? '+' : ''}{stockData.changePercent}%)
                </span>
              </div>
            </div>

            {/* 관심종목 버튼 */}
            <button
              onClick={() => setIsWatched(!isWatched)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isWatched
                  ? 'bg-[#3182f6] text-white'
                  : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
              }`}
            >
              {isWatched ? '⭐ 관심종목' : '☆ 관심종목'}
            </button>
          </div>

          {/* 9개 탭 메뉴 */}
          <div className="flex gap-6 overflow-x-auto scrollbar-hide pb-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative pb-3 px-1 text-sm font-medium transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'text-[#3182f6]'
                    : 'text-[#8b95a1] hover:text-[#191f28]'
                }`}
              >
                {tab.label}
                {activeTab === tab.id && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#3182f6]" />
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-6">
        {renderTabContent()}
      </div>
    </div>
  );
}

// 인플루언서 탭 컴포넌트 (실제 Supabase 데이터 사용)
function InfluencerTab({ code }: { code: string }) {
  const [periodFilter, setPeriodFilter] = useState('전체');
  const [influencerFilter, setInfluencerFilter] = useState('전체');
  const [signalData, setSignalData] = useState<any[]>([]);
  const [influencerOptions, setInfluencerOptions] = useState([
    { name: '전체', count: null }
  ]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const periodOptions = ['전체', '1개월', '6개월', '1년', '3년'];

  // 실제 Supabase 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('🔄 Loading influencer signals for code:', code);
        
        // 안전한 Supabase import
        try {
          const { getStockSignals } = await import('@/lib/supabase');
          const signals = await getStockSignals(code);
          console.log('✅ Successfully loaded', signals.length, 'signals from Supabase');
          
          if (signals.length === 0) {
            console.log('ℹ️ No signals found for stock code:', code);
            setSignalData([]);
            setInfluencerOptions([{ name: '전체', count: null }]);
            return;
          }
          
          // 데이터를 UI용 형태로 변환
          const transformedSignals = signals.map((signal: any) => {
            const publishedDate = signal.influencer_videos?.published_at 
              ? new Date(signal.influencer_videos.published_at)
              : signal.created_at 
              ? new Date(signal.created_at)
              : new Date();
            
            const videoUrl = signal.influencer_videos?.video_id 
              ? `https://youtube.com/watch?v=${signal.influencer_videos.video_id}`
              : '#';

            return {
              date: publishedDate.toISOString().split('T')[0],
              influencer: signal.speakers?.name || 
                         signal.influencer_videos?.influencer_channels?.channel_name || 
                         '알 수 없는 인플루언서',
              signal: signal.signal,
              quote: signal.key_quote || '키 인용문이 없습니다.',
              return: 'N/A', // 수익률은 계산하지 않음 (하드코딩 금지)
              videoUrl,
              price: 0
            };
          });
          
          setSignalData(transformedSignals);
          
          // 인플루언서별 카운트 생성
          const influencerCounts = transformedSignals.reduce((acc: any, signal: any) => {
            acc[signal.influencer] = (acc[signal.influencer] || 0) + 1;
            return acc;
          }, {});
          
          const influencerOpts = [
            { name: '전체', count: null },
            ...Object.entries(influencerCounts).map(([name, count]) => ({
              name,
              count
            }))
          ];
          
          setInfluencerOptions(influencerOpts);
          
        } catch (supabaseError) {
          console.error('❌ Supabase connection failed:', supabaseError);
          setError('데이터베이스 연결에 실패했습니다.');
          setSignalData([]);
          setInfluencerOptions([{ name: '전체', count: null }]);
        }
        
      } catch (error) {
        console.error('❌ Error loading stock signals:', error);
        setError('시그널 데이터를 불러오는 중 오류가 발생했습니다.');
        setSignalData([]);
      } finally {
        setLoading(false);
      }
    };

    if (code) {
      loadData();
    }
  }, [code]);

  const getLocalSignalColor = (signal: string) => {
    switch (signal) {
      case '매수':
      case 'BUY': return 'text-blue-600 bg-blue-100';
      case '긍정':
      case 'POSITIVE': return 'text-green-600 bg-green-100';
      case '중립':
      case 'NEUTRAL': return 'text-yellow-600 bg-yellow-100';
      case '경계':
      case 'CONCERN': return 'text-orange-600 bg-orange-100';
      case '매도':
      case 'SELL': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSignalEmoji = (signal: string) => {
    switch (signal) {
      case '매수':
      case 'BUY': return '🔵';
      case '긍정':
      case 'POSITIVE': return '🟢';
      case '중립':
      case 'NEUTRAL': return '🟡';
      case '경계':
      case 'CONCERN': return '🟠';
      case '매도':
      case 'SELL': return '🔴';
      default: return '⚪';
    }
  };

  const getSignalText = (signal: string) => {
    return signal;
  };

  const getFilteredSignals = () => {
    let filtered = signalData;

    if (influencerFilter !== '전체') {
      filtered = filtered.filter(signal => signal.influencer === influencerFilter);
    }

    // 기간 필터 (간단한 구현)
    if (periodFilter !== '전체') {
      const now = new Date();
      let cutoffDate = new Date();
      
      switch (periodFilter) {
        case '1개월':
          cutoffDate.setMonth(now.getMonth() - 1);
          break;
        case '6개월':
          cutoffDate.setMonth(now.getMonth() - 6);
          break;
        case '1년':
          cutoffDate.setFullYear(now.getFullYear() - 1);
          break;
        case '3년':
          cutoffDate.setFullYear(now.getFullYear() - 3);
          break;
      }
      
      filtered = filtered.filter(signal => new Date(signal.date) >= cutoffDate);
    }

    return filtered;
  };

  const filteredSignals = getFilteredSignals();

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-8 text-center">
        <div className="text-lg text-[#8b95a1]">📈 인플루언서 시그널을 불러오는 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-8 text-center">
        <div className="text-4xl mb-4">⚠️</div>
        <div className="text-lg font-medium text-[#191f28] mb-2">오류가 발생했습니다</div>
        <div className="text-sm text-[#8b95a1]">{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Yahoo Finance 차트 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <h3 className="text-lg font-bold mb-4">📈 주가 차트 + 시그널 오버레이</h3>
        <StockChart 
          stockCode={code}
          stockName=""
          signals={signalData}
        />
      </div>

      <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
        {/* 필터 */}
        <div className="p-4 border-b border-[#f0f0f0]">
          <div className="flex gap-4 mb-4">
            {/* 기간 필터 */}
            <div className="flex gap-2">
              {periodOptions.map((period) => (
                <button
                  key={period}
                  onClick={() => setPeriodFilter(period)}
                  className={`px-3 py-1 text-sm rounded-full transition-colors ${
                    periodFilter === period
                      ? 'bg-[#3182f6] text-white'
                      : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
                  }`}
                >
                  {period}
                </button>
              ))}
            </div>
          </div>
          
          {/* 인플루언서 필터 */}
          <div className="flex gap-2 flex-wrap">
            {influencerOptions.map((option) => (
              <button
                key={option.name}
                onClick={() => setInfluencerFilter(option.name)}
                className={`px-3 py-1 text-sm rounded-full transition-colors ${
                  influencerFilter === option.name
                    ? 'bg-[#3182f6] text-white'
                    : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
                }`}
              >
                {option.name}
                {option.count && ` (${option.count})`}
              </button>
            ))}
          </div>
        </div>

        {/* 시그널이 없는 경우 */}
        {signalData.length === 0 ? (
          <div className="p-8 text-center">
            <div className="text-4xl mb-4">📈</div>
            <div className="text-lg font-medium text-[#191f28] mb-2">
              아직 시그널이 없습니다
            </div>
            <div className="text-sm text-[#8b95a1]">
              이 종목에 대한 인플루언서 시그널이 아직 없습니다.
            </div>
          </div>
        ) : filteredSignals.length === 0 ? (
          <div className="p-8 text-center">
            <div className="text-4xl mb-4">🔍</div>
            <div className="text-lg font-medium text-[#191f28] mb-2">
              필터 조건에 맞는 시그널이 없습니다
            </div>
            <div className="text-sm text-[#8b95a1]">
              다른 필터 조건을 시도해보세요.
            </div>
          </div>
        ) : (
          /* 시그널 테이블 */
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#f8f9fa] border-b border-[#f0f0f0]">
                <tr>
                  <th className="text-left px-4 py-3 text-sm font-medium text-[#8b95a1]">날짜</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-[#8b95a1]">인플루언서</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-[#8b95a1]">시그널</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-[#8b95a1]">핵심 발언</th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-[#8b95a1]">영상</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#f0f0f0]">
                {filteredSignals.map((signal, index) => (
                  <tr key={index} className="hover:bg-[#f8f9fa]">
                    <td className="px-4 py-4 text-sm text-[#191f28]">
                      {new Date(signal.date).toLocaleDateString('ko-KR', { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </td>
                    <td className="px-4 py-4 text-sm font-medium text-[#191f28]">
                      {signal.influencer}
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{getSignalEmoji(signal.signal)}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getLocalSignalColor(signal.signal)}`}>
                          {getSignalText(signal.signal)}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-4 text-sm text-[#191f28] max-w-xs">
                      <div className="truncate">{signal.quote}</div>
                    </td>
                    <td className="px-4 py-4">
                      <a
                        href={signal.videoUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[#3182f6] hover:text-[#2171e5] text-sm font-medium"
                      >
                        영상보기 →
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// 애널리스트 탭 컴포넌트
function AnalystTab({ code }: { code: string }) {
  return (
    <div className="space-y-6">
      {/* 차트 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <h3 className="text-lg font-bold mb-4">📊 애널리스트 차트</h3>
        <StockChart 
          stockCode={code}
          stockName=""
          signals={[]}
        />
      </div>
      
      {/* 애널리스트 리포트 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <h3 className="text-lg font-bold mb-4">📊 애널리스트 리포트</h3>
        <div className="text-center py-8">
          <div className="text-4xl mb-4">📊</div>
          <div className="text-lg font-medium text-[#191f28] mb-2">
            애널리스트 리포트 준비중
          </div>
          <div className="text-sm text-[#8b95a1]">
            애널리스트 리포트 데이터를 준비 중입니다.
          </div>
        </div>
      </div>
    </div>
  );
}