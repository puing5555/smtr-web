-- Invest SNS Database Schema
-- PostgreSQL (Supabase)

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table (Supabase Auth 확장)
CREATE TABLE public.users (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(50) UNIQUE NOT NULL,
  display_name VARCHAR(100),
  avatar_url TEXT,
  bio TEXT,
  is_verified BOOLEAN DEFAULT FALSE,
  is_influencer BOOLEAN DEFAULT FALSE,
  investment_style VARCHAR(50), -- 'conservative', 'moderate', 'aggressive'
  experience_level VARCHAR(50), -- 'beginner', 'intermediate', 'expert'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL
);

-- Influencers table (인플루언서 정보)
CREATE TABLE public.influencers (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  rating DECIMAL(3,2) DEFAULT 0, -- 0.00 ~ 5.00
  total_followers INTEGER DEFAULT 0,
  success_rate DECIMAL(5,2) DEFAULT 0, -- 성공률 %
  total_signals INTEGER DEFAULT 0,
  specialty VARCHAR(100), -- 전문 분야
  certification_url TEXT, -- 자격증/인증서 URL
  subscription_price INTEGER DEFAULT 0, -- 월 구독료 (원)
  is_premium BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL
);

-- Stocks table (종목 정보)
CREATE TABLE public.stocks (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  symbol VARCHAR(20) NOT NULL UNIQUE, -- 종목 코드
  name VARCHAR(100) NOT NULL, -- 종목명
  market VARCHAR(50) NOT NULL, -- 'KOSPI', 'KOSDAQ', 'NYSE', 'NASDAQ'
  sector VARCHAR(100), -- 업종
  current_price DECIMAL(12,2),
  change_rate DECIMAL(8,4), -- 변동률 %
  volume BIGINT,
  market_cap BIGINT, -- 시가총액
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL
);

-- Posts table (SNS 피드 글)
CREATE TABLE public.posts (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  author_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  images TEXT[], -- 이미지 URL 배열
  post_type VARCHAR(50) DEFAULT 'general', -- 'general', 'signal', 'analysis', 'news'
  stock_symbols VARCHAR(20)[], -- 관련 종목 코드들
  hashtags TEXT[], -- 해시태그들
  is_premium BOOLEAN DEFAULT FALSE,
  likes_count INTEGER DEFAULT 0,
  comments_count INTEGER DEFAULT 0,
  shares_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL
);

-- Signals table (투자 시그널)
CREATE TABLE public.signals (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  influencer_id UUID REFERENCES public.influencers(id) ON DELETE CASCADE,
  post_id UUID REFERENCES public.posts(id) ON DELETE SET NULL,
  stock_symbol VARCHAR(20) NOT NULL,
  signal_type VARCHAR(50) NOT NULL, -- 'buy', 'sell', 'hold', 'watch'
  target_price DECIMAL(12,2),
  stop_loss DECIMAL(12,2),
  entry_price DECIMAL(12,2),
  current_price DECIMAL(12,2),
  confidence_level INTEGER CHECK (confidence_level >= 1 AND confidence_level <= 5), -- 1-5 확신도
  time_horizon VARCHAR(50), -- 'short', 'medium', 'long'
  rationale TEXT, -- 근거/이유
  status VARCHAR(50) DEFAULT 'active', -- 'active', 'closed', 'expired'
  result VARCHAR(50), -- 'success', 'failure', 'partial', null
  roi_percentage DECIMAL(8,4), -- 수익률 %
  expires_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL
);

-- Comments table (댓글)
CREATE TABLE public.comments (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  post_id UUID REFERENCES public.posts(id) ON DELETE CASCADE,
  author_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  parent_id UUID REFERENCES public.comments(id) ON DELETE CASCADE, -- 대댓글용
  content TEXT NOT NULL,
  likes_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL
);

