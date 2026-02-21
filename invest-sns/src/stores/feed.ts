import { create } from 'zustand';
import { PostWithDetails, FeedFilters } from '@/types/database';

interface FeedState {
  posts: PostWithDetails[];
  isLoading: boolean;
  hasMore: boolean;
  currentPage: number;
  filters: FeedFilters;
}

interface FeedActions {
  setPosts: (posts: PostWithDetails[]) => void;
  addPosts: (posts: PostWithDetails[]) => void;
  addPost: (post: PostWithDetails) => void;
  updatePost: (postId: string, updates: Partial<PostWithDetails>) => void;
  deletePost: (postId: string) => void;
  setLoading: (loading: boolean) => void;
  setHasMore: (hasMore: boolean) => void;
  setCurrentPage: (page: number) => void;
  setFilters: (filters: Partial<FeedFilters>) => void;
  resetFilters: () => void;
  loadFeed: (refresh?: boolean) => Promise<void>;
  loadMore: () => Promise<void>;
  toggleLike: (postId: string) => Promise<void>;
  createPost: (postData: any) => Promise<void>;
}

const defaultFilters: FeedFilters = {
  following_only: false,
  has_signals: false,
  is_premium: false,
};

export const useFeedStore = create<FeedState & FeedActions>((set, get) => ({
  // State
  posts: [],
  isLoading: false,
  hasMore: true,
  currentPage: 1,
  filters: defaultFilters,

  // Actions
  setPosts: (posts) => set({ posts }),

  addPosts: (newPosts) =>
    set((state) => ({
      posts: [...state.posts, ...newPosts],
    })),

  addPost: (post) =>
    set((state) => ({
      posts: [post, ...state.posts],
    })),

  updatePost: (postId, updates) =>
    set((state) => ({
      posts: state.posts.map((post) =>
        post.id === postId ? { ...post, ...updates } : post
      ),
    })),

  deletePost: (postId) =>
    set((state) => ({
      posts: state.posts.filter((post) => post.id !== postId),
    })),

  setLoading: (isLoading) => set({ isLoading }),

  setHasMore: (hasMore) => set({ hasMore }),

  setCurrentPage: (currentPage) => set({ currentPage }),

  setFilters: (filters) =>
    set((state) => ({
      filters: { ...state.filters, ...filters },
    })),

  resetFilters: () => set({ filters: defaultFilters }),

  loadFeed: async (refresh = false) => {
    const { isLoading, filters } = get();
    if (isLoading) return;

    set({ isLoading: true });

    try {
      // TODO: Implement API call
      console.log('Loading feed with filters:', filters);
      
      // Mock data for now
      const mockPosts: PostWithDetails[] = [
        {
          id: '1',
          author_id: 'user1',
          content: '삼성전자 목표가 상향 조정! 🚀 AI 반도체 수요 증가로 장기적으로 볼만한 종목입니다. #삼성전자 #AI반도체',
          images: [],
          post_type: 'analysis',
          stock_symbols: ['005930'],
          hashtags: ['삼성전자', 'AI반도체'],
          is_premium: false,
          likes_count: 124,
          comments_count: 23,
          shares_count: 8,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          author: {
            id: 'user1',
            email: 'investor@example.com',
            username: 'pro_investor',
            display_name: '프로투자자',
            avatar_url: '/avatars/1.jpg',
            bio: '10년차 개인투자자',
            is_verified: true,
            is_influencer: true,
            investment_style: 'moderate',
            experience_level: 'expert',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          comments: [],
          liked_by_user: false,
        },
        {
          id: '2',
          author_id: 'user2',
          content: '오늘 코스피 상승 마감! 📈 개인투자자 순매수세가 강했네요. 내일도 기대해봅시다.',
          images: ['/charts/kospi-daily.jpg'],
          post_type: 'general',
          stock_symbols: [],
          hashtags: ['코스피', '상승', '개인투자자'],
          is_premium: false,
          likes_count: 89,
          comments_count: 15,
          shares_count: 3,
          created_at: new Date(Date.now() - 3600000).toISOString(),
          updated_at: new Date(Date.now() - 3600000).toISOString(),
          author: {
            id: 'user2',
            email: 'trader@example.com',
            username: 'daily_trader',
            display_name: '데일리트레이더',
            avatar_url: '/avatars/2.jpg',
            bio: '단타 전문',
            is_verified: false,
            is_influencer: false,
            investment_style: 'aggressive',
            experience_level: 'intermediate',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          comments: [],
          liked_by_user: true,
        },
      ];

      if (refresh) {
        set({ posts: mockPosts, currentPage: 1, hasMore: true });
      } else {
        set((state) => ({
          posts: [...state.posts, ...mockPosts],
          currentPage: state.currentPage + 1,
        }));
      }
    } catch (error) {
      console.error('Error loading feed:', error);
    } finally {
      set({ isLoading: false });
    }
  },

  loadMore: async () => {
    const { hasMore, isLoading } = get();
    if (!hasMore || isLoading) return;

    await get().loadFeed(false);
  },

  toggleLike: async (postId) => {
    try {
      // TODO: Implement API call
      console.log('Toggling like for post:', postId);
      
      // Optimistic update
      set((state) => ({
        posts: state.posts.map((post) =>
          post.id === postId
            ? {
                ...post,
                liked_by_user: !post.liked_by_user,
                likes_count: post.liked_by_user
                  ? post.likes_count - 1
                  : post.likes_count + 1,
              }
            : post
        ),
      }));
    } catch (error) {
      console.error('Error toggling like:', error);
      // Revert optimistic update on error
    }
  },

  createPost: async (postData) => {
    try {
      // TODO: Implement API call
      console.log('Creating post:', postData);
      
      // Add to store after successful creation
      // const newPost = await api.createPost(postData);
      // get().addPost(newPost);
    } catch (error) {
      console.error('Error creating post:', error);
      throw error;
    }
  },
}));