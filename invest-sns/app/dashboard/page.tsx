'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// ── Mock Data ──────────────────────────────────────────────────────────────

const NOTIFICATIONS = [
  {
    id: '1',
    icon: '📢',
    type: 'disclosure',
    title: 'SK하이닉스 공시',
    body: '2024년 4분기 실적 발표 — 영업이익 7.7조 원',
    time: '06:50',
    read: false,
    ticker: '000660',
    tab: 'disclosure',
  },
  {
    id: '2',
    icon: '🤖',
    type: 'signal',
    title: '삼성전자 AI 시그널',
    body: '매수 시그널 3개 집중 — 반도체 업황 개선 기대감',
    time: '07:15',
    read: false,
    ticker: '005930',
    tab: '',
  },
  {
    id: '3',
    icon: '📈',
    type: 'price',
    title: 'NVIDIA 가격 알림',
    body: '$820 돌파 — 목표가 1차 달성',
    time: '06:30',
    read: true,
    ticker: 'NVDA',
    tab: '',
  },
  {
    id: '4',
    icon: '🎙️',
    type: 'signal',
    title: '카카오 신규 시그널',
    body: '긍정 시그널 — "카카오페이 흑자 전환 기대"',
    time: '어제',
    read: true,
    ticker: '035720',
    tab: '',
  },
];

const HOLDINGS = [
  { name: '삼성전자', ticker: '005930', qty: 30, avgPrice: 68500, currentPrice: 74600, profitPct: '+8.91%', up: true, aiOpinion: '보유 유지', aiColor: 'text-blue-500' },
  { name: 'SK하이닉스', ticker: '000660', qty: 10, avgPrice: 175000, currentPrice: 192500, profitPct: '+10.00%', up: true, aiOpinion: '추가 매수', aiColor: 'text-green-600' },
  { name: 'NVIDIA', ticker: 'NVDA', qty: 5, avgPrice: 700.00, currentPrice: 824.03, profitPct: '+17.72%', up: true, aiOpinion: '목표가 상향 검토', aiColor: 'text-blue-500' },
  { name: '카카오', ticker: '035720', qty: 20, avgPrice: 52000, currentPrice: 41300, profitPct: '-20.58%', up: false, aiOpinion: '손절 검토', aiColor: 'text-red-500' },
];

const WATCHLIST = [
  { name: 'TSMC', ticker: 'TSM', currentPrice: 147.80, change: '-1.60%', up: false, aiOpinion: '매수 대기', aiColor: 'text-yellow-600' },
  { name: '현대차', ticker: '005380', currentPrice: 231000, change: '+0.87%', up: true, aiOpinion: '관심 유지', aiColor: 'text-blue-500' },
  { name: 'Tesla', ticker: 'TSLA', currentPrice: 178.65, change: '-2.14%', up: false, aiOpinion: '추가 하락 경계', aiColor: 'text-orange-500' },
  { name: 'LG에너지솔루션', ticker: '373220', currentPrice: 388000, change: '+2.38%', up: true, aiOpinion: '분할 매수 검토', aiColor: 'text-green-600' },
  { name: 'Meta', ticker: 'META', currentPrice: 515.20, change: '+1.77%', up: true, aiOpinion: '보유 추천', aiColor: 'text-blue-500' },
];

