// Database Types for Invest SNS

export interface User {
  id: string;
  email: string;
  username: string;
  display_name?: string;
  avatar_url?: string;
  bio?: string;
  is_verified: boolean;
  is_influencer: boolean;
  investment_style?: 'conservative' | 'moderate' | 'aggressive';
  experience_level?: 'beginner' | 'intermediate' | 'expert';
  created_at: string;
  updated_at: string;
}

export interface Influencer {
  id: string;
  user_id: string;
  rating: number;
  total_followers: number;
  success_rate: number;
  total_signals: number;
  specialty?: string;
  certification_url?: string;
  subscription_price: number;
  is_premium: boolean;
  created_at: string;
  updated_at: string;
  user?: User;
}

export interface Stock {
  id: string;
  symbol: string;
  name: string;
  market: 'KOSPI' | 'KOSDAQ' | 'NYSE' | 'NASDAQ';
  sector?: string;
  current_price?: number;
  change_rate?: number;
  volume?: number;
  market_cap?: number;
  created_at: string;
  updated_at: string;
}

export interface Post {
  id: string;
  author_id: string;
  content: string;
  images?: string[];
  post_type: 'general' | 'signal' | 'analysis' | 'news';
  stock_symbols?: string[];
  hashtags?: string[];
  is_premium: boolean;
  likes_count: number;
  comments_count: number;
  shares_count: number;
  created_at: string;
  updated_at: string;
  author?: User;
  comments?: Comment[];
  liked_by_user?: boolean;
}

export interface Signal {
  id: string;
  influencer_id: string;
  post_id?: string;
  stock_symbol: string;
  signal_type: 'buy' | 'sell' | 'hold' | 'watch';
  target_price?: number;
  stop_loss?: number;
  entry_price?: number;
  current_price?: number;
  confidence_level: 1 | 2 | 3 | 4 | 5;
  time_horizon: 'short' | 'medium' | 'long';
  rationale?: string;
  status: 'active' | 'closed' | 'expired';
  result?: 'success' | 'failure' | 'partial';
  roi_percentage?: number;
  expires_at?: string;
  created_at: string;
  updated_at: string;
  influencer?: Influencer;
  stock?: Stock;
  post?: Post;
}

export interface Comment {
  id: string;
  post_id: string;
  author_id: string;
  parent_id?: string;
  content: string;
  likes_count: number;
  created_at: string;
  updated_at: string;
  author?: User;
  replies?: Comment[];
  liked_by_user?: boolean;
}

export interface Like {
  id: string;
  user_id: string;
  post_id?: string;
  comment_id?: string;
  created_at: string;
}

export interface Follow {
  id: string;
  follower_id: string;
  following_id: string;
  created_at: string;
  follower?: User;
  following?: User;
}

export interface Watchlist {
  id: string;
  user_id: string;
  stock_symbol: string;
  notes?: string;
  target_price?: number;
  created_at: string;
  stock?: Stock;
}

export interface Notification {
  id: string;
  user_id: string;
  type: 'like' | 'comment' | 'follow' | 'signal' | 'mention';
  title: string;
  message: string;
  data?: Record<string, any>;
  is_read: boolean;
  created_at: string;
}

export interface News {
  id: string;
  title: string;
  content?: string;
  summary?: string;
  url?: string;
  source?: string;
  author?: string;
  published_at?: string;
  stock_symbols?: string[];
  sentiment?: 'positive' | 'negative' | 'neutral';
  importance: 1 | 2 | 3 | 4 | 5;
  created_at: string;
}

// Extended types with relations
export interface PostWithDetails extends Post {
  author: User;
  comments: Comment[];
  liked_by_user: boolean;
  stocks?: Stock[];
}

export interface SignalWithDetails extends Signal {
  influencer: Influencer;
  stock: Stock;
  post?: Post;
}

export interface CommentWithDetails extends Comment {
  author: User;
  replies: CommentWithDetails[];
  liked_by_user: boolean;
}

// API Response types
export interface PaginationMeta {
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface ApiResponse<T> {
  data: T;
  meta?: PaginationMeta;
  error?: string;
}

export interface FeedResponse extends ApiResponse<PostWithDetails[]> {}
export interface SignalsResponse extends ApiResponse<SignalWithDetails[]> {}
export interface NewsResponse extends ApiResponse<News[]> {}

// Form types
export interface CreatePostData {
  content: string;
  images?: string[];
  post_type: Post['post_type'];
  stock_symbols?: string[];
  hashtags?: string[];
  is_premium?: boolean;
}

export interface CreateSignalData {
  stock_symbol: string;
  signal_type: Signal['signal_type'];
  target_price?: number;
  stop_loss?: number;
  entry_price?: number;
  confidence_level: Signal['confidence_level'];
  time_horizon: Signal['time_horizon'];
  rationale?: string;
  expires_at?: string;
}

export interface UpdateProfileData {
  display_name?: string;
  bio?: string;
  avatar_url?: string;
  investment_style?: User['investment_style'];
  experience_level?: User['experience_level'];
}

// Filter and search types
export interface FeedFilters {
  post_type?: Post['post_type'];
  stock_symbols?: string[];
  following_only?: boolean;
  has_signals?: boolean;
  is_premium?: boolean;
}

export interface SignalFilters {
  signal_type?: Signal['signal_type'];
  stock_symbol?: string;
  status?: Signal['status'];
  time_horizon?: Signal['time_horizon'];
  confidence_level?: Signal['confidence_level'];
  influencer_id?: string;
}

export interface SearchFilters {
  query: string;
  type?: 'users' | 'posts' | 'stocks' | 'hashtags';
  stock_symbols?: string[];
  date_range?: {
    from: string;
    to: string;
  };
}