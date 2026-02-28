'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { getStockSignals, getSignalColor } from '@/lib/supabase';
import StockChart from '@/components/StockChart';
import StockDisclosureTab from '@/components/stock/StockDisclosureTab';
import FeedCard from '@/components/FeedCard';
import { influencers } from '@/data/influencerData';
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

// 탭 정의
const tabs = [
  { id: 'feed', label: '피드', icon: '📱' },
  { id: 'influencer', label: '인플루언서', icon: '📈' },
  { id: 'analyst', label: '애널리스트', icon: '📊' },
  { id: 'disclosure', label: '공시', icon: '📋' },
  { id: 'earnings', label: '실적', icon: '📈' },
  { id: 'reports', label: '리포트', icon: '📄' },
  { id: 'insider', label: '임원매매', icon: '💼' },
  { id: 'calendar', label: '일정', icon: '📅' },
  { id: 'memo', label: '메모', icon: '📝' },
];

// 더미 종목 데이터
const getStockData = (code: string) => {
  const stockMap: { [key: string]: any } = {
    '005930': { name: '삼성전자', price: 68500, change: 1200, changePercent: 1.78 },
    '000660': { name: 'SK하이닉스', price: 178000, change: -2100, changePercent: -1.16 },
    '035420': { name: 'NAVER', price: 185500, change: 3200, changePercent: 1.76 },
    '051910': { name: 'LG화학', price: 412000, change: -5500, changePercent: -1.32 },
    '005380': { name: '현대차', price: 221000, change: 4500, changePercent: 2.08 },
  };

  return stockMap[code] || { name: `종목 ${code}`, price: 50000, change: 0, changePercent: 0 };
};