-- Likes table (좋아요)
CREATE TABLE public.likes (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  post_id UUID REFERENCES public.posts(id) ON DELETE CASCADE,
  comment_id UUID REFERENCES public.comments(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL,
  UNIQUE(user_id, post_id),
  UNIQUE(user_id, comment_id),
  CHECK (
    (post_id IS NOT NULL AND comment_id IS NULL) OR 
    (post_id IS NULL AND comment_id IS NOT NULL)
  )
);

-- Follows table (팔로우)
CREATE TABLE public.follows (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  follower_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  following_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL,
  UNIQUE(follower_id, following_id),
  CHECK (follower_id != following_id)
);

-- Watchlist table (관심종목)
CREATE TABLE public.watchlist (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  stock_symbol VARCHAR(20) NOT NULL,
  notes TEXT,
  target_price DECIMAL(12,2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL,
  UNIQUE(user_id, stock_symbol)
);

-- Notifications table (알림)
CREATE TABLE public.notifications (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL, -- 'like', 'comment', 'follow', 'signal', 'mention'
  title VARCHAR(200) NOT NULL,
  message TEXT NOT NULL,
  data JSONB, -- 추가 데이터 (post_id, user_id 등)
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL
);

-- News table (뉴스)
CREATE TABLE public.news (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  title VARCHAR(500) NOT NULL,
  content TEXT,
  summary TEXT,
  url TEXT UNIQUE,
  source VARCHAR(100),
  author VARCHAR(100),
  published_at TIMESTAMP WITH TIME ZONE,
  stock_symbols VARCHAR(20)[], -- 관련 종목들
  sentiment VARCHAR(50), -- 'positive', 'negative', 'neutral'
  importance INTEGER CHECK (importance >= 1 AND importance <= 5), -- 중요도
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_posts_author_id ON public.posts(author_id);
CREATE INDEX idx_posts_created_at ON public.posts(created_at DESC);
CREATE INDEX idx_posts_stock_symbols ON public.posts USING GIN(stock_symbols);
CREATE INDEX idx_signals_influencer_id ON public.signals(influencer_id);
CREATE INDEX idx_signals_stock_symbol ON public.signals(stock_symbol);
CREATE INDEX idx_signals_created_at ON public.signals(created_at DESC);
CREATE INDEX idx_comments_post_id ON public.comments(post_id);
CREATE INDEX idx_likes_user_id ON public.likes(user_id);
CREATE INDEX idx_follows_follower_id ON public.follows(follower_id);
CREATE INDEX idx_follows_following_id ON public.follows(following_id);
CREATE INDEX idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX idx_notifications_created_at ON public.notifications(created_at DESC);
CREATE INDEX idx_news_published_at ON public.news(published_at DESC);
CREATE INDEX idx_news_stock_symbols ON public.news USING GIN(stock_symbols);

-- Row Level Security (RLS) policies
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.follows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.watchlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (더 구체적인 정책은 나중에 추가)
CREATE POLICY "Users can view public profiles" ON public.users FOR SELECT USING (true);
CREATE POLICY "Users can update own profile" ON public.users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Posts are viewable by everyone" ON public.posts FOR SELECT USING (true);
CREATE POLICY "Users can create posts" ON public.posts FOR INSERT WITH CHECK (auth.uid() = author_id);
CREATE POLICY "Users can update own posts" ON public.posts FOR UPDATE USING (auth.uid() = author_id);
CREATE POLICY "Users can delete own posts" ON public.posts FOR DELETE USING (auth.uid() = author_id);

-- Functions for updating timestamps
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = TIMEZONE('utc'::TEXT, NOW());
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER on_users_updated
  BEFORE UPDATE ON public.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER on_posts_updated
  BEFORE UPDATE ON public.posts
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER on_signals_updated
  BEFORE UPDATE ON public.signals
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

-- Sample data (optional)
-- INSERT INTO public.stocks (symbol, name, market, sector) VALUES
-- ('005930', '삼성전자', 'KOSPI', '전자기술'),
-- ('000660', 'SK하이닉스', 'KOSPI', '반도체'),
-- ('035420', 'NAVER', 'KOSPI', '인터넷'),
-- ('035720', '카카오', 'KOSPI', '인터넷');