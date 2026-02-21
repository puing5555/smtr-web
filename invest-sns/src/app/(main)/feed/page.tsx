'use client';

import { useEffect } from 'react';
import { Plus, Filter, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import PostCard from '@/components/feed/PostCard';
import { useFeedStore } from '@/stores/feed';

export default function FeedPage() {
  const { 
    posts, 
    isLoading, 
    hasMore, 
    filters,
    loadFeed, 
    loadMore, 
    toggleLike,
    setFilters 
  } = useFeedStore();

  useEffect(() => {
    loadFeed(true);
  }, []);

  const handleLike = async (postId: string) => {
    await toggleLike(postId);
  };

  const handleComment = (postId: string) => {
    console.log('Comment on post:', postId);
    // TODO: Navigate to post detail or open comment modal
  };

  const handleShare = (postId: string) => {
    console.log('Share post:', postId);
    // TODO: Implement share functionality
  };

  const handleFilterChange = (newFilters: any) => {
    setFilters(newFilters);
    loadFeed(true);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">투자 피드</h1>
          <p className="text-gray-600 mt-1">
            인플루언서들의 최신 투자 인사이트를 확인해보세요
          </p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Plus className="w-4 h-4 mr-2" />
          글 작성
        </Button>
      </div>

      {/* Tabs and Filters */}
      <div className="space-y-4">
        <Tabs defaultValue="all" className="w-full">
          <div className="flex items-center justify-between">
            <TabsList className="grid w-full grid-cols-4 lg:w-auto">
              <TabsTrigger 
                value="all" 
                onClick={() => handleFilterChange({})}
              >
                전체
              </TabsTrigger>
              <TabsTrigger 
                value="following"
                onClick={() => handleFilterChange({ following_only: true })}
              >
                팔로잉
              </TabsTrigger>
              <TabsTrigger 
                value="signals"
                onClick={() => handleFilterChange({ has_signals: true })}
              >
                시그널
              </TabsTrigger>
              <TabsTrigger 
                value="premium"
                onClick={() => handleFilterChange({ is_premium: true })}
              >
                프리미엄
              </TabsTrigger>
            </TabsList>

            <Button variant="outline" size="sm">
              <Filter className="w-4 h-4 mr-2" />
              필터
            </Button>
          </div>

          {/* Active Filters */}
          {(filters.stock_symbols?.length || filters.post_type) && (
            <div className="flex flex-wrap gap-2">
              {filters.stock_symbols?.map((symbol) => (
                <Badge key={symbol} variant="secondary">
                  {symbol}
                </Badge>
              ))}
              {filters.post_type && (
                <Badge variant="secondary">
                  {filters.post_type}
                </Badge>
              )}
            </div>
          )}

          <TabsContent value="all" className="mt-6">
            <FeedContent 
              posts={posts}
              isLoading={isLoading}
              hasMore={hasMore}
              onLike={handleLike}
              onComment={handleComment}
              onShare={handleShare}
              onLoadMore={loadMore}
            />
          </TabsContent>

          <TabsContent value="following" className="mt-6">
            <FeedContent 
              posts={posts}
              isLoading={isLoading}
              hasMore={hasMore}
              onLike={handleLike}
              onComment={handleComment}
              onShare={handleShare}
              onLoadMore={loadMore}
            />
          </TabsContent>

          <TabsContent value="signals" className="mt-6">
            <FeedContent 
              posts={posts}
              isLoading={isLoading}
              hasMore={hasMore}
              onLike={handleLike}
              onComment={handleComment}
              onShare={handleShare}
              onLoadMore={loadMore}
            />
          </TabsContent>

          <TabsContent value="premium" className="mt-6">
            <FeedContent 
              posts={posts}
              isLoading={isLoading}
              hasMore={hasMore}
              onLike={handleLike}
              onComment={handleComment}
              onShare={handleShare}
              onLoadMore={loadMore}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

interface FeedContentProps {
  posts: any[];
  isLoading: boolean;
  hasMore: boolean;
  onLike: (postId: string) => void;
  onComment: (postId: string) => void;
  onShare: (postId: string) => void;
  onLoadMore: () => void;
}

function FeedContent({ 
  posts, 
  isLoading, 
  hasMore, 
  onLike, 
  onComment, 
  onShare, 
  onLoadMore 
}: FeedContentProps) {
  return (
    <div className="space-y-6">
      {/* Market Summary Card */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
        <h3 className="text-lg font-semibold mb-3">오늘의 시장 동향</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <TrendingUp className="w-4 h-4 mr-1 text-green-300" />
              <span className="text-sm opacity-90">코스피</span>
            </div>
            <div className="font-bold">2,485.67</div>
            <div className="text-sm text-green-300">+1.24%</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <TrendingUp className="w-4 h-4 mr-1 text-green-300" />
              <span className="text-sm opacity-90">코스닥</span>
            </div>
            <div className="font-bold">736.82</div>
            <div className="text-sm text-green-300">+0.87%</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <span className="text-sm opacity-90">달러</span>
            </div>
            <div className="font-bold">1,340</div>
            <div className="text-sm text-red-300">-0.45%</div>
          </div>
        </div>
      </div>

      {/* Posts */}
      {posts.length === 0 && !isLoading ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <TrendingUp className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">아직 게시물이 없습니다</h3>
          <p className="text-gray-500">
            첫 번째 게시물을 작성하거나 다른 사용자를 팔로우해보세요.
          </p>
          <Button className="mt-4 bg-blue-600 hover:bg-blue-700">
            <Plus className="w-4 h-4 mr-2" />
            첫 게시물 작성하기
          </Button>
        </div>
      ) : (
        <div className="space-y-6">
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onLike={onLike}
              onComment={onComment}
              onShare={onShare}
            />
          ))}
        </div>
      )}

      {/* Load More */}
      {hasMore && (
        <div className="text-center">
          <Button 
            variant="outline" 
            onClick={onLoadMore}
            disabled={isLoading}
          >
            {isLoading ? '로딩 중...' : '더 보기'}
          </Button>
        </div>
      )}

      {/* Loading skeleton */}
      {isLoading && (
        <div className="space-y-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-lg p-6 space-y-4 animate-pulse">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                <div className="space-y-2 flex-1">
                  <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/6"></div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
              <div className="h-8 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}