export default function StockDetailClient({ code }: StockDetailClientProps) {
  const [activeTab, setActiveTab] = useState('feed');
  const [isWatched, setIsWatched] = useState(false);
  const searchParams = useSearchParams();
  const router = useRouter();
  const stockData = getStockData(code);
  const timeline = getStockTimeline(code);

  // URL 쿼리 파라미터에서 탭 설정
  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam && tabs.some(tab => tab.id === tabParam)) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  // 해당 종목의 시그널 가져오기
  const getStockSignals = (code: string, name: string) => {
    const stockMapping: { [key: string]: string[] } = {
      '005930': ['삼성전자', '삼성'],
      '000660': ['SK하이닉스', '하이닉스'],
      '035420': ['네이버', 'NAVER'],
      '051910': ['LG화학'],
      '005380': ['현대차', '현대자동차'],
      '005490': ['POSCO홀딩스', '포스코'],
      'BTC': ['비트코인', 'Bitcoin'],
      'ETH': ['이더리움', 'Ethereum']
    };

    const possibleNames = stockMapping[code] || [name];
    const signals: any[] = [];
    
    influencers.forEach(influencer => {
      influencer.recentCalls.forEach(call => {
        const isMatch = possibleNames.some(stockName => 
          call.stock.includes(stockName) || stockName.includes(call.stock)
        );
        
        if (isMatch) {
          signals.push({
            id: `${influencer.id}-${call.stock}`,
            stock: call.stock,
            signal_type: call.direction,
            speaker: influencer.name,
            content_snippet: `${call.stock} ${call.direction} 추천`,
            date: call.date,
            video_published_at: call.date,
            accuracy_rate: influencer.accuracy,
            return_rate: call.returnRate,
            status: call.status
          });
        }
      });
    });
    
    return signals;
  };

  const stockSignals = getStockSignals(code, stockData.name);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'feed':
        return (
          <div className="space-y-4">
            {timeline.map((event) => (
              <FeedCard
                key={event.id}
                icon={event.icon}
                categoryName={event.categoryName}
                title={event.title}
                date={event.time}
                onClick={() => setActiveTab(event.tab)}
              />
            ))}
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
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">실적 분석</h3>
            <p className="text-[#8b95a1]">상세 실적 분석을 준비중입니다</p>
          </div>
        );

      case 'reports':
        return (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📄</div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">리서치 리포트</h3>
            <p className="text-[#8b95a1]">증권사 리포트를 준비중입니다</p>
          </div>
        );

      case 'insider':
        return (
          <div className="space-y-4">
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <h4 className="font-bold text-[#191f28] mb-4">임원 매매 현황</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <div>
                    <div className="font-medium text-red-800">김○○ 전무 매도</div>
                    <div className="text-sm text-red-600">5억원 규모 • 3일 전</div>
                  </div>
                  <div className="text-red-600 font-bold">-1.2%</div>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div>
                    <div className="font-medium text-blue-800">박○○ 상무 매수</div>
                    <div className="text-sm text-blue-600">3억원 규모 • 1주 전</div>
                  </div>
                  <div className="text-blue-600 font-bold">+0.8%</div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'calendar':
        return (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📅</div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">종목 일정</h3>
            <p className="text-[#8b95a1]">실적발표, 주주총회 등 일정을 준비중입니다</p>
          </div>
        );

      case 'memo':
        return (
          <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
            <h4 className="font-bold text-[#191f28] mb-4">내 메모</h4>
            <div className="space-y-4">
              <textarea
                placeholder="이 종목에 대한 메모를 작성해보세요..."
                className="w-full h-32 p-3 border border-[#e8e8e8] rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
              />
              <div className="flex justify-end">
                <button className="px-4 py-2 bg-[#3182f6] text-white rounded-lg hover:bg-[#2171e5] transition-colors">
                  저장
                </button>
              </div>
            </div>
          </div>
        );

      default:
        return <div>준비중</div>;
    }
  };

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
              <span className="text-sm">내 종목으로</span>
            </button>
          </div>

          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-[#191f28]">
                {stockData.name}
                <span className="text-lg text-[#8b95a1] font-normal ml-2">
                  {code}
                </span>
              </h1>
              <div className="flex items-center gap-4 mt-2">
                <span className="text-3xl font-bold text-[#191f28]">
                  {stockData.price.toLocaleString()}원
                </span>
                <span className={`text-lg font-medium ${
                  stockData.change >= 0 ? 'text-red-500' : 'text-blue-500'
                }`}>
                  {stockData.change >= 0 ? '+' : ''}{stockData.change.toLocaleString()}원
                  ({stockData.change >= 0 ? '+' : ''}{stockData.changePercent}%)
                </span>
              </div>
              
              {/* Coverage Stats */}
              <div className="flex items-center gap-4 mt-3 text-sm text-[#8b95a1]">
                <span>인플루언서 12명</span>
                <span>•</span>
                <span>애널리스트 8명</span>
                <span>•</span>
                <span>투자자 5명</span>
                <span>•</span>
                <span>팔로워 3,247명</span>
              </div>
            </div>
            
            {/* Watch Button */}
            <button
              onClick={() => setIsWatched(!isWatched)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isWatched
                  ? 'bg-green-100 text-green-700 border border-green-200'
                  : 'bg-[#3182f6] text-white hover:bg-[#2171e5]'
              }`}
            >
              {isWatched ? '✓ 관심종목 등록됨' : '+ 관심종목 추가'}
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-[#e8e8e8]">
        <div className="px-4">
          <div className="flex overflow-x-auto scrollbar-hide">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-shrink-0 flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors relative ${
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

// 애널리스트 탭 컴포넌트
function AnalystTab({ code }: { code: string }) {
  const stockData = getStockData(code);

  // 더미 애널리스트 데이터
  const analystReports = [
    {
      analyst: '김선우',
      firm: '한국투자증권',
      rating: '매수',
      targetPrice: 85000,
      currentPrice: stockData.price,
      date: '2024-02-15',
      title: `${stockData.name} 3분기 실적 컨센서스 상회 예상`,
      summary: 'AI 반도체 수요 증가로 인한 실적 개선 기대',
    },
    {
      analyst: '이미래',
      firm: '미래에셋증권',
      rating: '매수',
      targetPrice: 82000,
      currentPrice: stockData.price,
      date: '2024-02-10',
      title: `${stockData.name} 메모리 업황 회복 본격화`,
      summary: '2024년 하반기부터 메모리 수요 회복세 지속 전망',
    },
    {
      analyst: '박테크',
      firm: '삼성증권',
      rating: '중립',
      targetPrice: 70000,
      currentPrice: stockData.price,
      date: '2024-02-05',
      title: `${stockData.name} 단기 조정 후 재평가 필요`,
      summary: '밸류에이션 부담은 있으나 중장기 성장성은 긍정적',
    },
  ];

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case '매수': return 'text-blue-600 bg-blue-100';
      case '중립': return 'text-yellow-600 bg-yellow-100';
      case '매도': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getUpside = (target: number, current: number) => {
    return ((target - current) / current * 100).toFixed(1);
  };

  return (
    <div className="space-y-6">
      {/* 주가 차트 + 목표주가 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <div className="flex justify-between items-center mb-4">
          <h4 className="font-medium text-[#191f28]">주가 차트 & 목표주가</h4>
          <div className="text-sm text-[#8b95a1]">
            애널리스트 {analystReports.length}명
          </div>
        </div>
        
        <div className="relative h-80 bg-[#f8f9fa] rounded-lg overflow-hidden">
          <svg className="w-full h-full" viewBox="0 0 400 200">
            {/* 배경 격자 */}
            <defs>
              <pattern id="grid-analyst" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e8e8e8" strokeWidth="0.5"/>
              </pattern>
              <linearGradient id="priceGradient-analyst" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#3182f6" stopOpacity="0.2"/>
                <stop offset="100%" stopColor="#3182f6" stopOpacity="0.05"/>
              </linearGradient>
            </defs>
            
            <rect width="100%" height="100%" fill="url(#grid-analyst)" />
            
            {/* 주가 라인 */}
            <path
              d="M 20 120 L 60 100 L 100 90 L 140 110 L 180 80 L 220 70 L 260 85 L 300 65 L 340 75 L 380 60"
              fill="none"
              stroke="#3182f6"
              strokeWidth="3"
            />
            
            {/* 주가 영역 */}
            <path
              d="M 20 120 L 60 100 L 100 90 L 140 110 L 180 80 L 220 70 L 260 85 L 300 65 L 340 75 L 380 60 L 380 200 L 20 200 Z"
              fill="url(#priceGradient-analyst)"
            />
            
            {/* 목표주가 라인들 */}
            <line x1="20" y1="40" x2="380" y2="40" stroke="#dc3545" strokeWidth="2" strokeDasharray="5,5" opacity="0.8" />
            <line x1="20" y1="50" x2="380" y2="50" stroke="#28a745" strokeWidth="2" strokeDasharray="5,5" opacity="0.8" />
            <line x1="20" y1="80" x2="380" y2="80" stroke="#ffc107" strokeWidth="2" strokeDasharray="5,5" opacity="0.8" />
            
            {/* 현재가 라인 */}
            <line x1="20" y1="60" x2="380" y2="60" stroke="#3182f6" strokeWidth="2" opacity="0.9" />
            
            {/* 목표가 라벨 */}
            <text x="385" y="45" className="text-xs fill-red-600">85,000원</text>
            <text x="385" y="55" className="text-xs fill-green-600">82,000원</text>
            <text x="385" y="85" className="text-xs fill-yellow-600">70,000원</text>
            <text x="385" y="65" className="text-xs fill-blue-600">현재가</text>
          </svg>
        </div>
        
        {/* 목표주가 요약 */}
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-sm text-[#8b95a1] mb-1">평균 목표가</div>
            <div className="text-lg font-bold text-[#191f28]">
              {Math.round(analystReports.reduce((sum, report) => sum + report.targetPrice, 0) / analystReports.length).toLocaleString()}원
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-[#8b95a1] mb-1">평균 상승여력</div>
            <div className="text-lg font-bold text-green-600">
              +{Math.round(analystReports.reduce((sum, report) => sum + parseFloat(getUpside(report.targetPrice, report.currentPrice)), 0) / analystReports.length)}%
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-[#8b95a1] mb-1">매수 의견</div>
            <div className="text-lg font-bold text-blue-600">
              {analystReports.filter(r => r.rating === '매수').length}/{analystReports.length}
            </div>
          </div>
        </div>
      </div>

      {/* 애널리스트 리포트 목록 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
        <div className="p-6 border-b border-[#e8e8e8]">
          <h4 className="font-medium text-[#191f28]">애널리스트 리포트</h4>
        </div>
        <div className="divide-y divide-[#f0f0f0]">
          {analystReports.map((report, index) => (
            <div key={index} className="p-6 hover:bg-[#f8f9fa] transition-colors">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-blue-800">
                      {report.analyst[0]}
                    </span>
                  </div>
                  <div>
                    <div className="font-medium text-[#191f28]">{report.analyst}</div>
                    <div className="text-sm text-[#8b95a1]">{report.firm}</div>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getRatingColor(report.rating)}`}>
                    {report.rating}
                  </span>
                  <div className="text-sm text-[#8b95a1] mt-1">
                    {new Date(report.date).toLocaleDateString('ko-KR', { 
                      month: 'short', 
                      day: 'numeric' 
                    })}
                  </div>
                </div>
              </div>

              <div className="mb-3">
                <h5 className="font-medium text-[#191f28] mb-1">{report.title}</h5>
                <p className="text-sm text-[#8b95a1]">{report.summary}</p>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-[#f0f0f0]">
                <div className="flex gap-4 text-sm">
                  <div>
                    <span className="text-[#8b95a1]">목표가: </span>
                    <span className="font-medium text-[#191f28]">
                      {report.targetPrice.toLocaleString()}원
                    </span>
                  </div>
                  <div>
                    <span className="text-[#8b95a1]">상승여력: </span>
                    <span className={`font-medium ${
                      parseFloat(getUpside(report.targetPrice, report.currentPrice)) > 0 
                        ? 'text-green-600' 
                        : 'text-red-600'
                    }`}>
                      {getUpside(report.targetPrice, report.currentPrice)}%
                    </span>
                  </div>
                </div>
                <button className="text-[#3182f6] hover:text-[#2171e5] text-sm font-medium">
                  리포트 보기 →
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// 인플루언서 탭 컴포넌트
function InfluencerTab({ code }: { code: string }) {
  const [periodFilter, setPeriodFilter] = useState('전체');
  const [influencerFilter, setInfluencerFilter] = useState('전체');
  const [signalData, setSignalData] = useState<any[]>([]);
  const [influencerOptions, setInfluencerOptions] = useState([
    { name: '전체', count: null }
  ]);
  const [loading, setLoading] = useState(true);

  const periodOptions = ['1개월', '6개월', '1년', '3년', '전체'];

  // 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        const { getStockSignals } = await import('@/lib/supabase');
        const signals = await getStockSignals(code);
        
        // 데이터를 UI용 형태로 변환
        const transformedSignals = signals.map((signal: any) => {
          const publishedDate = signal.influencer_videos?.published_at 
            ? new Date(signal.influencer_videos.published_at)
            : new Date();
          
          const videoUrl = signal.influencer_videos?.video_id 
            ? `https://youtube.com/watch?v=${signal.influencer_videos.video_id}`
            : '#';

          return {
            date: publishedDate.toISOString().split('T')[0],
            influencer: signal.speakers?.name || signal.influencer_videos?.influencer_channels?.channel_name || 'Unknown',
            signal: signal.signal,
            quote: signal.key_quote || '키 인용문이 없습니다.',
            return: 'N/A', // TODO: 수익률 계산
            videoUrl,
            price: 0 // TODO: 발언 시점 주가
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
            count: count as number
          }))
        ];
        
        setInfluencerOptions(influencerOpts);
      } catch (error) {
        console.error('Error loading stock signals:', error);
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
    // DB는 한글로 저장되어 있으므로 그대로 반환
    return signal;
  };

  // 필터링된 데이터 계산
  const getFilteredSignals = () => {
    let filtered = [...signalData];
    
    // 인플루언서 필터
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
      <div className="text-center py-8">
        <div className="text-lg text-[#8b95a1]">데이터를 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 필터 섹션 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <div className="space-y-4">
          {/* 기간 필터 */}
          <div>
            <h4 className="font-medium text-[#191f28] mb-3">기간</h4>
            <div className="flex gap-2 flex-wrap">
              {periodOptions.map((period) => (
                <button
                  key={period}
                  onClick={() => setPeriodFilter(period)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
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
          <div>
            <h4 className="font-medium text-[#191f28] mb-3">인플루언서</h4>
            <div className="flex gap-2 flex-wrap">
              {influencerOptions.map((option) => (
                <button
                  key={option.name}
                  onClick={() => setInfluencerFilter(option.name)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    influencerFilter === option.name
                      ? 'bg-[#3182f6] text-white'
                      : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
                  }`}
                >
                  {option.name}
                  {option.count && `(${option.count})`}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 차트 영역 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <h4 className="font-medium text-[#191f28] mb-4">주가 차트 & 신호</h4>
        <div className="relative h-72 bg-[#f8f9fa] rounded-lg overflow-hidden">
          <svg className="w-full h-full" viewBox="0 0 460 240">
            <defs>
              <linearGradient id="priceGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#3182f6" stopOpacity="0.15"/>
                <stop offset="100%" stopColor="#3182f6" stopOpacity="0.02"/>
              </linearGradient>
            </defs>
            
            {/* Y축 가격 라벨 */}
            {code === '005930' ? (
              <>
                <text x="48" y="35" textAnchor="end" className="text-[10px]" fill="#8b95a1">200,000</text>
                <line x1="52" y1="32" x2="420" y2="32" stroke="#e8e8e8" strokeWidth="0.5" strokeDasharray="3,3"/>
                <text x="48" y="75" textAnchor="end" className="text-[10px]" fill="#8b95a1">180,000</text>
                <line x1="52" y1="72" x2="420" y2="72" stroke="#e8e8e8" strokeWidth="0.5" strokeDasharray="3,3"/>
                <text x="48" y="115" textAnchor="end" className="text-[10px]" fill="#8b95a1">160,000</text>
                <line x1="52" y1="112" x2="420" y2="112" stroke="#e8e8e8" strokeWidth="0.5" strokeDasharray="3,3"/>
                <text x="48" y="155" textAnchor="end" className="text-[10px]" fill="#8b95a1">140,000</text>
                <line x1="52" y1="152" x2="420" y2="152" stroke="#e8e8e8" strokeWidth="0.5" strokeDasharray="3,3"/>
                <text x="48" y="195" textAnchor="end" className="text-[10px]" fill="#8b95a1">120,000</text>
                <line x1="52" y1="192" x2="420" y2="192" stroke="#e8e8e8" strokeWidth="0.5" strokeDasharray="3,3"/>
                
                {/* 주가 라인 (삼성전자 1월~2월: 120,000→197,000) */}
                <path d="M 60 192 L 100 180 L 140 175 L 180 160 L 220 150 L 260 148 L 300 110 L 340 72 L 380 55 L 420 40" fill="none" stroke="#3182f6" strokeWidth="2.5"/>
                <path d="M 60 192 L 100 180 L 140 175 L 180 160 L 220 150 L 260 148 L 300 110 L 340 72 L 380 55 L 420 40 L 420 210 L 60 210 Z" fill="url(#priceGrad)"/>
                
                {/* 시그널 점: 부읽남TV 조진표 매수 (2/23, ~197,000원) */}
                <circle cx="380" cy="55" r="7" fill="#3182f6" stroke="white" strokeWidth="2"/>
                <text x="380" y="48" textAnchor="middle" className="text-[9px]" fill="#3182f6" fontWeight="bold">매수</text>
              </>
            ) : code === '000660' ? (
              <>
                <text x="48" y="35" textAnchor="end" className="text-[10px]" fill="#8b95a1">950,000</text>
                <line x1="52" y1="32" x2="420" y2="32" stroke="#e8e8e8" strokeWidth="0.5" strokeDasharray="3,3"/>
                <text x="48" y="115" textAnchor="end" className="text-[10px]" fill="#8b95a1">700,000</text>
                <line x1="52" y1="112" x2="420" y2="112" stroke="#e8e8e8" strokeWidth="0.5" strokeDasharray="3,3"/>
                <text x="48" y="195" textAnchor="end" className="text-[10px]" fill="#8b95a1">450,000</text>
                <line x1="52" y1="192" x2="420" y2="192" stroke="#e8e8e8" strokeWidth="0.5" strokeDasharray="3,3"/>
                
                <path d="M 60 170 L 100 155 L 140 140 L 180 120 L 220 100 L 260 90 L 300 70 L 340 55 L 380 50 L 420 45" fill="none" stroke="#3182f6" strokeWidth="2.5"/>
                <path d="M 60 170 L 100 155 L 140 140 L 180 120 L 220 100 L 260 90 L 300 70 L 340 55 L 380 50 L 420 45 L 420 210 L 60 210 Z" fill="url(#priceGrad)"/>
                
                <circle cx="380" cy="50" r="7" fill="#3182f6" stroke="white" strokeWidth="2"/>
                <text x="380" y="43" textAnchor="middle" className="text-[9px]" fill="#3182f6" fontWeight="bold">매수</text>
              </>
            ) : (
              <>
                <text x="48" y="55" textAnchor="end" className="text-[10px]" fill="#8b95a1">고가</text>
                <text x="48" y="175" textAnchor="end" className="text-[10px]" fill="#8b95a1">저가</text>
                <path d="M 60 150 L 100 130 L 140 120 L 180 140 L 220 100 L 260 90 L 300 105 L 340 80 L 380 90 L 420 70" fill="none" stroke="#3182f6" strokeWidth="2.5"/>
                <path d="M 60 150 L 100 130 L 140 120 L 180 140 L 220 100 L 260 90 L 300 105 L 340 80 L 380 90 L 420 70 L 420 210 L 60 210 Z" fill="url(#priceGrad)"/>
              </>
            )}
            
            {/* X축 날짜 라벨 */}
            <text x="60" y="225" textAnchor="middle" className="text-[10px]" fill="#8b95a1">1/6</text>
            <text x="140" y="225" textAnchor="middle" className="text-[10px]" fill="#8b95a1">1/13</text>
            <text x="220" y="225" textAnchor="middle" className="text-[10px]" fill="#8b95a1">1/20</text>
            <text x="300" y="225" textAnchor="middle" className="text-[10px]" fill="#8b95a1">2/3</text>
            <text x="380" y="225" textAnchor="middle" className="text-[10px]" fill="#8b95a1">2/23</text>
            <text x="420" y="225" textAnchor="middle" className="text-[10px]" fill="#8b95a1">2/28</text>
          </svg>
          
          {/* 범례 */}
          <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm rounded-lg p-3 text-xs">
            <div className="flex items-center gap-2 mb-1">
              <span>🔵 매수</span>
              <span>🟢 긍정</span>
            </div>
            <div className="flex items-center gap-2">
              <span>🟡 중립</span>
              <span>🟠 경계</span>
              <span>🔴 매도</span>
            </div>
          </div>
        </div>
      </div>

      {/* 신호 테이블 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
        <div className="p-6 border-b border-[#e8e8e8]">
          <h4 className="font-medium text-[#191f28]">인플루언서 신호 이력</h4>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#f8f9fa]">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">날짜</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">인플루언서</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">신호</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">핵심발언</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">수익률</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">영상링크</th>
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
                  <td className="px-4 py-4 text-sm font-medium">
                    <span className={signal.return.startsWith('+') ? 'text-red-600' : 'text-blue-600'}>
                      {signal.return}
                    </span>
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
      </div>
    </div>
  );
}