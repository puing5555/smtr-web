'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getUserStocks } from '@/lib/api/user-stocks';
import { getUserWatchlist } from '@/lib/api/user-watchlist';
import { getUnreadNotifications, getNotificationStats } from '@/lib/api/user-notifications';
import type { Database } from '@/types/supabase';

type UserStock = Database['public']['Tables']['user_stocks']['Row'];
type UserWatchlist = Database['public']['Tables']['user_watchlist']['Row'];
type UserNotification = Database['public']['Tables']['user_notifications']['Row'];

// Mock 시황 데이터 (추후 API 연동)
const MARKET_DATA = [
  { label: 'US', items: ['S&P 5,234 +0.3%', '나스닥 16,832 +0.5%', '다우 39,420 +0.1%'] },
  { label: 'KR', items: ['코스피 2,578 -0.2%', '코스닥 752 +0.4%'] },
  { label: '₿', items: ['BTC $85,420 +1.2%', '금 $2,914 +0.3%', '원달러 1,455 +0.1%'] },
];

type TabKey = '지금' | '뉴스' | 'LIVE' | '시장';

interface VideoCard {
  id: string;
  channel_name: string;
  title: string;
  upload_date: string;
  long_summary: string | null;
  youtube_url: string;
  mentioned_stocks: string[] | null;
  channel_id: string;
  category?: string;
}

// ─── 더미 데이터 (DB 없을 때 fallback) ────────────────────────
const dummyHoldings = [
  { name: "삼성전자", code: "005930", qty: 30, avgPrice: 68500, currentPrice: 74600, returnPct: 8.91 },
  { name: "SK하이닉스", code: "000660", qty: 10, avgPrice: 175000, currentPrice: 192500, returnPct: 10.0 },
  { name: "NVIDIA", code: "NVDA", qty: 5, avgPrice: 700, currentPrice: 824.03, returnPct: 17.72 },
  { name: "카카오", code: "035720", qty: 20, avgPrice: 52000, currentPrice: 41300, returnPct: -20.58 },
];

const dummyWatchlist = [
  { name: "하이트진로", code: "000080", currentPrice: 21500, changePct: 2.1 },
  { name: "CELH", code: "CELH", currentPrice: 32.45, changePct: 0.5 },
  { name: "테슬라", code: "TSLA", currentPrice: 267.89, changePct: -1.2 },
  { name: "한화에어로", code: "012450", currentPrice: 315000, changePct: 4.3 },
  { name: "SOFI", code: "SOFI", currentPrice: 12.34, changePct: 3.7 },
];

const dummyAlerts = [
  { time: "07:15", icon: "🤖", title: "삼성전자 AI 시그널", desc: "매수 시그널 3개 집중 — 반도체 업황 개선 기대감" },
  { time: "06:50", icon: "📢", title: "SK하이닉스 공시", desc: "2024년 4분기 실적 발표 — 영업이익 7.7조 원" },
  { time: "06:30", icon: "📈", title: "NVIDIA 목표가 상향", desc: "골드만삭스 목표가 $950 → $1,100 상향" },
  { time: "06:00", icon: "⚠️", title: "카카오 손절 검토", desc: "AI 판단: 손절 라인 도달, 포지션 재검토 필요" },
];

const dummyDisclosures = [
  { time: "08:30", company: "SK하이닉스", type: "실적", grade: "A+", title: "4분기 실적 발표", summary: "영업이익 7.7조원, 컨센서스 대비 +15% 서프라이즈. HBM 매출 비중 확대.", verdict: "긍정", what: "분기 영업이익 역대 최고치 경신", so_what: "HBM 수요 지속 + AI 인프라 투자 확대 수혜", now_what: "목표가 상향 가능성 높음, 보유 유지 권장" },
  { time: "07:45", company: "삼성전자", type: "자사주", grade: "A", title: "자사주 3조원 매입 결정", summary: "향후 6개월간 3조원 규모 자사주 매입. 주주환원 강화.", verdict: "긍정", what: "3조원 규모 자사주 매입 프로그램 발표", so_what: "주가 하방 지지 + 주주환원 시그널", now_what: "단기 주가 지지 효과 기대" },
  { time: "07:00", company: "에코프로비엠", type: "CB발행", grade: "C", title: "2000억 CB 발행 결정", summary: "전환가액 25만원, 희석률 약 4.2%. 시설투자 목적.", verdict: "부정", what: "2000억원 규모 전환사채 발행", so_what: "주식 전환 시 4.2% 지분 희석", now_what: "단기 매도 압력 가능성, 전환가 대비 현재가 모니터링" },
];

