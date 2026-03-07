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
    if (!user) { router.push('/login'); return; }
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

  const userStockNames = stocks.map(s => s.stock_name);
  const userWatchlistNames = watchlist.map(w => w.stock_name);
  const userStocks = new Set([...userStockNames, ...userWatchlistNames]);

  const filteredVideos = videos.filter(video => {
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
          <p style={{ fontSize: 13, color: C.gray, marginTop: 4, marginBottom: 0 }}>{user?.email} 님의 포트폴리오</p>
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
              {stocks.length > 0 ? (
                <div>
                  {stocks.slice(0, 4).map((stock, idx) => {
                    const returnPct = (stock as any).return_pct ?? 0;
                    const returnAmt = (stock as any).return_amount ?? 0;
                    const currentPrice = (stock as any).current_price ?? stock.avg_buy_price;
                    const isPositive = returnPct >= 0;
                    return (
                      <div key={stock.id} style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '12px 0',
                        borderBottom: idx < Math.min(stocks.length, 4) - 1 ? `1px solid ${C.lightGray}` : 'none',
                      }}>
                        {/* 왼쪽: 종목명 + 코드 + 수량·단가 */}
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                            <span style={{ fontWeight: 700, fontSize: 15, color: C.primary }}>{stock.stock_name}</span>
                            <span style={{ fontSize: 12, color: C.gray }}>{stock.stock_code}</span>
                          </div>
                          <div style={{ fontSize: 12, color: C.gray }}>
                            {stock.quantity}주 · 평균 {stock.avg_buy_price.toLocaleString('ko-KR')}원
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
              ) : (
                <div style={{ textAlign: 'center', padding: '24px 0', color: C.gray }}>
                  <p style={{ marginBottom: 8, fontSize: 14 }}>보유 종목이 없습니다</p>
                  <Link href="/my-portfolio" style={{ fontSize: 13, color: C.accent, textDecoration: 'none' }}>종목 추가하기 →</Link>
                </div>
              )}
            </div>

            {/* ② 관심종목 */}
            <div style={cardStyle}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <span style={{ fontSize: 13, fontWeight: 600, color: C.gray }}>관심종목</span>
                <Link href="/my-watchlist" style={{ fontSize: 12, color: C.accent, textDecoration: 'none' }}>전체보기 →</Link>
              </div>
              {watchlist.length > 0 ? (
                <div style={{ display: 'flex', gap: 10, overflowX: 'auto', paddingBottom: 4 }}>
                  {watchlist.slice(0, 8).map((item) => {
                    const changePct = (item as any).change_pct ?? 0;
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
                        <div style={{ fontSize: 12, color: C.gray, marginBottom: 4 }}>{(item as any).stock_code || ''}</div>
                        <div style={{ fontWeight: 700, fontSize: 14, color: isPos ? C.red : C.blue }}>
                          {changePct !== 0 ? (isPos ? '+' : '') + changePct.toFixed(2) + '%' : '-'}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '16px 0', color: C.gray, fontSize: 14 }}>
                  <p style={{ marginBottom: 8 }}>관심종목이 없습니다</p>
                  <Link href="/my-watchlist" style={{ fontSize: 13, color: C.accent, textDecoration: 'none' }}>관심종목 추가 →</Link>
                </div>
              )}
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
              {notifications.length > 0 ? (
                <div>
                  {notifications.map((notif, idx) => {
                    const notifIcon = (notif as any).icon || '🔔';
                    return (
                      <div key={notif.id} style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: 12,
                        padding: '12px 0',
                        borderBottom: idx < notifications.length - 1 ? `1px solid ${C.lightGray}` : 'none',
                        background: !notif.is_read ? '#F0F7FF' : 'transparent',
                        margin: !notif.is_read ? '0 -8px' : 0,
                        padding: !notif.is_read ? '12px 8px' : '12px 0',
                        borderRadius: !notif.is_read ? 8 : 0,
                      }}>
                        <span style={{ fontSize: 20, flexShrink: 0, lineHeight: 1 }}>{notifIcon}</span>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontWeight: 700, fontSize: 14, color: C.primary, marginBottom: 3 }}>{notif.title}</div>
                          <div style={{ fontSize: 13, color: C.gray, lineHeight: 1.4 }}>{notif.message}</div>
                          <div style={{ fontSize: 12, color: '#9CA3AF', marginTop: 4 }}>
                            {new Date(notif.created_at).toLocaleString('ko-KR')}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p style={{ textAlign: 'center', padding: '16px 0', color: C.gray, fontSize: 14 }}>알림이 없습니다</p>
              )}
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
              {/* Placeholder — 실제 공시 데이터 연동 시 아래 구조로 렌더링 */}
              <div style={{ textAlign: 'center', padding: '24px 0', color: C.gray }}>
                <div style={{ fontSize: 32, marginBottom: 10 }}>📋</div>
                <p style={{ fontSize: 14, marginBottom: 8 }}>공시 데이터 로딩 중...</p>
                <Link href="/explore" style={{ fontSize: 13, color: C.accent, textDecoration: 'none' }}>공시 탭에서 보기 →</Link>
              </div>
              {/* 공시 카드 예시 구조 (데이터 있을 때 사용)
              {disclosures.map(d => {
                const isPos = d.sentiment === '긍정';
                const isNeg = d.sentiment === '부정';
                const borderColor = isPos ? C.green : isNeg ? C.red : C.gray;
                return (
                  <div key={d.id} style={{
                    background: '#F8F9FA', borderRadius: 12, padding: 16, marginBottom: 12,
                    borderLeft: `4px solid ${borderColor}`,
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
                      <span style={{ fontWeight: 700, fontSize: 15, color: C.primary }}>{d.company}</span>
                      {d.type && (
                        <span style={{ background: isPos ? '#D1FAE5' : isNeg ? '#FEE2E2' : '#F3F4F6',
                          color: isPos ? '#065F46' : isNeg ? '#991B1B' : C.gray,
                          padding: '2px 8px', borderRadius: 6, fontSize: 11, fontWeight: 600 }}>
                          {d.type}
                        </span>
                      )}
                      {d.grade && (
                        <span style={{ background: '#EEF2FF', color: '#4338CA', padding: '2px 8px', borderRadius: 6, fontSize: 11, fontWeight: 600 }}>
                          {d.grade}
                        </span>
                      )}
                      <span style={{ fontSize: 12, color: C.gray, marginLeft: 'auto' }}>{formatTime(d.created_at)}</span>
                    </div>
                    <p style={{ fontWeight: 600, fontSize: 14, color: C.primary, marginBottom: 6 }}>{d.title}</p>
                    <p style={{ fontSize: 13, color: C.gray, lineHeight: 1.5, marginBottom: 8 }}>{d.summary}</p>
                    {(d.what || d.so_what || d.now_what) && (
                      <div style={{ fontSize: 12, color: '#4B5563', lineHeight: 1.6 }}>
                        {d.what && <div>💡 <strong>What</strong> {d.what}</div>}
                        {d.so_what && <div>🔍 <strong>So What</strong> {d.so_what}</div>}
                        {d.now_what && <div>📌 <strong>Now What</strong> {d.now_what}</div>}
                      </div>
                    )}
                  </div>
                );
              })} */}
            </div>

            {/* 뉴스 헤드라인 */}
            <div style={cardStyle}>
              <div style={{ fontSize: 13, fontWeight: 600, color: C.gray, marginBottom: 16 }}>뉴스 헤드라인</div>
              <div style={{ textAlign: 'center', padding: '24px 0', color: C.gray }}>
                <div style={{ fontSize: 32, marginBottom: 10 }}>📰</div>
                <p style={{ fontSize: 14 }}>뉴스 API 연동 예정</p>
              </div>
              {/* 뉴스 카드 예시 구조 (데이터 있을 때 사용)
              {news.map((n, idx) => (
                <div key={n.id} style={{
                  padding: '12px 0',
                  borderBottom: idx < news.length - 1 ? `1px solid ${C.lightGray}` : 'none',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                    <span style={{ background: '#F3F4F6', color: C.gray, fontSize: 11, padding: '2px 8px', borderRadius: 6, fontWeight: 600 }}>
                      {n.tag}
                    </span>
                  </div>
                  <p style={{ fontSize: 14, fontWeight: 500, color: C.primary, lineHeight: 1.4, marginBottom: 6 }}>{n.title}</p>
                  <p style={{ fontSize: 12, color: C.gray }}>{n.source} · {formatTime(n.published_at)}</p>
                </div>
              ))} */}
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
