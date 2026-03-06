# 내 종목 대시보드 기술 스펙 v1.0

> **프로젝트**: invest-sns  
> **목표**: 개인화된 종목 관리 및 AI 분석 대시보드  
> **작성일**: 2026-03-06  
> **우선순위**: P0 (1순위 기능)

## 📋 목차
1. [현재 인프라 분석](#1-현재-인프라-분석)
2. [Supabase Auth 설계](#2-supabase-auth-설계)
3. [DB 스키마 설계](#3-db-스키마-설계)
4. [API 설계](#4-api-설계)
5. [프론트엔드 페이지](#5-프론트엔드-페이지)
6. [구현 순서 (Sprint Plan)](#6-구현-순서-sprint-plan)
7. [기술 제약 및 솔루션](#7-기술-제약-및-솔루션)

---

## 1. 현재 인프라 분석

### ✅ 기존 구축 완료
- **Framework**: Next.js 14 + TypeScript
- **Database**: Supabase (PostgreSQL + RLS)
- **Authentication**: Supabase Auth (이메일/비밀번호 + Google OAuth)
- **Deployment**: GitHub Pages (정적 배포)
- **UI**: Tailwind CSS
- **Chart**: Recharts

### ✅ 현재 데이터 파이프라인
```
유튜브 영상 → AI 분석 → influencer_signals 테이블 → 대시보드
├── influencers (인플루언서 정보)
├── influencer_channels (채널 정보)
├── influencer_videos (영상 정보)
└── influencer_signals (종목 시그널)
```

### ✅ 기존 `/my-stocks` 페이지
- 기본 피드 구조 구현됨
- 인플루언서 시그널 데이터 연동 완료
- 종목 필터링 UI 있음 (하드코딩)
- 시그널 상세 모달 구현됨

### 🔧 개선 필요 영역
- 사용자별 종목 관리 (보유 종목, 관심 종목)
- 개인화된 알림 설정
- 사용자 프로필 관리
- AI 분석의 개인화

---

## 2. Supabase Auth 설계

### 2.1 현재 Auth 상태
```typescript
// context/AuthContext.tsx - 이미 구현됨
interface AuthContextType {
  user: User | null;           // Supabase User 객체
  session: Session | null;     // JWT 세션
  loading: boolean;
  signUp: (email: string, password: string) => Promise<{ error: any }>;
  signIn: (email: string, password: string) => Promise<{ error: any }>;
  signInWithGoogle: () => Promise<{ error: any }>;
  signOut: () => Promise<void>;
}
```

### 2.2 확장 필요사항
```typescript
// 프로필 완성도 체크 추가
interface ExtendedAuthContextType extends AuthContextType {
  profile: UserProfile | null;
  updateProfile: (data: Partial<UserProfile>) => Promise<{ error: any }>;
  isProfileComplete: boolean;
}

interface UserProfile {
  id: string;
  email: string;
  display_name?: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
  // 대시보드 설정
  dashboard_preferences: {
    default_view: 'portfolio' | 'watchlist' | 'feed';
    show_notifications: boolean;
    show_ai_insights: boolean;
  };
}
```

### 2.3 RLS 정책 전략
```sql
-- 모든 사용자별 테이블에 적용할 기본 RLS 패턴
CREATE POLICY "users_own_data" ON user_stocks 
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "users_own_watchlist" ON user_watchlist 
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "users_own_notifications" ON user_notifications 
  FOR ALL USING (auth.uid() = user_id);
```

---

## 3. DB 스키마 설계

### 3.1 사용자 프로필 확장
```sql
-- users 테이블 (Supabase auth.users 확장)
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  display_name TEXT,
  avatar_url TEXT,
  dashboard_preferences JSONB DEFAULT '{
    "default_view": "portfolio",
    "show_notifications": true,
    "show_ai_insights": true
  }'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS 활성화
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users_own_profile" ON public.user_profiles 
  FOR ALL USING (auth.uid() = id);
```

### 3.2 보유 종목 관리
```sql
-- 사용자 보유 종목 테이블
CREATE TABLE IF NOT EXISTS public.user_stocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  stock_code TEXT NOT NULL,        -- '005930', 'NVDA'
  stock_name TEXT NOT NULL,        -- '삼성전자', 'NVIDIA Corp'
  market TEXT NOT NULL CHECK (market IN (
    'KR', 'US', 'JP', 'CN', 'CRYPTO'
  )),
  
  -- 매수 정보
  quantity DECIMAL(15,4) NOT NULL,
  avg_buy_price DECIMAL(15,4) NOT NULL,
  total_investment DECIMAL(15,2) GENERATED ALWAYS AS (quantity * avg_buy_price) STORED,
  
  -- 메타데이터
  first_bought_at TIMESTAMPTZ DEFAULT NOW(),
  last_updated_at TIMESTAMPTZ DEFAULT NOW(),
  notes TEXT,                      -- 매수 이유, 메모 등
  
  -- 제약조건
  UNIQUE(user_id, stock_code),
  CHECK (quantity > 0),
  CHECK (avg_buy_price > 0)
);

-- 인덱스
CREATE INDEX idx_user_stocks_user_id ON public.user_stocks(user_id);
CREATE INDEX idx_user_stocks_market ON public.user_stocks(market);

-- RLS
ALTER TABLE public.user_stocks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users_own_stocks" ON public.user_stocks 
  FOR ALL USING (auth.uid() = user_id);
```

### 3.3 관심 종목 (워치리스트)
```sql
-- 사용자 관심 종목 테이블
CREATE TABLE IF NOT EXISTS public.user_watchlist (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  stock_code TEXT NOT NULL,
  stock_name TEXT NOT NULL,
  market TEXT NOT NULL CHECK (market IN (
    'KR', 'US', 'JP', 'CN', 'CRYPTO'
  )),
  
  -- 알림 설정
  alert_on_signals BOOLEAN DEFAULT true,        -- 시그널 발생시 알림
  alert_price_target DECIMAL(15,4),             -- 목표가 알림
  alert_price_type TEXT CHECK (alert_price_type IN ('above', 'below')),
  
  -- 메타데이터
  added_at TIMESTAMPTZ DEFAULT NOW(),
  notes TEXT,
  
  -- 제약조건
  UNIQUE(user_id, stock_code)
);

-- 인덱스 & RLS
CREATE INDEX idx_user_watchlist_user_id ON public.user_watchlist(user_id);
ALTER TABLE public.user_watchlist ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users_own_watchlist" ON public.user_watchlist 
  FOR ALL USING (auth.uid() = user_id);
```

### 3.4 알림 설정 및 기록
```sql
-- 사용자 알림 설정
CREATE TABLE IF NOT EXISTS public.user_notification_settings (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- 글로벌 알림 설정
  enabled BOOLEAN DEFAULT true,
  
  -- 카테고리별 알림 설정
  portfolio_alerts BOOLEAN DEFAULT true,        -- 보유종목 시그널
  watchlist_alerts BOOLEAN DEFAULT true,        -- 관심종목 시그널
  price_alerts BOOLEAN DEFAULT true,            -- 가격 알림
  analyst_reports BOOLEAN DEFAULT true,         -- 애널리스트 리포트
  
  -- 알림 방식 (향후 확장용)
  email_enabled BOOLEAN DEFAULT false,
  push_enabled BOOLEAN DEFAULT true,
  
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 알림 기록 (발송 이력)
CREATE TABLE IF NOT EXISTS public.user_notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- 알림 내용
  type TEXT NOT NULL CHECK (type IN (
    'signal', 'price_target', 'analyst_report', 'market_summary'
  )),
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  stock_code TEXT,                              -- 관련 종목 (선택사항)
  
  -- 상태
  is_read BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  read_at TIMESTAMPTZ,
  
  -- 메타데이터 (JSON)
  metadata JSONB                                -- 시그널 ID, 리포트 URL 등
);

-- 인덱스
CREATE INDEX idx_user_notifications_user_id ON public.user_notifications(user_id);
CREATE INDEX idx_user_notifications_unread ON public.user_notifications(user_id) 
  WHERE is_read = false;
CREATE INDEX idx_user_notifications_created ON public.user_notifications(created_at DESC);

-- RLS
ALTER TABLE public.user_notification_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_notification_settings" ON public.user_notification_settings 
  FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "users_own_notifications" ON public.user_notifications 
  FOR ALL USING (auth.uid() = user_id);
```

---

## 4. API 설계

### 4.1 Supabase REST API 엔드포인트

#### 보유 종목 관리
```typescript
// lib/api/user-stocks.ts
export async function getUserStocks(userId: string) {
  const { data, error } = await supabase
    .from('user_stocks')
    .select('*')
    .eq('user_id', userId)
    .order('total_investment', { ascending: false });
  return { data, error };
}

export async function addUserStock(stockData: {
  stock_code: string;
  stock_name: string;
  market: string;
  quantity: number;
  avg_buy_price: number;
  notes?: string;
}) {
  const { data, error } = await supabase
    .from('user_stocks')
    .insert([{
      user_id: (await supabase.auth.getUser()).data.user?.id,
      ...stockData
    }]);
  return { data, error };
}

export async function updateUserStock(stockId: string, updates: {
  quantity?: number;
  avg_buy_price?: number;
  notes?: string;
}) {
  const { data, error } = await supabase
    .from('user_stocks')
    .update(updates)
    .eq('id', stockId);
  return { data, error };
}

export async function deleteUserStock(stockId: string) {
  const { data, error } = await supabase
    .from('user_stocks')
    .delete()
    .eq('id', stockId);
  return { data, error };
}
```

#### 관심 종목 관리
```typescript
// lib/api/user-watchlist.ts
export async function getUserWatchlist(userId: string) {
  const { data, error } = await supabase
    .from('user_watchlist')
    .select('*')
    .eq('user_id', userId)
    .order('added_at', { ascending: false });
  return { data, error };
}

export async function addToWatchlist(watchlistData: {
  stock_code: string;
  stock_name: string;
  market: string;
  alert_on_signals?: boolean;
  alert_price_target?: number;
  notes?: string;
}) {
  // 중복 체크 후 추가
  const { data, error } = await supabase
    .from('user_watchlist')
    .upsert([{
      user_id: (await supabase.auth.getUser()).data.user?.id,
      ...watchlistData
    }]);
  return { data, error };
}

export async function removeFromWatchlist(stockCode: string) {
  const { data, error } = await supabase
    .from('user_watchlist')
    .delete()
    .eq('stock_code', stockCode)
    .eq('user_id', (await supabase.auth.getUser()).data.user?.id);
  return { data, error };
}
```

#### 개인화된 시그널 조회
```typescript
// lib/api/personalized-signals.ts
export async function getPersonalizedSignals(userId: string, limit = 20) {
  // 보유종목 + 관심종목의 최신 시그널만 조회
  const { data: portfolioStocks } = await getUserStocks(userId);
  const { data: watchlistStocks } = await getUserWatchlist(userId);
  
  const allStockCodes = [
    ...(portfolioStocks?.map(s => s.stock_code) || []),
    ...(watchlistStocks?.map(s => s.stock_code) || [])
  ];
  
  if (allStockCodes.length === 0) {
    return { data: [], error: null };
  }
  
  const { data, error } = await supabase
    .from('influencer_signals')
    .select(`
      *,
      video:influencer_videos!inner(
        title,
        published_at,
        channel:influencer_channels!inner(
          channel_name,
          influencer:influencers!inner(name)
        )
      )
    `)
    .in('ticker', allStockCodes)
    .eq('review_status', 'approved')
    .order('video.published_at', { ascending: false })
    .limit(limit);
    
  return { data, error };
}
```

### 4.2 실시간 데이터 동기화
```typescript
// lib/api/real-time.ts
export function subscribeToUserSignals(
  userId: string, 
  callback: (payload: any) => void
) {
  // 사용자의 종목에 대한 새로운 시그널 실시간 감지
  return supabase
    .channel('user-signals')
    .on('postgres_changes', {
      event: 'INSERT',
      schema: 'public',
      table: 'influencer_signals',
      filter: `review_status=eq.approved`
    }, callback)
    .subscribe();
}

export function subscribeToUserNotifications(
  userId: string,
  callback: (payload: any) => void
) {
  return supabase
    .channel(`user-notifications:${userId}`)
    .on('postgres_changes', {
      event: 'INSERT',
      schema: 'public',
      table: 'user_notifications',
      filter: `user_id=eq.${userId}`
    }, callback)
    .subscribe();
}
```

---

## 5. 프론트엔드 페이지

### 5.1 `/my-stocks` 메인 대시보드 개선

#### 현재 상태 분석
- ✅ 기본 피드 구조 있음
- ✅ 시그널 카드 컴포넌트 있음
- ✅ 상세 모달 있음
- 🔧 하드코딩된 종목 필터 → 동적 종목 관리로 교체 필요

#### 개선된 페이지 구조
```typescript
// app/my-stocks/page.tsx (개선)
'use client';

export default function MyStocksDashboard() {
  const { user } = useAuth();
  const [view, setView] = useState<'portfolio' | 'watchlist' | 'feed'>('portfolio');
  const [portfolioStocks, setPortfolioStocks] = useState([]);
  const [watchlistStocks, setWatchlistStocks] = useState([]);
  const [personalizedSignals, setPersonalizedSignals] = useState([]);
  
  return (
    <div className="container mx-auto p-4">
      {/* 헤더 - 시황 요약 */}
      <MarketSummaryCard />
      
      {/* 탭 네비게이션 */}
      <TabNavigation view={view} setView={setView} />
      
      {view === 'portfolio' && (
        <PortfolioView 
          stocks={portfolioStocks}
          signals={personalizedSignals.filter(s => 
            portfolioStocks.some(p => p.stock_code === s.ticker)
          )}
        />
      )}
      
      {view === 'watchlist' && (
        <WatchlistView 
          stocks={watchlistStocks}
          signals={personalizedSignals.filter(s => 
            watchlistStocks.some(w => w.stock_code === s.ticker)
          )}
        />
      )}
      
      {view === 'feed' && (
        <PersonalizedFeedView signals={personalizedSignals} />
      )}
    </div>
  );
}
```

#### 새로운 컴포넌트들

##### 5.1.1 시황 요약 카드
```typescript
// components/MarketSummaryCard.tsx
export default function MarketSummaryCard() {
  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-xl font-bold mb-4">📊 오늘의 시황</h2>
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-sm text-gray-600">코스피</div>
          <div className="text-lg font-bold text-red-500">2,640.23 (-1.2%)</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-600">나스닥</div>
          <div className="text-lg font-bold text-green-500">14,823.43 (+0.8%)</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-600">원/달러</div>
          <div className="text-lg font-bold">1,342.50</div>
        </div>
      </div>
      
      {/* AI 시황 요약 */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <div className="text-sm font-medium text-blue-800">🤖 AI 시황 요약</div>
        <div className="text-sm text-blue-700 mt-1">
          오늘은 미국 고용지표 발표로 인한 변동성이 예상됩니다. 
          테크주 중심으로 상승세를 보이고 있어 관련 종목에 주목하세요.
        </div>
      </div>
    </div>
  );
}
```

##### 5.1.2 보유 종목 뷰
```typescript
// components/PortfolioView.tsx
interface PortfolioStock {
  id: string;
  stock_code: string;
  stock_name: string;
  quantity: number;
  avg_buy_price: number;
  current_price?: number;  // 실시간 가격 (외부 API)
  market: string;
}

export default function PortfolioView({ stocks, signals }: {
  stocks: PortfolioStock[];
  signals: any[];
}) {
  const totalInvestment = stocks.reduce((sum, stock) => 
    sum + (stock.quantity * stock.avg_buy_price), 0);
  
  const totalValue = stocks.reduce((sum, stock) => 
    sum + (stock.quantity * (stock.current_price || stock.avg_buy_price)), 0);
    
  const totalGainLoss = totalValue - totalInvestment;
  const totalGainLossPercent = (totalGainLoss / totalInvestment) * 100;
  
  return (
    <div className="space-y-6">
      {/* 포트폴리오 요약 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold mb-4">💰 포트폴리오 요약</h3>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-600">투자금액</div>
            <div className="text-xl font-bold">
              {formatCurrency(totalInvestment, 'KR')}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">현재가치</div>
            <div className="text-xl font-bold">
              {formatCurrency(totalValue, 'KR')}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">손익</div>
            <div className={`text-xl font-bold ${totalGainLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {totalGainLoss >= 0 ? '+' : ''}{formatCurrency(totalGainLoss, 'KR')}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">수익률</div>
            <div className={`text-xl font-bold ${totalGainLossPercent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {totalGainLossPercent >= 0 ? '+' : ''}{totalGainLossPercent.toFixed(2)}%
            </div>
          </div>
        </div>
      </div>
      
      {/* 종목별 상세 */}
      <div className="space-y-4">
        {stocks.map(stock => (
          <PortfolioStockCard 
            key={stock.id} 
            stock={stock} 
            recentSignals={signals.filter(s => s.ticker === stock.stock_code)}
          />
        ))}
      </div>
      
      {/* 종목 추가 버튼 */}
      <AddStockButton type="portfolio" />
    </div>
  );
}
```

##### 5.1.3 개인화된 AI 인사이트
```typescript
// components/AIInsightCard.tsx
export default function AIInsightCard({ userStocks }: { userStocks: any[] }) {
  const [insights, setInsights] = useState([]);
  
  useEffect(() => {
    // 사용자 종목 기반 AI 인사이트 생성
    generatePersonalizedInsights(userStocks).then(setInsights);
  }, [userStocks]);
  
  return (
    <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg shadow p-6">
      <h3 className="text-lg font-bold mb-4">🎯 AI 맞춤 분석</h3>
      
      {insights.map((insight, index) => (
        <div key={index} className="mb-3 last:mb-0">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <span className="text-purple-600 text-sm font-bold">{index + 1}</span>
            </div>
            <div>
              <div className="font-medium text-gray-900">{insight.title}</div>
              <div className="text-sm text-gray-600">{insight.summary}</div>
              {insight.action && (
                <div className="mt-2 px-3 py-1 bg-purple-100 text-purple-700 text-xs rounded-full inline-block">
                  💡 {insight.action}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

async function generatePersonalizedInsights(userStocks: any[]) {
  // 사용자 종목의 최근 시그널 패턴 분석
  // 시장 상황과 개인 포트폴리오 매칭
  // AI 기반 리밸런싱 제안 등
  
  return [
    {
      title: "삼성전자 매수 시그널 증가",
      summary: "최근 3일간 인플루언서들의 긍정 시그널이 85% 증가했습니다.",
      action: "추가 매수 검토 권장"
    },
    {
      title: "포트폴리오 집중도 높음", 
      summary: "IT 섹터 비중이 65%입니다. 분산투자를 고려해보세요.",
      action: "금융/바이오 섹터 관심종목 추가"
    }
  ];
}
```

### 5.2 종목 추가/편집 모달

#### 종목 추가 모달 컴포넌트
```typescript
// components/AddStockModal.tsx
interface AddStockModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'portfolio' | 'watchlist';
}

export default function AddStockModal({ isOpen, onClose, type }: AddStockModalProps) {
  const [formData, setFormData] = useState({
    stock_code: '',
    stock_name: '',
    market: 'KR',
    quantity: type === 'portfolio' ? 0 : undefined,
    avg_buy_price: type === 'portfolio' ? 0 : undefined,
    notes: ''
  });
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (type === 'portfolio') {
        await addUserStock(formData);
      } else {
        await addToWatchlist(formData);
      }
      onClose();
      // 리스트 새로고침
    } catch (error) {
      console.error('Failed to add stock:', error);
    }
  };
  
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <h2 className="text-xl font-bold">
          {type === 'portfolio' ? '보유 종목 추가' : '관심 종목 추가'}
        </h2>
        
        {/* 종목 검색 */}
        <StockSearchInput
          value={formData.stock_code}
          onChange={(stock) => setFormData({
            ...formData,
            stock_code: stock.code,
            stock_name: stock.name,
            market: stock.market
          })}
        />
        
        {/* 포트폴리오인 경우만 수량/매수가 입력 */}
        {type === 'portfolio' && (
          <>
            <div>
              <label className="block text-sm font-medium">보유 수량</label>
              <input
                type="number"
                step="0.0001"
                value={formData.quantity}
                onChange={(e) => setFormData({
                  ...formData,
                  quantity: parseFloat(e.target.value)
                })}
                className="mt-1 block w-full rounded-md border-gray-300"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium">평균 매수가</label>
              <input
                type="number"
                step="0.01"
                value={formData.avg_buy_price}
                onChange={(e) => setFormData({
                  ...formData,
                  avg_buy_price: parseFloat(e.target.value)
                })}
                className="mt-1 block w-full rounded-md border-gray-300"
                required
              />
            </div>
          </>
        )}
        
        {/* 메모 */}
        <div>
          <label className="block text-sm font-medium">메모 (선택사항)</label>
          <textarea
            value={formData.notes}
            onChange={(e) => setFormData({
              ...formData,
              notes: e.target.value
            })}
            className="mt-1 block w-full rounded-md border-gray-300"
            rows={3}
            placeholder="매수 이유, 목표가 등을 입력하세요"
          />
        </div>
        
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-gray-600 bg-gray-100 rounded-md"
          >
            취소
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-md"
          >
            추가
          </button>
        </div>
      </form>
    </Modal>
  );
}
```

### 5.3 알림 설정 페이지
```typescript
// app/my-stocks/settings/page.tsx
export default function NotificationSettings() {
  const [settings, setSettings] = useState({
    portfolio_alerts: true,
    watchlist_alerts: true,
    price_alerts: true,
    analyst_reports: true
  });
  
  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">알림 설정</h1>
      
      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium">보유종목 시그널 알림</div>
            <div className="text-sm text-gray-600">보유하고 있는 종목에 새로운 시그널이 발생하면 알림을 받습니다</div>
          </div>
          <Toggle 
            checked={settings.portfolio_alerts}
            onChange={(checked) => setSettings({...settings, portfolio_alerts: checked})}
          />
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium">관심종목 시그널 알림</div>
            <div className="text-sm text-gray-600">관심종목에 새로운 시그널이 발생하면 알림을 받습니다</div>
          </div>
          <Toggle 
            checked={settings.watchlist_alerts}
            onChange={(checked) => setSettings({...settings, watchlist_alerts: checked})}
          />
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium">가격 알림</div>
            <div className="text-sm text-gray-600">설정한 목표가에 도달하면 알림을 받습니다</div>
          </div>
          <Toggle 
            checked={settings.price_alerts}
            onChange={(checked) => setSettings({...settings, price_alerts: checked})}
          />
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium">애널리스트 리포트</div>
            <div className="text-sm text-gray-600">보유/관심종목의 새로운 애널리스트 리포트가 나오면 알림을 받습니다</div>
          </div>
          <Toggle 
            checked={settings.analyst_reports}
            onChange={(checked) => setSettings({...settings, analyst_reports: checked})}
          />
        </div>
      </div>
      
      <div className="mt-6">
        <button 
          onClick={handleSaveSettings}
          className="w-full bg-blue-600 text-white py-3 rounded-md font-medium"
        >
          설정 저장
        </button>
      </div>
    </div>
  );
}
```

---

## 6. 구현 순서 (Sprint Plan)

### Sprint 1: 기반 인프라 구축 (2일)
**목표**: 사용자별 데이터 저장 및 인증 강화

#### Day 1: DB 스키마 & Auth 개선
- [ ] **DB 마이그레이션 파일 작성**
  - `supabase/migrations/20260306000000_user_stocks_dashboard.sql`
  - user_profiles, user_stocks, user_watchlist, user_notifications 테이블
  - RLS 정책 설정
- [ ] **Auth Context 확장**
  - UserProfile 타입 추가
  - 프로필 완성도 체크 로직
  - updateProfile 함수 구현
- [ ] **API 함수 구현**
  - `lib/api/user-stocks.ts` (CRUD)
  - `lib/api/user-watchlist.ts` (CRUD)  
  - `lib/api/user-profile.ts`

#### Day 2: 기본 UI 컴포넌트
- [ ] **공통 컴포넌트 구현**
  - `components/AddStockModal.tsx`
  - `components/StockSearchInput.tsx` (기존 종목 데이터 활용)
  - `components/Toggle.tsx`
- [ ] **기본 데이터 연동 테스트**
  - 종목 추가/삭제/수정 동작 확인
  - RLS 권한 체크
  - 로그인 후 데이터 격리 확인

**Sprint 1 완료 기준**: 로그인 후 종목 추가/삭제가 정상 동작하고, 다른 사용자와 데이터가 격리됨

---

### Sprint 2: 보유/관심 종목 CRUD (2일)

#### Day 3: 포트폴리오 관리
- [ ] **PortfolioView 컴포넌트**
  - 보유종목 리스트 표시
  - 총 투자금액, 현재가치, 손익 계산
  - 종목별 카드 (수량, 평균매수가, 현재손익)
- [ ] **편집 기능 구현**
  - 수량/매수가 수정 모달
  - 종목별 메모 편집
  - 종목 삭제 (확인 다이얼로그)
- [ ] **정렬/필터링**
  - 투자금액순, 수익률순, 가나다순
  - 시장별 필터링 (한국/미국/기타)

#### Day 4: 관심종목 관리
- [ ] **WatchlistView 컴포넌트**
  - 관심종목 리스트 표시
  - 빠른 추가/삭제 버튼
- [ ] **가격 알림 설정**
  - 목표가 설정 UI
  - 알림 조건 (이상/이하) 선택
- [ ] **관심종목 → 포트폴리오 이동**
  - "매수 완료" 버튼으로 보유종목으로 이동
  - 수량/매수가 입력 후 자동 이관

**Sprint 2 완료 기준**: 보유/관심 종목을 자유롭게 추가/편집/삭제할 수 있고, 기본적인 손익 계산이 표시됨

---

### Sprint 3: 대시보드 UI 완성 (3일)

#### Day 5: 메인 대시보드 레이아웃  
- [ ] **MarketSummaryCard 구현**
  - 주요 지수 표시 (하드코딩 → 향후 실시간 연동)
  - 환율 정보
  - 간단한 시장 상황 텍스트
- [ ] **TabNavigation 구현**
  - 포트폴리오 / 관심종목 / 피드 탭
  - 각 탭별 뱃지 (보유종목 수, 알림 수 등)
- [ ] **기존 `/my-stocks/page.tsx` 리팩토링**
  - 하드코딩된 종목 칩 → 동적 사용자 데이터
  - 개인화된 피드 연동

#### Day 6: 개인화된 피드
- [ ] **PersonalizedFeedView 구현**
  - 사용자 종목만 필터링된 시그널 피드
  - 보유종목 시그널과 관심종목 시그널 구분
  - 시그널 카드에 "보유중" / "관심" 라벨 추가
- [ ] **실시간 업데이트**
  - Supabase Realtime으로 새 시그널 감지
  - 토스트 알림 또는 배너로 알림

#### Day 7: 반응형 및 UX 개선
- [ ] **모바일 반응형 최적화**
  - 탭 네비게이션 모바일 최적화
  - 터치 친화적인 버튼 크기
  - 스와이프 제스처 고려
- [ ] **로딩 상태 및 에러 처리**
  - Skeleton 로딩 UI
  - 네트워크 오류 처리
  - 빈 상태(Empty State) 디자인
- [ ] **접근성 개선**
  - 키보드 네비게이션
  - 스크린 리더 지원
  - 충분한 색상 대비

**Sprint 3 완료 기준**: 완전히 기능하는 개인화된 대시보드가 구현되고, 모바일에서도 원활하게 동작함

---

### Sprint 4: AI 분석 + 알림 시스템 (3일)

#### Day 8: AI 개인화 분석
- [ ] **AIInsightCard 구현**
  - 사용자 종목 기반 패턴 분석
  - 시그널 트렌드 분석 (긍정/부정 비율 변화)
  - 포트폴리오 리밸런싱 제안
- [ ] **개인화 알고리즘**
  - 최근 30일 시그널 패턴 분석
  - 섹터별 집중도 분석
  - 수익률과 시그널 상관관계 분석

#### Day 9: 알림 시스템 기반
- [ ] **NotificationSettings 페이지**
  - 알림 카테고리별 ON/OFF
  - 사용자별 설정 저장/로드
- [ ] **알림 생성 로직**
  - 새 시그널 발생시 알림 생성
  - 목표가 도달시 알림 생성 (가격 데이터 연동 시)
- [ ] **알림 표시 UI**
  - 헤더에 알림 벨 아이콘 + 뱃지
  - 알림 드롭다운 또는 별도 페이지

#### Day 10: 통합 테스트 및 최적화
- [ ] **전체 플로우 테스트**
  - 회원가입 → 종목 추가 → 시그널 확인 → 알림 설정
  - 다양한 시나리오 테스트
- [ ] **성능 최적화**
  - API 호출 최적화 (불필요한 요청 제거)
  - 이미지 최적화
  - 번들 크기 최적화
- [ ] **GitHub Pages 배포**
  - Build 에러 수정
  - 정적 배포 최적화
  - 배포 후 기능 검증

**Sprint 4 완료 기준**: 완성된 개인화 대시보드가 프로덕션 환경에서 안정적으로 동작하고, 사용자가 알림을 통해 실시간으로 종목 정보를 받을 수 있음

---

## 7. 기술 제약 및 솔루션

### 7.1 GitHub Pages 정적 배포 제약

#### 제약사항
- **SSR 불가**: Next.js의 서버 사이드 기능 제한
- **API Routes 불가**: `/api/*` 경로 사용 불가
- **실시간 기능 제한**: WebSocket 등 서버 기능 없음

#### 솔루션
```typescript
// 1. Client-Side Only 렌더링
'use client';  // 모든 컴포넌트에서 명시적으로 선언

// 2. Supabase로 API 대체
// /api/stocks → supabase.from('user_stocks').select()

// 3. Static Export 설정
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  basePath: '/invest-sns',
  assetPrefix: '/invest-sns/',
  images: {
    unoptimized: true
  }
};

// 4. 환경변수는 NEXT_PUBLIC_ 접두사 필수
process.env.NEXT_PUBLIC_SUPABASE_URL
process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
```

### 7.2 Supabase Free Tier 제약

#### 제약사항
- **Database**: 500MB 저장공간
- **Auth**: 50,000 MAU (월간 활성 사용자)  
- **API**: 무제한 요청 (rate limit 있음)
- **Realtime**: 200 concurrent connections

#### 모니터링 및 최적화
```typescript
// 1. 쿼리 최적화
export async function getPersonalizedSignalsOptimized(userId: string) {
  // 사용자 종목만 미리 조회해서 IN 절 최소화
  const { data: userStockCodes } = await supabase
    .from('user_stocks')
    .select('stock_code')
    .eq('user_id', userId);
    
  if (!userStockCodes?.length) return { data: [], error: null };
  
  // 필요한 컬럼만 선택
  const { data, error } = await supabase
    .from('influencer_signals')
    .select('id, ticker, signal, confidence, key_quote, created_at, video_id')
    .in('ticker', userStockCodes.map(s => s.stock_code))
    .order('created_at', { ascending: false })
    .limit(20);
    
  return { data, error };
}

// 2. 캐싱 전략
const CACHE_TTL = 5 * 60 * 1000; // 5분
const signalsCache = new Map();

export async function getCachedSignals(userId: string) {
  const cacheKey = `signals:${userId}`;
  const cached = signalsCache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  
  const freshData = await getPersonalizedSignalsOptimized(userId);
  signalsCache.set(cacheKey, {
    data: freshData,
    timestamp: Date.now()
  });
  
  return freshData;
}
```

### 7.3 실시간 vs 폴링 전략

#### 실시간 (Supabase Realtime)
```typescript
// 장점: 즉시 반영, 사용자 경험 우수
// 단점: Connection 제한, 배터리 소모

export function useRealtimeSignals(userId: string) {
  const [signals, setSignals] = useState([]);
  
  useEffect(() => {
    const subscription = supabase
      .channel('user-signals')
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'influencer_signals'
      }, (payload) => {
        // 사용자 종목인지 클라이언트에서 필터링
        if (isUserStock(payload.new.ticker, userId)) {
          setSignals(prev => [payload.new, ...prev]);
        }
      })
      .subscribe();
      
    return () => subscription.unsubscribe();
  }, [userId]);
  
  return signals;
}
```

#### 폴링 (Fallback)
```typescript
// 장점: 안정적, 리소스 효율적
// 단점: 지연 시간, API 호출량

export function usePollingSignals(userId: string) {
  const [signals, setSignals] = useState([]);
  
  useEffect(() => {
    const poll = async () => {
      const { data } = await getCachedSignals(userId);
      if (data) setSignals(data);
    };
    
    poll(); // 즉시 실행
    const interval = setInterval(poll, 30000); // 30초마다
    
    return () => clearInterval(interval);
  }, [userId]);
  
  return signals;
}

// 하이브리드 접근
export function useSignals(userId: string) {
  const realtimeSignals = useRealtimeSignals(userId);
  const pollingSignals = usePollingSignals(userId);
  
  // Realtime 연결이 안정적이면 실시간, 아니면 폴링
  const [connectionStable, setConnectionStable] = useState(true);
  
  return connectionStable ? realtimeSignals : pollingSignals;
}
```

### 7.4 외부 주가 데이터 연동

#### 무료 API 활용 전략
```typescript
// 1. 알파벤티지 (무료 tier: 5 calls/min, 500 calls/day)
const ALPHA_VANTAGE_API_KEY = process.env.NEXT_PUBLIC_ALPHA_VANTAGE_KEY;

export async function getStockPrice(symbol: string, market: string) {
  if (market === 'US') {
    const response = await fetch(
      `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${ALPHA_VANTAGE_API_KEY}`
    );
    const data = await response.json();
    return data['Global Quote']?.['05. price'];
  }
  
  // 한국 주식은 한국투자증권 등 별도 API 검토 필요
  return null;
}

// 2. 캐싱으로 API 호출 최소화
const priceCache = new Map();
const PRICE_CACHE_TTL = 60000; // 1분

export async function getCachedStockPrice(symbol: string, market: string) {
  const cacheKey = `price:${market}:${symbol}`;
  const cached = priceCache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < PRICE_CACHE_TTL) {
    return cached.price;
  }
  
  const price = await getStockPrice(symbol, market);
  if (price) {
    priceCache.set(cacheKey, { price, timestamp: Date.now() });
  }
  
  return price;
}
```

---

## 📝 구현 체크리스트

### Sprint 1 (기반 인프라) ✅/❌
- [ ] DB 마이그레이션 파일 작성 및 배포
- [ ] RLS 정책 테스트
- [ ] Auth Context 확장 (UserProfile)
- [ ] API 함수 구현 (user-stocks, user-watchlist)
- [ ] 기본 UI 컴포넌트 (AddStockModal, Toggle)

### Sprint 2 (CRUD 기능) ✅/❌ 
- [ ] 포트폴리오 관리 UI
- [ ] 관심종목 관리 UI
- [ ] 종목 편집/삭제 기능
- [ ] 손익 계산 로직

### Sprint 3 (대시보드 UI) ✅/❌
- [ ] MarketSummaryCard 구현
- [ ] 개인화된 피드
- [ ] 반응형 디자인
- [ ] 로딩/에러 상태 처리

### Sprint 4 (AI + 알림) ✅/❌
- [ ] AI 인사이트 카드
- [ ] 알림 설정 페이지  
- [ ] 실시간 알림 시스템
- [ ] 전체 통합 테스트 + 배포

---

## 🚀 배포 및 모니터링

### 배포 프로세스
```bash
# 1. 개발 환경에서 테스트
npm run dev

# 2. 빌드 테스트
npm run build

# 3. GitHub Pages 배포
npm run deploy

# 4. 배포 후 기능 검증
# - 회원가입/로그인
# - 종목 추가/삭제
# - 실시간 시그널 수신
# - 알림 설정
```

### 사용자 피드백 수집
- **텔레그램 그룹**: 베타 테스터 피드백
- **GA4**: 사용자 행동 분석 (페이지뷰, 체류시간)
- **Supabase Analytics**: DB 쿼리 성능, 에러율 모니터링

---

## 📋 완료 보고

이 기술 스펙에 따라 구현을 완료하면 다음과 같은 결과물이 완성됩니다:

1. **개인화된 종목 대시보드** - 사용자별 보유/관심 종목 관리
2. **실시간 AI 분석** - 개인 포트폴리오 기반 맞춤 인사이트  
3. **스마트 알림 시스템** - 종목별 시그널 & 가격 알림
4. **반응형 모바일 UI** - 언제 어디서나 접근 가능
5. **확장 가능한 아키텍처** - 향후 프리미엄 기능 추가 용이

**다음 단계**: Sprint 1부터 순차적으로 구현을 시작하고, 각 Sprint 완료시 텔레그램 그룹에 진행상황을 보고해주세요.