const dummyNews = [
  { time: "08:00", source: "한경", title: "미국 반도체 수출규제 완화 시그널... 엔비디아 시간외 +3%", tag: "반도체" },
  { time: "07:30", source: "매경", title: "연준 파월 \"인플레이션 둔화 확인\"... 6월 금리인하 기대↑", tag: "매크로" },
  { time: "07:00", source: "Bloomberg", title: "비트코인 $90K 돌파 임박, ETF 자금 유입 가속", tag: "크립토" },
  { time: "06:30", source: "로이터", title: "삼성전자-TSMC AI칩 수주 경쟁 격화", tag: "반도체" },
  { time: "06:00", source: "조선비즈", title: "2차전지 섹터 반등세... LG엔솔 외국인 3일 연속 순매수", tag: "2차전지" },
];

const dummyVideos: VideoCard[] = [
  { id: "d1", channel_name: "이효석아카데미", upload_date: "오늘 07:30", title: "반도체 사이클 2차 랠리 시작된다", category: "한국주식", long_summary: "필라델피아 반도체 지수가 3일 연속 상승하며 2차 랠리 신호를 보이고 있다. HBM 수요가 예상보다 강하고, SK하이닉스와 삼성전자의 실적 서프라이즈 가능성이 높다. 미국 AI 인프라 투자가 가속화되면서 메모리 수요는 하반기까지 이어질 전망.", mentioned_stocks: ["SK하이닉스", "삼성전자", "ASML"], youtube_url: "#", channel_id: "d1" },
  { id: "d2", channel_name: "월가아재", upload_date: "오늘 06:00", title: "미국 고용지표 쇼크, 연준 피벗 앞당겨질까", category: "미국주식", long_summary: "비농업 고용이 컨센서스 대비 크게 하회하며 경기 둔화 우려가 부각됐다. 연준의 6월 금리인하 가능성이 70%까지 상승. 기술주 중심으로 반등 가능성 높으나, 경기침체 시그널과 구분해야 한다.", mentioned_stocks: ["SPY", "QQQ", "TLT"], youtube_url: "#", channel_id: "d2" },
  { id: "d3", channel_name: "삼프로TV", upload_date: "오늘 08:00", title: "[마감시황] 외국인 반도체 폭풍매수, 코스피 2600 돌파", category: "한국주식", long_summary: "외국인이 삼성전자와 SK하이닉스를 중심으로 4거래일 연속 순매수. 코스피가 2600선을 돌파하며 3개월 만에 최고치를 기록. 기관은 차익실현 매도세를 보이고 있으나 외국인 수급이 압도적.", mentioned_stocks: ["삼성전자", "SK하이닉스"], youtube_url: "#", channel_id: "d3" },
  { id: "d4", channel_name: "코인데스크코리아", upload_date: "오늘 07:00", title: "비트코인 $85K 돌파, ETF 자금 유입 역대급", category: "크립토", long_summary: "비트코인 현물 ETF에 하루 $1.2B 유입되며 역대 최고 기록. 기관 투자자들의 본격적인 진입 신호로 해석. 이더리움도 $3,200 돌파하며 알트코인 랠리 기대감 상승.", mentioned_stocks: ["BTC", "ETH"], youtube_url: "#", channel_id: "d4" },
  { id: "d5", channel_name: "슈카월드", upload_date: "오늘 09:00", title: "미국이 금리를 안 내리는 진짜 이유", category: "미국주식", long_summary: "미국 경제가 여전히 강한 고용과 소비를 보이고 있어 연준이 금리 인하를 서두르지 않는 배경을 분석. 인플레이션의 구조적 변화와 재정적자 문제까지 함께 다루며 하반기 전망을 제시.", mentioned_stocks: [], youtube_url: "#", channel_id: "d5" },
  { id: "d6", channel_name: "소수몽키", upload_date: "오늘 06:30", title: "테슬라 이번에는 진짜 바닥일까? FSD 12.5 분석", category: "미국주식", long_summary: "테슬라 FSD 12.5 업데이트가 완전자율주행에 한 걸음 더 다가갔다는 평가. 중국 시장 매출 반등과 사이버트럭 생산 정상화도 긍정적. 다만 밸류에이션 논란은 여전.", mentioned_stocks: ["테슬라"], youtube_url: "#", channel_id: "d6" },
  { id: "d7", channel_name: "GODofIT", upload_date: "오늘 08:30", title: "엔비디아 실적 프리뷰: 이번에도 서프라이즈?", category: "미국주식", long_summary: "엔비디아 다음 주 실적 발표를 앞두고 주요 체크포인트 분석. 데이터센터 매출 YoY +200% 예상, H200/B100 전환 사이클, 중국 수출 규제 영향까지 종합 정리.", mentioned_stocks: ["NVIDIA", "AMD"], youtube_url: "#", channel_id: "d7" },
  { id: "d8", channel_name: "세상학개론", upload_date: "어제 22:00", title: "2024년에 반드시 사야 할 한국 배당주 TOP 5", category: "한국주식", long_summary: "고배당 + 성장성을 겸비한 한국 배당주 5개를 선정. 배당수익률 5% 이상이면서 실적 성장이 확인된 종목 위주로 분석. KT&G, 하나금융, SK텔레콤 등이 포함.", mentioned_stocks: ["KT&G", "하나금융", "SK텔레콤"], youtube_url: "#", channel_id: "d8" },
  { id: "d9", channel_name: "이효석아카데미", upload_date: "어제 20:00", title: "비트코인 10만불 간다? 반감기 후 시나리오", category: "크립토", long_summary: "비트코인 반감기 이후 역사적 패턴을 분석하며 $100K 시나리오를 제시. 기관 ETF 자금 유입, 스테이블코인 시가총액 증가, 온체인 데이터 모두 긍정적 신호를 보이고 있다.", mentioned_stocks: ["BTC"], youtube_url: "#", channel_id: "d9" },
  { id: "d10", channel_name: "리치고TV", upload_date: "어제 19:00", title: "초보자가 절대 사면 안되는 ETF 3가지", category: "미국주식", long_summary: "레버리지 ETF, 인버스 ETF, 테마형 ETF의 위험성을 구체적 사례와 함께 설명. 장기 보유 시 괴리율 문제와 비용 구조를 분석하며 초보자에게 적합한 대안 ETF도 제시.", mentioned_stocks: [], youtube_url: "#", channel_id: "d10" },
];

