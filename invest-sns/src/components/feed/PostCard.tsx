'use client';

import { useState } from 'react';
import { Heart, MessageCircle, Share2, MoreHorizontal, TrendingUp, TrendingDown } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { PostWithDetails } from '@/types/database';

interface PostCardProps {
  post: PostWithDetails;
  onLike: (postId: string) => void;
  onComment: (postId: string) => void;
  onShare: (postId: string) => void;
}

export default function PostCard({ post, onLike, onComment, onShare }: PostCardProps) {
  const [isLiking, setIsLiking] = useState(false);

  const handleLike = async () => {
    if (isLiking) return;
    setIsLiking(true);
    try {
      await onLike(post.id);
    } finally {
      setIsLiking(false);
    }
  };

  const getPostTypeColor = (type: string) => {
    switch (type) {
      case 'signal':
        return 'bg-green-100 text-green-800';
      case 'analysis':
        return 'bg-blue-100 text-blue-800';
      case 'news':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPostTypeLabel = (type: string) => {
    switch (type) {
      case 'signal':
        return '시그널';
      case 'analysis':
        return '분석';
      case 'news':
        return '뉴스';
      default:
        return '일반';
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return '방금 전';
    if (diffInMinutes < 60) return `${diffInMinutes}분 전`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}시간 전`;
    return `${Math.floor(diffInMinutes / 1440)}일 전`;
  };

  return (
    <Card className="w-full p-6 space-y-4 bg-white border border-gray-200 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Avatar className="w-10 h-10">
            <img 
              src={post.author.avatar_url || `/avatars/default.png`} 
              alt={post.author.display_name || post.author.username}
              className="w-full h-full object-cover rounded-full"
            />
          </Avatar>
          <div className="flex flex-col">
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-gray-900">
                {post.author.display_name || post.author.username}
              </span>
              {post.author.is_verified && (
                <div className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
              )}
              {post.author.is_influencer && (
                <Badge variant="secondary" className="text-xs">
                  인플루언서
                </Badge>
              )}
            </div>
            <span className="text-sm text-gray-500">@{post.author.username}</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge className={getPostTypeColor(post.post_type)}>
            {getPostTypeLabel(post.post_type)}
          </Badge>
          {post.is_premium && (
            <Badge className="bg-yellow-100 text-yellow-800">
              프리미엄
            </Badge>
          )}
          <span className="text-sm text-gray-500">
            {formatTimeAgo(post.created_at)}
          </span>
          <Button variant="ghost" size="sm">
            <MoreHorizontal className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-3">
        <p className="text-gray-900 leading-relaxed whitespace-pre-wrap">
          {post.content}
        </p>

        {/* Stock symbols */}
        {post.stock_symbols && post.stock_symbols.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {post.stock_symbols.map((symbol) => (
              <Badge 
                key={symbol} 
                variant="outline" 
                className="text-blue-600 border-blue-200 hover:bg-blue-50 cursor-pointer"
              >
                ${symbol}
              </Badge>
            ))}
          </div>
        )}

        {/* Hashtags */}
        {post.hashtags && post.hashtags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {post.hashtags.map((tag) => (
              <span key={tag} className="text-blue-500 hover:text-blue-700 cursor-pointer">
                #{tag}
              </span>
            ))}
          </div>
        )}

        {/* Images */}
        {post.images && post.images.length > 0 && (
          <div className="grid grid-cols-2 gap-2 mt-4">
            {post.images.map((image, index) => (
              <div key={index} className="relative overflow-hidden rounded-lg">
                <img 
                  src={image} 
                  alt={`Post image ${index + 1}`}
                  className="w-full h-48 object-cover hover:scale-105 transition-transform cursor-pointer"
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex items-center space-x-6">
          <Button 
            variant="ghost" 
            size="sm" 
            className={`flex items-center space-x-2 ${
              post.liked_by_user ? 'text-red-500 hover:text-red-600' : 'text-gray-500 hover:text-red-500'
            }`}
            onClick={handleLike}
            disabled={isLiking}
          >
            <Heart className={`w-5 h-5 ${post.liked_by_user ? 'fill-current' : ''}`} />
            <span>{post.likes_count}</span>
          </Button>

          <Button 
            variant="ghost" 
            size="sm" 
            className="flex items-center space-x-2 text-gray-500 hover:text-blue-500"
            onClick={() => onComment(post.id)}
          >
            <MessageCircle className="w-5 h-5" />
            <span>{post.comments_count}</span>
          </Button>

          <Button 
            variant="ghost" 
            size="sm" 
            className="flex items-center space-x-2 text-gray-500 hover:text-green-500"
            onClick={() => onShare(post.id)}
          >
            <Share2 className="w-5 h-5" />
            <span>{post.shares_count}</span>
          </Button>
        </div>

        {/* Performance indicator for signal posts */}
        {post.post_type === 'signal' && (
          <div className="flex items-center space-x-2">
            <div className="flex items-center text-green-600">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span className="text-sm font-medium">+12.5%</span>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}