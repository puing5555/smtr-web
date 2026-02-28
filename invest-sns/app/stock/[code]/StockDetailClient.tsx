'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface StockDetailClientProps {
  code: string;
}

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

// 종목별 더미 시그널 데이터
const getStockSignals = (code: string) => {
  const signalMap: { [key: string]: any[] } = {
    '005930': [
      {
        id: 1,
        date: '2024-12-15',
        influencer: '코린이아빠',
        signal: '매수',
        quote: '삼성전자 3분기 실적이 시장 기대치를 상회했습니다. HBM 수요 증가로 인한 성장 가능성이 높습니다.',
        return: '+8.5%',
        videoUrl: 'https://youtube.com/watch?v=sample1'
      },
      {
        id: 2,
        date: '2024-12-10',
        influencer: '삼프로TV',
        signal: '긍정',
        quote: '메모리 반도체 업황 개선이 기대됩니다.',
        return: '+12.3%',
        videoUrl: 'https://youtube.com/watch?v=sample2'
      }
    ],
    '000660': [
      {
        id: 1,
        date: '2024-12-14',
        influencer: '슈카월드',
        signal: '매수',
        quote: 'AI 반도체 수요가 계속 증가하고 있어요. SK하이닉스가 HBM 시장을 선도하고 있습니다.',
        return: '+15.2%',
        videoUrl: 'https://youtube.com/watch?v=sample3'
      }
    ],
    '005380': [
      {
        id: 1,
        date: '2024-12-12',
        influencer: '삼프로TV',
        signal: '긍정',
        quote: '전기차 판매량이 전년대비 50% 증가했습니다.',
        return: '+6.8%',
        videoUrl: 'https://youtube.com/watch?v=sample4'
      }
    ]
  };

  return signalMap[code] || [];
};

// 탭 정의
const tabs = [
  { id: 'feed', label: '피드', icon: '📱' },
  { id: 'influencer', label: '인플루언서', icon: '📈' },
  { id: 'analyst', label: '애널리스트', icon: '📊' },
  { id: 'disclosure', label: '공시', icon: '📋' },
];

export default function StockDetailClient({ code }: StockDetailClientProps) {
  const [activeTab, setActiveTab] = useState('feed');
  const [isWatched, setIsWatched] = useState(false);
  const router = useRouter();
  
  const stockData = getStockData(code);
  const signals = getStockSignals(code);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'feed':
        return (
          <div className="space-y-4">
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <h3 className="text-lg font-bold mb-4">📈 최근 동향</h3>
              {signals.length > 0 ? (
                <div className="space-y-3">
                  {signals.map(signal => (
                    <div key={signal.id} className="border-l-4 border-blue-500 pl-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-sm font-medium text-blue-600">{signal.influencer}</span>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">{signal.signal}</span>
                        <span className="text-xs text-gray-500">{signal.date}</span>
                      </div>
                      <p className="text-sm text-gray-700">{signal.quote}</p>
                      <div className="mt-2 text-xs text-green-600 font-medium">수익률: {signal.return}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">최근 시그널이 없습니다.</p>
              )}
            </div>
          </div>
        );
      
      case 'influencer':
        return (
          <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
            <h3 className="text-lg font-bold mb-4">📈 인플루언서 시그널</h3>
            {signals.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">날짜</th>
                      <th className="text-left py-2">인플루언서</th>
                      <th className="text-left py-2">시그널</th>
                      <th className="text-left py-2">핵심 발언</th>
                      <th className="text-left py-2">수익률</th>
                    </tr>
                  </thead>
                  <tbody>
                    {signals.map(signal => (
                      <tr key={signal.id} className="border-b hover:bg-gray-50">
                        <td className="py-3">{signal.date}</td>
                        <td className="py-3 font-medium">{signal.influencer}</td>
                        <td className="py-3">
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">{signal.signal}</span>
                        </td>
                        <td className="py-3 max-w-xs truncate">{signal.quote}</td>
                        <td className="py-3 font-medium text-green-600">{signal.return}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500">인플루언서 시그널이 없습니다.</p>
            )}
          </div>
        );
      
      case 'analyst':
        return (
          <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
            <h3 className="text-lg font-bold mb-4">📊 애널리스트 리포트</h3>
            <p className="text-gray-500">준비중입니다.</p>
          </div>
        );
      
      case 'disclosure':
        return (
          <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
            <h3 className="text-lg font-bold mb-4">📋 공시 정보</h3>
            <p className="text-gray-500">준비중입니다.</p>
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

          {/* 탭 메뉴 */}
          <div className="flex gap-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative pb-3 px-1 text-sm font-medium transition-colors ${
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