// ─── Design Tokens ───────────────────────────────────────────
const C = {
  bg: '#F8F9FA',
  card: '#FFFFFF',
  primary: '#1A1A2E',
  accent: '#2563EB',
  red: '#EF4444',
  blue: '#3B82F6',
  green: '#10B981',
  gray: '#6B7280',
  lightGray: '#E5E7EB',
};

const cardStyle: React.CSSProperties = {
  background: C.card,
  borderRadius: 16,
  padding: '20px 24px',
  marginBottom: 16,
  boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
};

// FilterPill
function FilterPill({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '8px 16px',
        borderRadius: 20,
        background: active ? C.accent : C.card,
        color: active ? '#fff' : C.gray,
        border: active ? 'none' : `1px solid ${C.lightGray}`,
        fontSize: 13,
        fontWeight: 600,
        cursor: 'pointer',
        flexShrink: 0,
        transition: 'all 0.15s',
        fontFamily: 'inherit',
      }}
    >
      {label}
    </button>
  );
}

// Category badge colors
function getCategoryStyle(category: string): React.CSSProperties {
  const map: Record<string, { bg: string; color: string }> = {
    'stock_analysis': { bg: '#DBEAFE', color: '#1E40AF' },
    '한국주식': { bg: '#DBEAFE', color: '#1E40AF' },
    'us_stock': { bg: '#FEE2E2', color: '#991B1B' },
    '미국주식': { bg: '#FEE2E2', color: '#991B1B' },
    'crypto': { bg: '#FEF3C7', color: '#92400E' },
    '크립토': { bg: '#FEF3C7', color: '#92400E' },
  };
  const s = map[category] || { bg: '#F3F4F6', color: '#374151' };
  return {
    background: s.bg,
    color: s.color,
    padding: '2px 8px',
    borderRadius: 6,
    fontSize: 11,
    fontWeight: 600,
  };
}

const CATEGORY_LABELS: Record<string, string> = {
  'stock_analysis': '종목분석',
  'market_overview': '시황',
  'education': '교육',
  'macro': '매크로',
  'general': '일반',
  'us_stock': '미국주식',
  'crypto': '크립토',
};