const MARKET = {
  us: [
    { name: 'S&P 500', value: '5,204.34', change: '+0.82%', up: true },
    { name: '나스닥', value: '16,265.64', change: '+1.14%', up: true },
    { name: '다우', value: '38,996.39', change: '+0.34%', up: true },
  ],
  kr: [
    { name: '코스피', value: '2,715.82', change: '+0.42%', up: true },
    { name: '코스닥', value: '867.43', change: '+0.68%', up: true },
  ],
  others: [
    { name: '금', value: '$2,185', change: '+0.30%', up: true },
    { name: '은', value: '$24.50', change: '-0.20%', up: false },
    { name: '비트코인', value: '$67,800', change: '+2.10%', up: true },
  ],
  fearGreed: { value: 72, label: '탐욕', color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200' },
  issues: [
    '연준 파월 의장 "금리 인하 서두르지 않겠다" 발언 → 시장 소화',
    'NVIDIA 실적 호조로 반도체·AI 섹터 강세 지속',
    '달러 인덱스 약세 전환 → 원화 강세 가능성',
  ],
};

const AI_INSIGHTS = [
  {
    icon: '🧠',
    title: '포트폴리오 집중도 경고',
    body: '반도체 비중이 전체의 62%입니다. 섹터 분산을 검토하세요. 에너지·헬스케어 섹터 편입을 고려해볼 시점입니다.',
    tag: '리스크',
    tagColor: 'bg-orange-50 text-orange-600 border-orange-200',
  },
  {
    icon: '💡',
    title: '수익 실현 타이밍 분석',
    body: 'NVIDIA +17.7% · SK하이닉스 +10% 수익 중. 고점 부근 저항선 접근 중으로 일부 차익 실현 고려 권장.',
    tag: '기회',
    tagColor: 'bg-blue-50 text-blue-600 border-blue-200',
  },
  {
    icon: '⚠️',
    title: '카카오 손실 관리',
    body: '카카오 -20.6% 손실 중. 추가 하락 가능성 높음. 원칙 손절선 -25% 도달 전 대응 플랜 수립 권장.',
    tag: '경고',
    tagColor: 'bg-red-50 text-red-600 border-red-200',
  },
];

// ──────────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const router = useRouter();
  const [portfolioTab, setPortfolioTab] = useState<'holdings' | 'watchlist'>('holdings');
  const [notifications, setNotifications] = useState(NOTIFICATIONS);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleNotificationClick = (n: typeof NOTIFICATIONS[0]) => {
    // 읽음 처리
    setNotifications((prev) =>
      prev.map((item) => (item.id === n.id ? { ...item, read: true } : item))
    );
    // 해당 종목 페이지로 이동
    const url = n.tab ? `/stock/${n.ticker}?tab=${n.tab}` : `/stock/${n.ticker}`;
    router.push(url);
  };

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-6 py-5">
        <h1 className="text-xl font-bold text-[#191f28]">📊 대시보드</h1>
        <p className="text-sm text-[#8b95a1] mt-1">내 종목 현황</p>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-5 space-y-5">

        {/* ① 오늘 알림 */}
        <section className="bg-white border border-[#e8e8e8] rounded-2xl overflow-hidden shadow-sm">
          <div className="flex items-center justify-between px-5 py-4 border-b border-[#f0f0f0]">
            <h2 className="text-sm font-bold text-[#191f28]">
              🔔 오늘 알림
              {unreadCount > 0 && (
                <span className="ml-2 text-[10px] font-bold text-white bg-[#f04452] rounded-full px-1.5 py-0.5">
                  {unreadCount}
                </span>
              )}
            </h2>
            <button className="text-xs text-[#3182f6]">전체 보기</button>
          </div>
          <div>
            {notifications.map((n) => (
              <button
                key={n.id}
                onClick={() => handleNotificationClick(n)}
                className={`w-full text-left px-5 py-3.5 border-b border-[#f0f0f0] last:border-0 hover:bg-gray-50 active:bg-gray-100 transition-colors ${
                  !n.read ? 'bg-[#f0faf5]' : 'bg-white'
                }`}
              >
                <div className="flex items-start gap-3">
                  {!n.read && (
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                  )}
                  {n.read && <div className="w-1.5 flex-shrink-0" />}
                  <div className="text-base flex-shrink-0">{n.icon}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-[#191f28]">{n.title}</span>
                      <span className="text-xs text-[#b0b8c1] ml-2 flex-shrink-0">{n.time}</span>
                    </div>
                    <p className="text-xs text-[#4e5968] mt-0.5">{n.body}</p>
                  </div>
                  <span className="text-[#b0b8c1] text-xs flex-shrink-0">›</span>
                </div>
              </button>
            ))}
          </div>
        </section>

        {/* ② 보유종목 / 관심종목 */}
        <section className="bg-white border border-[#e8e8e8] rounded-2xl overflow-hidden shadow-sm">
          <div className="flex items-center border-b border-[#e8e8e8]">
            <button
              onClick={() => setPortfolioTab('holdings')}
              className={`flex-1 py-3.5 text-sm font-medium transition-colors ${
                portfolioTab === 'holdings'
                  ? 'text-[#3182f6] border-b-2 border-[#3182f6] bg-white'
                  : 'text-[#8b95a1] bg-[#f9f9f9]'
              }`}
            >
              💼 보유종목 {HOLDINGS.length}
            </button>
            <button
              onClick={() => setPortfolioTab('watchlist')}
              className={`flex-1 py-3.5 text-sm font-medium transition-colors ${
                portfolioTab === 'watchlist'
                  ? 'text-[#3182f6] border-b-2 border-[#3182f6] bg-white'
                  : 'text-[#8b95a1] bg-[#f9f9f9]'
              }`}
            >
              ⭐ 관심종목 {WATCHLIST.length}
            </button>
            <Link href="/portfolio" className="text-xs text-[#3182f6] px-3 whitespace-nowrap">
              관리 →
            </Link>
          </div>

          {portfolioTab === 'holdings' && (
            <div className="divide-y divide-[#f0f0f0]">
              {HOLDINGS.map((stock) => (
                <Link
                  key={stock.ticker}
                  href={`/stock/${stock.ticker}`}
                  className="flex items-center justify-between px-5 py-4 hover:bg-gray-50 active:bg-gray-100 transition-colors"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-[#191f28]">{stock.name}</span>
                      <span className="text-xs text-[#b0b8c1]">{stock.ticker}</span>
                    </div>
                    <div className="text-xs text-[#8b95a1] mt-0.5">
                      {stock.qty}주 · 평균 {stock.avgPrice.toLocaleString()}원
                    </div>
                    <div className={`text-xs font-medium mt-1 ${stock.aiColor}`}>
                      🤖 {stock.aiOpinion}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-[#191f28]">
                      {stock.currentPrice.toLocaleString()}
                    </div>
                    <div className={`text-xs font-bold mt-0.5 ${stock.up ? 'text-green-600' : 'text-red-500'}`}>
                      {stock.profitPct}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}

          {portfolioTab === 'watchlist' && (
            <div className="divide-y divide-[#f0f0f0]">
              {WATCHLIST.map((stock) => (
                <Link
                  key={stock.ticker}
                  href={`/stock/${stock.ticker}`}
                  className="flex items-center justify-between px-5 py-4 hover:bg-gray-50 active:bg-gray-100 transition-colors"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-[#191f28]">{stock.name}</span>
                      <span className="text-xs text-[#b0b8c1]">{stock.ticker}</span>
                    </div>
                    <div className={`text-xs font-medium mt-1 ${stock.aiColor}`}>
                      🤖 {stock.aiOpinion}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-[#191f28]">
                      {typeof stock.currentPrice === 'number'
                        ? stock.currentPrice.toLocaleString()
                        : stock.currentPrice}
                    </div>
                    <div className={`text-xs font-medium mt-0.5 ${stock.up ? 'text-green-600' : 'text-red-500'}`}>
                      {stock.change}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>

        {/* ③ 시황 */}
        <section className="bg-white border border-[#e8e8e8] rounded-2xl p-5 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-[#191f28]">🌐 시황</h2>

          {/* 미국장 */}
          <div>
            <p className="text-xs font-medium text-[#8b95a1] mb-2">🇺🇸 미국장</p>
            <div className="grid grid-cols-3 gap-2">
              {MARKET.us.map((m) => (
                <div key={m.name} className="bg-[#f9f9f9] border border-[#e8e8e8] rounded-xl p-3 text-center">
                  <div className="text-xs text-[#8b95a1] mb-1">{m.name}</div>
                  <div className="text-sm font-bold text-[#191f28]">{m.value}</div>
                  <div className={`text-xs font-medium mt-0.5 ${m.up ? 'text-green-600' : 'text-red-500'}`}>
                    {m.change}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 코스피/코스닥 */}
          <div>
            <p className="text-xs font-medium text-[#8b95a1] mb-2">🇰🇷 국내장</p>
            <div className="grid grid-cols-2 gap-2">
              {MARKET.kr.map((m) => (
                <div key={m.name} className="bg-[#f9f9f9] border border-[#e8e8e8] rounded-xl p-3 text-center">
                  <div className="text-xs text-[#8b95a1] mb-1">{m.name}</div>
                  <div className="text-sm font-bold text-[#191f28]">{m.value}</div>
                  <div className={`text-xs font-medium mt-0.5 ${m.up ? 'text-green-600' : 'text-red-500'}`}>
                    {m.change}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 금/은/비트코인 */}
          <div>
            <p className="text-xs font-medium text-[#8b95a1] mb-2">🪙 원자재 · 코인</p>
            <div className="grid grid-cols-3 gap-2">
              {MARKET.others.map((m) => (
                <div key={m.name} className="bg-[#f9f9f9] border border-[#e8e8e8] rounded-xl p-3 text-center">
                  <div className="text-xs text-[#8b95a1] mb-1">{m.name}</div>
                  <div className="text-sm font-bold text-[#191f28]">{m.value}</div>
                  <div className={`text-xs font-medium mt-0.5 ${m.up ? 'text-green-600' : 'text-red-500'}`}>
                    {m.change}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Fear & Greed */}
          <div className={`flex items-center justify-between rounded-xl px-4 py-3 border ${MARKET.fearGreed.border} ${MARKET.fearGreed.bg}`}>
            <div className="flex items-center gap-3">
              <span className="text-2xl">😨</span>
              <div>
                <div className="text-xs text-[#8b95a1]">Fear & Greed Index</div>
                <div className="text-lg font-black text-[#191f28]">{MARKET.fearGreed.value}</div>
              </div>
            </div>
            <div className={`text-sm font-bold ${MARKET.fearGreed.color}`}>
              {MARKET.fearGreed.label}
            </div>
          </div>

          {/* 핵심 이슈 */}
          <div>
            <p className="text-xs font-medium text-[#8b95a1] mb-2">📌 핵심 이슈</p>
            <div className="space-y-2">
              {MARKET.issues.map((issue, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-[10px] font-bold text-[#3182f6] bg-blue-50 border border-blue-100 rounded px-1.5 py-0.5 flex-shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  <p className="text-xs text-[#4e5968] leading-relaxed">{issue}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ④ 오늘의 인사이트 (AI) */}
        <section className="bg-white border border-[#e8e8e8] rounded-2xl p-5 shadow-sm">
          <h2 className="text-sm font-bold text-[#191f28] mb-4">🤖 오늘의 인사이트</h2>
          <div className="space-y-3">
            {AI_INSIGHTS.map((insight, i) => (
              <div key={i} className="bg-[#f9f9f9] border border-[#e8e8e8] rounded-xl p-4">
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="text-base">{insight.icon}</span>
                  <span className="text-sm font-bold text-[#191f28]">{insight.title}</span>
                  <span className={`ml-auto text-[10px] font-bold border rounded px-1.5 py-0.5 ${insight.tagColor}`}>
                    {insight.tag}
                  </span>
                </div>
                <p className="text-xs text-[#4e5968] leading-relaxed">{insight.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Footer */}
        <div className="text-center py-2 pb-8">
          <Link href="/" className="text-sm text-[#3182f6] hover:underline">
            ← 메인으로 돌아가기
          </Link>
        </div>
      </div>
    </div>
  );
}