// ─── Main Component ────────────────────────────────────────────
export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabKey>('지금');
  const [stocks, setStocks] = useState<UserStock[]>([]);
  const [watchlist, setWatchlist] = useState<UserWatchlist[]>([]);
  const [notifications, setNotifications] = useState<UserNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [videos, setVideos] = useState<VideoCard[]>([]);
  const [videoFilter, setVideoFilter] = useState<string>('내 종목');
  const [channelFilter, setChannelFilter] = useState<string[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<string>('전체');
  const [videoPage, setVideoPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [expandedCards, setExpandedCards] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [newsFilter, setNewsFilter] = useState<'전체' | '공시' | '내종목'>('전체');

  useEffect(() => {
    if (authLoading) return;
    // if (!user) { router.push('/login'); return; } // 데모: 비로그인도 더미 대시보드 표시
    loadDashboard();
  }, [user, authLoading]);

  useEffect(() => {
    if (activeTab !== 'LIVE') return;
    const handleScroll = () => {
      if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 300) {
        loadMoreVideos();
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [activeTab, videoPage, hasMore, loadingMore]);

  const loadDashboard = async () => {
    setLoading(true);
    const timeoutId = setTimeout(() => setLoading(false), 8000);
    try {
      const [stocksRes, watchlistRes, notifRes, statsRes] = await Promise.all([
        getUserStocks(),
        getUserWatchlist(),
        getUnreadNotifications(),
        getNotificationStats(),
      ]);
      if (stocksRes.data) setStocks(stocksRes.data);
      if (watchlistRes.data) setWatchlist(watchlistRes.data);
      if (notifRes.data) setNotifications(notifRes.data.slice(0, 5));
      if (statsRes.data) setUnreadCount(statsRes.data.unread);
      await loadVideos();
    } catch (e) {
      console.error('Dashboard load error:', e);
    }
    clearTimeout(timeoutId);
    setLoading(false);
  };

  const loadVideos = async (page = 1, append = false) => {
    try {
      const limit = 20;
      const offset = (page - 1) * limit;
      const url = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/videos?select=*&order=upload_date.desc&limit=${limit}&offset=${offset}`;
      const res = await fetch(url, {
        headers: {
          apikey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
          Authorization: `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          if (append) {
            setVideos(prev => [...prev, ...data]);
          } else {
            setVideos(data);
          }
          setHasMore(data.length === limit);
        }
      }
    } catch (e) {
      // 테이블 없으면 무시
    }
  };

  const loadMoreVideos = async () => {
    if (loadingMore || !hasMore) return;
    setLoadingMore(true);
    const nextPage = videoPage + 1;
    await loadVideos(nextPage, true);
    setVideoPage(nextPage);
    setLoadingMore(false);
  };

  const toggleExpand = (id: string) => {
    setExpandedCards(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const formatKRW = (n: number) => n.toLocaleString('ko-KR') + '원';
  const formatPercent = (n: number) => (n >= 0 ? '+' : '') + n.toFixed(2) + '%';
  const formatTime = (iso: string) => {
    try {
      const d = new Date(iso);
      return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
    } catch { return iso; }
  };

  // ─── Fallback display 데이터 (DB 없으면 더미) ─────────────────
  const displayStocks = stocks.length > 0 ? stocks : dummyHoldings.map(d => ({
    id: d.code, stock_name: d.name, stock_code: d.code, ticker: d.code,
    quantity: d.qty, avg_buy_price: d.avgPrice, avg_price: d.avgPrice,
    current_price: d.currentPrice, return_pct: d.returnPct,
    user_id: '', created_at: '',
  } as any));

  const displayWatchlist = watchlist.length > 0 ? watchlist : dummyWatchlist.map(d => ({
    id: d.code, stock_name: d.name, stock_code: d.code, ticker: d.code,
    current_price: d.currentPrice, change_pct: d.changePct,
    alert_on_signals: false, user_id: '', created_at: '',
  } as any));

  const displayNotifications = notifications.length > 0 ? notifications : dummyAlerts.map((a, i) => ({
    id: String(i), title: a.title, message: a.desc, icon: a.icon,
    type: 'signal', is_read: false, created_at: a.time, user_id: '',
  } as any));

  const displayVideos = videos.length > 0 ? videos : dummyVideos;
  const displayDisclosures = dummyDisclosures; // 실제 DB 연동 전까지 더미 사용
  const displayNews = dummyNews; // 실제 DB 연동 전까지 더미 사용

  const userStockNames = displayStocks.map((s: any) => s.stock_name);
  const userWatchlistNames = displayWatchlist.map((w: any) => w.stock_name);
  const userStocks = new Set([...userStockNames, ...userWatchlistNames]);

  const filteredVideos = displayVideos.filter(video => {
    if (videoFilter === '내 종목') {
      if (!video.mentioned_stocks || video.mentioned_stocks.length === 0) return false;
      const hasMyStock = video.mentioned_stocks.some(s => userStocks.has(s));
      if (!hasMyStock) return false;
    }
    if (channelFilter.length > 0 && !channelFilter.includes(video.channel_name)) return false;
    if (categoryFilter !== '전체') {
      const catMap: Record<string, string> = {
        '한국주식': 'stock_analysis',
        '미국주식': 'us_stock',
        '크립토': 'crypto',
      };
      if ((video as any).category !== catMap[categoryFilter]) return false;
    }
    return true;
  });

  // ─── Loading ──────────────────────────────────────────────────
  if (authLoading || loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: C.bg }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>📊</div>
          <div style={{ color: C.gray, fontSize: 14 }}>대시보드 로딩 중...</div>
        </div>
      </div>
    );
  }

  const TABS: { key: TabKey; label: string }[] = [
    { key: '지금', label: '지금' },
    { key: '뉴스', label: '뉴스' },
    { key: 'LIVE', label: '🔴 LIVE' },
    { key: '시장', label: '시장' },
  ];

  // ─── Render ───────────────────────────────────────────────────
  return (
    <div style={{ minHeight: '100vh', background: C.bg, fontFamily: "'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif" }}>

      {/* ── Header ─────────────────────────────────────────── */}
      <div style={{ background: C.card, borderBottom: `1px solid ${C.lightGray}`, padding: '20px 24px' }}>
        <div style={{ maxWidth: 800, margin: '0 auto' }}>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: C.primary, margin: 0 }}>📊 대시보드</h1>
          <p style={{ fontSize: 13, color: C.gray, marginTop: 4, marginBottom: 0 }}>{user?.email ?? '게스트'} 님의 포트폴리오</p>
        </div>
      </div>

      {/* ── Tab Bar ───────────────────────────────────────── */}
      <div style={{ background: C.card, borderBottom: `2px solid ${C.lightGray}`, position: 'sticky', top: 0, zIndex: 10 }}>
        <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 16px', display: 'flex' }}>
          {TABS.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              style={{
                padding: '14px 20px',
                fontSize: 14,
                fontWeight: activeTab === tab.key ? 700 : 500,
                color: activeTab === tab.key ? C.accent : C.gray,
                background: 'none',
                border: 'none',
                borderBottom: activeTab === tab.key ? `3px solid ${C.accent}` : '3px solid transparent',
                cursor: 'pointer',
                transition: 'all 0.15s',
                fontFamily: 'inherit',
                marginBottom: -2,
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Content ───────────────────────────────────────── */}
      <div style={{ maxWidth: 800, margin: '0 auto', padding: '16px 16px 40px' }}>

        {/* ══════════════════════════════════════════════════
            탭 1: 지금
        ══════════════════════════════════════════════════ */}
        {activeTab === '지금' && (
          <>
            {/* ① 보유종목 */}
            <div style={cardStyle}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <span style={{ fontSize: 13, fontWeight: 600, color: C.gray }}>보유종목</span>
                <Link href="/my-portfolio" style={{ fontSize: 12, color: C.accent, textDecoration: 'none' }}>전체보기 →</Link>
              </div>
              <div>
                {displayStocks.slice(0, 4).map((stock: any, idx: number) => {
                  const returnPct = stock.return_pct ?? 0;
                  const currentPrice = stock.current_price ?? stock.avg_buy_price ?? stock.avg_price ?? 0;
                  const avgPrice = stock.avg_buy_price ?? stock.avg_price ?? 0;
                  const isPositive = returnPct >= 0;
                  return (
                    <div key={stock.id} style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '12px 0',
                      borderBottom: idx < Math.min(displayStocks.length, 4) - 1 ? `1px solid ${C.lightGray}` : 'none',
                    }}>
                      {/* 왼쪽: 종목명 + 코드 + 수량·단가 */}
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                          <span style={{ fontWeight: 700, fontSize: 15, color: C.primary }}>{stock.stock_name}</span>
                          <span style={{ fontSize: 12, color: C.gray }}>{stock.stock_code || stock.ticker || ''}</span>
                        </div>
                        <div style={{ fontSize: 12, color: C.gray }}>
                          {stock.quantity}주 · 평균 {avgPrice.toLocaleString('ko-KR')}원
                        </div>
                      </div>
                      {/* 오른쪽: 현재가 + 수익률 */}
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontWeight: 700, fontSize: 16, color: C.primary, marginBottom: 4 }}>
                          {currentPrice.toLocaleString('ko-KR')}원
                        </div>
                        <div style={{ fontWeight: 700, fontSize: 14, color: isPositive ? C.red : C.blue }}>
                          {formatPercent(returnPct)}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* ② 관심종목 */}
            <div style={cardStyle}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <span style={{ fontSize: 13, fontWeight: 600, color: C.gray }}>관심종목</span>
                <Link href="/my-watchlist" style={{ fontSize: 12, color: C.accent, textDecoration: 'none' }}>전체보기 →</Link>
              </div>
              <div style={{ display: 'flex', gap: 10, overflowX: 'auto', paddingBottom: 4 }}>
                {displayWatchlist.slice(0, 8).map((item: any) => {
                  const changePct = item.change_pct ?? 0;
                  const isPos = changePct >= 0;
                  return (
                    <div key={item.id} style={{
                      minWidth: 120,
                      borderRadius: 12,
                      background: '#F8F9FA',
                      padding: '10px 12px',
                      textAlign: 'center',
                      flexShrink: 0,
                      border: `1px solid ${C.lightGray}`,
                    }}>
                      <div style={{ fontWeight: 600, fontSize: 13, color: C.primary, marginBottom: 2 }}>
                        {item.stock_name}
                        {item.alert_on_signals && <span style={{ marginLeft: 4 }}>🔔</span>}
                      </div>
                      <div style={{ fontSize: 12, color: C.gray, marginBottom: 4 }}>{item.stock_code || item.ticker || ''}</div>
                      <div style={{ fontWeight: 700, fontSize: 14, color: isPos ? C.red : C.blue }}>
                        {changePct !== 0 ? (isPos ? '+' : '') + changePct.toFixed(2) + '%' : '-'}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* ③ 시황 */}
            <div style={cardStyle}>
              <div style={{ fontSize: 13, fontWeight: 600, color: C.gray, marginBottom: 14 }}>시황</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {MARKET_DATA.map((group) => (
                  <div key={group.label} style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                    <span style={{ fontWeight: 700, fontSize: 13, color: C.gray, width: 28, flexShrink: 0, paddingTop: 1 }}>
                      {group.label}
                    </span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 12px' }}>
                      {group.items.map((item) => {
                        const hasMinus = item.includes('-') && !item.includes('원달러');
                        const hasPlus = item.includes('+');
                        return (
                          <span key={item} style={{
                            fontSize: 13,
                            fontWeight: 700,
                            color: hasPlus ? C.red : hasMinus ? C.blue : C.primary,
                          }}>
                            {item}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
              <p style={{ fontSize: 11, color: '#9CA3AF', marginTop: 12, marginBottom: 0 }}>※ 시황 데이터 추후 API 연동 예정</p>
            </div>

            {/* ④ 오늘 알림 */}
            <div style={cardStyle}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <span style={{ fontSize: 13, fontWeight: 600, color: C.gray }}>
                  오늘 알림{' '}
                  {unreadCount > 0 && (
                    <span style={{
                      background: C.red,
                      color: '#fff',
                      fontSize: 11,
                      padding: '1px 6px',
                      borderRadius: 10,
                      marginLeft: 6,
                      fontWeight: 700,
                    }}>{unreadCount}</span>
                  )}
                </span>
                <Link href="/notifications" style={{ fontSize: 12, color: C.accent, textDecoration: 'none' }}>전체보기 →</Link>
              </div>
              <div>
                {displayNotifications.map((notif: any, idx: number) => {
                  const notifIcon = notif.icon || '🔔';
                  const isUnread = !notif.is_read;
                  let timeStr = notif.created_at;
                  try { timeStr = new Date(notif.created_at).toLocaleString('ko-KR'); } catch { }
                  return (
                    <div key={notif.id} style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 12,
                      padding: isUnread ? '12px 8px' : '12px 0',
                      borderBottom: idx < displayNotifications.length - 1 ? `1px solid ${C.lightGray}` : 'none',
                      background: isUnread ? '#F0F7FF' : 'transparent',
                      margin: isUnread ? '0 -8px' : 0,
                      borderRadius: isUnread ? 8 : 0,
                    }}>
                      <span style={{ fontSize: 20, flexShrink: 0, lineHeight: 1 }}>{notifIcon}</span>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 700, fontSize: 14, color: C.primary, marginBottom: 3 }}>{notif.title}</div>
                        <div style={{ fontSize: 13, color: C.gray, lineHeight: 1.4 }}>{notif.message}</div>
                        <div style={{ fontSize: 12, color: '#9CA3AF', marginTop: 4 }}>{timeStr}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}

        {/* ══════════════════════════════════════════════════
            탭 2: 뉴스
        ══════════════════════════════════════════════════ */}
        {activeTab === '뉴스' && (
          <>
            {/* 필터 */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
              {(['전체', '공시', '내종목'] as const).map(f => (
                <FilterPill key={f} label={f} active={newsFilter === f} onClick={() => setNewsFilter(f)} />
              ))}
            </div>

            {/* 공시 AI 분석 */}
            <div style={cardStyle}>
              <div style={{ fontSize: 13, fontWeight: 600, color: C.gray, marginBottom: 16 }}>공시 AI 분석</div>
              {displayDisclosures.map((d, idx) => {
                const isPos = d.verdict === '긍정';
                const isNeg = d.verdict === '부정';
                const borderColor = isPos ? C.green : isNeg ? C.red : C.gray;
                return (
                  <div key={idx} style={{
                    background: '#F8F9FA', borderRadius: 12, padding: 16, marginBottom: 12,
                    borderLeft: `4px solid ${borderColor}`,
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, flexWrap: 'wrap' as const }}>
                      <span style={{ fontWeight: 700, fontSize: 15, color: C.primary }}>{d.company}</span>
                      {d.type && (
                        <span style={{
                          background: isPos ? '#D1FAE5' : isNeg ? '#FEE2E2' : '#F3F4F6',
                          color: isPos ? '#065F46' : isNeg ? '#991B1B' : C.gray,
                          padding: '2px 8px', borderRadius: 6, fontSize: 11, fontWeight: 600,
                        }}>{d.type}</span>
                      )}
                      {d.grade && (
                        <span style={{ background: '#EEF2FF', color: '#4338CA', padding: '2px 8px', borderRadius: 6, fontSize: 11, fontWeight: 600 }}>
                          {d.grade}
                        </span>
                      )}
                      <span style={{ fontSize: 12, color: C.gray, marginLeft: 'auto' }}>{d.time}</span>
                    </div>
                    <p style={{ fontWeight: 600, fontSize: 14, color: C.primary, marginBottom: 6 }}>{d.title}</p>
                    <p style={{ fontSize: 13, color: C.gray, lineHeight: 1.5, marginBottom: 8 }}>{d.summary}</p>
                    <div style={{ fontSize: 12, color: '#4B5563', lineHeight: 1.6 }}>
                      {d.what && <div>💡 <strong>What</strong> {d.what}</div>}
                      {d.so_what && <div>🔍 <strong>So What</strong> {d.so_what}</div>}
                      {d.now_what && <div>📌 <strong>Now What</strong> {d.now_what}</div>}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* 뉴스 헤드라인 */}
            <div style={cardStyle}>
              <div style={{ fontSize: 13, fontWeight: 600, color: C.gray, marginBottom: 16 }}>뉴스 헤드라인</div>
              {displayNews.map((n, idx) => (
                <div key={idx} style={{
                  padding: '12px 0',
                  borderBottom: idx < displayNews.length - 1 ? `1px solid ${C.lightGray}` : 'none',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                    <span style={{ background: '#F3F4F6', color: C.gray, fontSize: 11, padding: '2px 8px', borderRadius: 6, fontWeight: 600 }}>
                      {n.tag}
                    </span>
                    <span style={{ fontSize: 12, color: '#9CA3AF', marginLeft: 'auto' }}>{n.time}</span>
                  </div>
                  <p style={{ fontSize: 14, fontWeight: 500, color: C.primary, lineHeight: 1.4, marginBottom: 4 }}>{n.title}</p>
                  <p style={{ fontSize: 12, color: C.gray }}>{n.source}</p>
                </div>
              ))}
            </div>
          </>
        )}

        {/* ══════════════════════════════════════════════════
            탭 3: LIVE
        ══════════════════════════════════════════════════ */}
        {activeTab === 'LIVE' && (
          <>
            {/* 필터 2줄 */}
            <div style={{ marginBottom: 16 }}>
              {/* 1줄: 내 종목 / 전체 */}
              <div style={{ display: 'flex', gap: 8, marginBottom: 8, overflowX: 'auto', paddingBottom: 2 }}>
                {['내 종목', '전체'].map(f => (
                  <FilterPill
                    key={f}
                    label={f === '내 종목' ? '⭐ 내 종목' : '전체'}
                    active={videoFilter === f}
                    onClick={() => {
                      setVideoFilter(f);
                      setCategoryFilter('전체');
                      setChannelFilter([]);
                    }}
                  />
                ))}
              </div>
              {/* 2줄: 카테고리 */}
              <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 2 }}>
                {['전체', '한국주식', '미국주식', '크립토'].map(f => (
                  <FilterPill
                    key={f}
                    label={f}
                    active={categoryFilter === f}
                    onClick={() => {
                      setCategoryFilter(f);
                      if (f !== '전체') setVideoFilter('전체');
                    }}
                  />
                ))}
              </div>
            </div>

            {/* 영상 카드 목록 */}
            {filteredVideos.length > 0 ? (
              <div>
                {filteredVideos.map(video => {
                  const isExpanded = expandedCards.has(video.id);
                  const summary = video.long_summary || '';
                  const SHORT_LIMIT = 120;
                  const needsToggle = summary.length > SHORT_LIMIT;
                  const category = (video as any).category || '';
                  const hasMyStock = video.mentioned_stocks?.some(s => userStocks.has(s));

                  return (
                    <div key={video.id} style={{
                      ...cardStyle,
                      border: hasMyStock ? `2px solid ${C.accent}` : `1px solid #F3F4F6`,
                      background: hasMyStock ? '#F8FAFF' : C.card,
                    }}>
                      {/* 채널 + 카테고리 + 시간 */}
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          {/* 아바타 */}
                          <div style={{
                            width: 36, height: 36, borderRadius: '50%', background: C.lightGray,
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontWeight: 700, fontSize: 15, color: C.primary, flexShrink: 0,
                          }}>
                            {video.channel_name[0]}
                          </div>
                          <div>
                            <div style={{ fontWeight: 700, fontSize: 14, color: C.primary }}>{video.channel_name}</div>
                            <div style={{ fontSize: 12, color: C.gray }}>{formatTime(video.upload_date)}</div>
                          </div>
                        </div>
                        {/* 카테고리 뱃지 */}
                        {category && (
                          <span style={getCategoryStyle(category)}>
                            {CATEGORY_LABELS[category] || category}
                          </span>
                        )}
                      </div>

                      {/* 제목 */}
                      <h3 style={{ fontWeight: 700, fontSize: 15, color: C.primary, lineHeight: 1.4, marginBottom: 8, margin: '0 0 8px 0' }}>
                        {video.title}
                      </h3>

                      {/* 요약 */}
                      {summary && (
                        <div style={{ marginBottom: 10 }}>
                          <p style={{
                            fontSize: 13,
                            color: '#4B5563',
                            lineHeight: 1.6,
                            margin: 0,
                            display: !isExpanded && needsToggle ? '-webkit-box' : 'block',
                            WebkitLineClamp: !isExpanded && needsToggle ? 2 : undefined,
                            WebkitBoxOrient: 'vertical' as const,
                            overflow: !isExpanded && needsToggle ? 'hidden' : 'visible',
                          }}>
                            {summary}
                          </p>
                          {needsToggle && (
                            <button
                              onClick={() => toggleExpand(video.id)}
                              style={{
                                fontSize: 12, color: C.accent, background: 'none', border: 'none',
                                cursor: 'pointer', padding: '4px 0', fontFamily: 'inherit', fontWeight: 600,
                              }}
                            >
                              {isExpanded ? '접기▲' : '더보기▼'}
                            </button>
                          )}
                        </div>
                      )}

                      {/* 종목 태그 */}
                      {video.mentioned_stocks && video.mentioned_stocks.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12, alignItems: 'center' }}>
                          <span style={{ fontSize: 12, color: C.gray }}>📌</span>
                          {video.mentioned_stocks.slice(0, 5).map(s => (
                            <span
                              key={s}
                              style={{
                                padding: '2px 8px',
                                borderRadius: 6,
                                fontSize: 12,
                                fontWeight: userStocks.has(s) ? 600 : 400,
                                background: userStocks.has(s) ? '#DBEAFE' : '#F3F4F6',
                                color: userStocks.has(s) ? '#1E40AF' : C.gray,
                              }}
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* 영상 보기 버튼 */}
                      <a
                        href={video.youtube_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 6,
                          background: C.red,
                          color: '#fff',
                          borderRadius: 8,
                          padding: '6px 14px',
                          fontSize: 12,
                          fontWeight: 600,
                          textDecoration: 'none',
                        }}
                      >
                        🎬 영상 보기
                      </a>
                    </div>
                  );
                })}

                {/* 무한 스크롤 */}
                {loadingMore && (
                  <div style={{ textAlign: 'center', padding: '16px 0', color: C.gray, fontSize: 14 }}>
                    <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite', marginRight: 6 }}>⟳</span>로딩 중...
                  </div>
                )}
                {!hasMore && filteredVideos.length > 0 && (
                  <p style={{ textAlign: 'center', padding: '16px 0', color: '#9CA3AF', fontSize: 12 }}>모든 영상을 불러왔습니다</p>
                )}
              </div>
            ) : (
              <div style={{ ...cardStyle, textAlign: 'center', padding: '48px 24px' }}>
                <div style={{ fontSize: 40, marginBottom: 12 }}>🎬</div>
                {videoFilter === '내 종목' && userStocks.size === 0 ? (
                  <>
                    <p style={{ color: C.gray, fontSize: 14, marginBottom: 4 }}>보유/관심 종목을 추가하면</p>
                    <p style={{ color: C.gray, fontSize: 14, marginBottom: 12 }}>관련 영상이 표시됩니다</p>
                    <Link href="/my-portfolio" style={{ fontSize: 13, color: C.accent, textDecoration: 'none' }}>종목 추가하기 →</Link>
                  </>
                ) : (
                  <>
                    <p style={{ color: C.gray, fontSize: 14, marginBottom: 4 }}>영상 데이터 준비 중</p>
                    <p style={{ color: '#9CA3AF', fontSize: 12 }}>추적 채널의 영상이 수집되면 여기에 표시됩니다</p>
                  </>
                )}
              </div>
            )}
          </>
        )}

        {/* ══════════════════════════════════════════════════
            탭 4: 시장
        ══════════════════════════════════════════════════ */}
        {activeTab === '시장' && (
          <div style={{ ...cardStyle, textAlign: 'center', padding: '48px 24px' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>📊</div>
            <p style={{ fontWeight: 700, fontSize: 18, color: C.primary, marginBottom: 10 }}>시장 탭 준비 중</p>
            <p style={{ fontSize: 14, color: C.gray, lineHeight: 1.7, margin: 0 }}>
              Fear &amp; Greed 게이지 · 섹터별 등락<br />
              외국인/기관 수급 · 유튜버 전체 컨센서스
            </p>
          </div>
        )}

      </div>
    </div>
  );
}
