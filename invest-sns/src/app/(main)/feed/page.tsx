'use client';

import { useState, useEffect } from 'react';
import { 
  Search, 
  Image as ImageIcon, 
  Smile, 
  Calendar, 
  MapPin, 
  Bold, 
  Italic, 
  MoreHorizontal,
  MessageCircle,
  Repeat2,
  Heart,
  BarChart3,
  Share,
  Bookmark,
  CheckCircle
} from 'lucide-react';
import { Avatar } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

// basePath 처리를 위한 헬퍼 함수
const getImagePath = (path: string) => {
  const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
  return `${basePath}${path}`;
};

// 더미 데이터
const dummyPosts = [
  {
    id: '1',
    author: {
      name: '박두환',
      handle: 'doohwan_park',
      avatar: getImagePath('/avatars/doohwan.jpg'),
      verified: true
    },
    content: '비트코인이 $45,000을 돌파했습니다! 다음 저항선은 $48,000 수준으로 보입니다. 단기 조정 가능성도 있으니 리스크 관리 잊지 마세요.',
    translation: 'Bitcoin has broken through $45,000! The next resistance level appears to be around $48,000.',
    timeAgo: '13시간',
    image: getImagePath('/charts/bitcoin-chart.jpg'),
    stats: {
      comments: 142,
      retweets: 89,
      likes: 1247,
      views: 15600
    }
  },
  {
    id: '2',
    author: {
      name: '이효석',
      handle: 'hyoseok_lee',
      avatar: getImagePath('/avatars/hyoseok.jpg'),
      verified: true
    },
    content: 'NVIDIA 실적 발표 앞두고 있는데, 반도체 섹터 전반적으로 긴장감이 돌고 있네요. AI 관련주들 움직임 주의깊게 봐야겠습니다 📊',
    timeAgo: '2시간',
    stats: {
      comments: 67,
      retweets: 134,
      likes: 892,
      views: 8945
    }
  },
  {
    id: '3',
    author: {
      name: '코린이 아빠',
      handle: 'korini_papa',
      avatar: getImagePath('/avatars/korini.jpg'),
      verified: true
    },
    content: '오늘 코스피 2,500선 터치했다가 다시 하락. 개인투자자들 매수 물량이 늘고 있는데 외국인 매도세가 여전히 강하네요. 당분간 박스권 예상 📈',
    timeAgo: '5시간',
    stats: {
      comments: 203,
      retweets: 156,
      likes: 2134,
      views: 23400
    }
  },
  {
    id: '4',
    author: {
      name: 'CryptoWhale',
      handle: 'crypto_whale_kr',
      avatar: getImagePath('/avatars/whale.jpg'),
      verified: false
    },
    content: '이더리움 스테이킹 수익률이 계속 하락 중이네요. DeFi 생태계 변화와 함께 수익 구조도 재편되고 있는 것 같습니다.',
    translation: 'Ethereum staking yield continues to decline. The profit structure seems to be restructuring along with DeFi ecosystem changes.',
    timeAgo: '8시간',
    stats: {
      comments: 89,
      retweets: 45,
      likes: 567,
      views: 4520
    }
  },
  {
    id: '5',
    author: {
      name: '주식왕',
      handle: 'stock_king_2024',
      avatar: getImagePath('/avatars/stock-king.jpg'),
      verified: false
    },
    content: '삼성전자 실적 시즌이 다가오고 있네요. 메모리 반도체 업황 회복 기대감이 커지고 있는데, 실제 실적이 어떻게 나올지 궁금합니다 🤔',
    timeAgo: '12시간',
    stats: {
      comments: 312,
      retweets: 78,
      likes: 1456,
      views: 18900
    }
  }
];

const trendingTopics = [
  { category: '태국에서 트렌드 중', topic: '#비트코인', posts: '84.2K 게시물' },
  { category: '비즈니스 · 트렌드 중', topic: '#NVIDIA실적', posts: '23.1K 게시물' },
  { category: '투자 · 트렌드 중', topic: '#코스피2500', posts: '15.7K 게시물' },
  { category: '크립토 · 트렌드 중', topic: '#이더리움스테이킹', posts: '9.8K 게시물' },
  { category: '트렌드 중', topic: '#삼성전자실적', posts: '7.2K 게시물' }
];

const suggestedFollows = [
  {
    name: '김작가',
    handle: 'writer_kim',
    avatar: getImagePath('/avatars/writer-kim.jpg'),
    verified: true,
    description: '투자 전문 작가'
  },
  {
    name: '부동산왕',
    handle: 'realestate_king',
    avatar: getImagePath('/avatars/realestate.jpg'),
    verified: false,
    description: '부동산 투자 전문가'
  },
  {
    name: '퀀트투자',
    handle: 'quant_invest',
    avatar: getImagePath('/avatars/quant.jpg'),
    verified: true,
    description: '퀀트 투자 연구소'
  }
];

interface PostProps {
  post: typeof dummyPosts[0];
}

function XPost({ post }: PostProps) {
  const [liked, setLiked] = useState(false);
  const [retweeted, setRetweeted] = useState(false);

  return (
    <article className="px-4 py-3 border-b border-[#eff3f4] hover:bg-gray-50/50 transition-colors cursor-pointer">
      <div className="flex space-x-3">
        <Avatar className="w-10 h-10 flex-shrink-0">
          <img 
            src={post.author.avatar || getImagePath('/avatars/default.jpg')} 
            alt={post.author.name}
            className="w-full h-full object-cover rounded-full"
          />
        </Avatar>
        
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center space-x-1 mb-1">
            <span className="font-bold text-[#0f1419] hover:underline cursor-pointer">
              {post.author.name}
            </span>
            {post.author.verified && (
              <CheckCircle className="w-5 h-5 text-[#1d9bf0]" fill="currentColor" />
            )}
            <span className="text-[#536471]">@{post.author.handle}</span>
            <span className="text-[#536471]">·</span>
            <span className="text-[#536471] hover:underline cursor-pointer">
              {post.timeAgo}
            </span>
            <div className="ml-auto">
              <Button variant="ghost" size="sm" className="w-8 h-8 p-0 text-[#536471] hover:bg-gray-100">
                <MoreHorizontal className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Content */}
          <div className="mb-3">
            <p className="text-[#0f1419] text-[15px] leading-5 whitespace-pre-wrap">
              {post.content}
            </p>
            {post.translation && (
              <p className="text-[#1d9bf0] text-[15px] mt-2">
                {post.translation}
              </p>
            )}
          </div>

          {/* Image */}
          {post.image && (
            <div className="mb-3 rounded-2xl overflow-hidden border border-[#eff3f4]">
              <img 
                src={post.image || getImagePath('/images/chart-placeholder.jpg')} 
                alt="Post image"
                className="w-full h-64 object-cover"
              />
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between max-w-md mt-2">
            <Button 
              variant="ghost" 
              size="sm" 
              className="flex items-center space-x-1 text-[#536471] hover:text-[#1d9bf0] hover:bg-[#1d9bf0]/10 p-2 rounded-full group"
            >
              <div className="p-2 rounded-full group-hover:bg-[#1d9bf0]/10">
                <MessageCircle className="w-4 h-4" />
              </div>
              <span className="text-sm">{post.stats.comments}</span>
            </Button>

            <Button 
              variant="ghost" 
              size="sm" 
              className={`flex items-center space-x-1 p-2 rounded-full group ${
                retweeted 
                  ? 'text-green-600' 
                  : 'text-[#536471] hover:text-green-600 hover:bg-green-600/10'
              }`}
              onClick={() => setRetweeted(!retweeted)}
            >
              <div className="p-2 rounded-full group-hover:bg-green-600/10">
                <Repeat2 className="w-4 h-4" />
              </div>
              <span className="text-sm">{post.stats.retweets}</span>
            </Button>

            <Button 
              variant="ghost" 
              size="sm" 
              className={`flex items-center space-x-1 p-2 rounded-full group ${
                liked 
                  ? 'text-red-600' 
                  : 'text-[#536471] hover:text-red-600 hover:bg-red-600/10'
              }`}
              onClick={() => setLiked(!liked)}
            >
              <div className="p-2 rounded-full group-hover:bg-red-600/10">
                <Heart className={`w-4 h-4 ${liked ? 'fill-current' : ''}`} />
              </div>
              <span className="text-sm">{liked ? post.stats.likes + 1 : post.stats.likes}</span>
            </Button>

            <Button 
              variant="ghost" 
              size="sm" 
              className="flex items-center space-x-1 text-[#536471] hover:text-[#1d9bf0] hover:bg-[#1d9bf0]/10 p-2 rounded-full group"
            >
              <div className="p-2 rounded-full group-hover:bg-[#1d9bf0]/10">
                <BarChart3 className="w-4 h-4" />
              </div>
              <span className="text-sm">{post.stats.views}</span>
            </Button>

            <div className="flex items-center space-x-1">
              <Button 
                variant="ghost" 
                size="sm" 
                className="w-8 h-8 p-0 text-[#536471] hover:text-[#1d9bf0] hover:bg-[#1d9bf0]/10 rounded-full"
              >
                <Bookmark className="w-4 h-4" />
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                className="w-8 h-8 p-0 text-[#536471] hover:text-[#1d9bf0] hover:bg-[#1d9bf0]/10 rounded-full"
              >
                <Share className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </article>
  );
}

function TrendingSection() {
  return (
    <div className="bg-[#f7f9fa] rounded-2xl p-4 mb-4">
      <h2 className="text-xl font-bold text-[#0f1419] mb-4">무슨 일이 일어나고 있나요?</h2>
      <div className="space-y-3">
        {trendingTopics.map((trend, index) => (
          <div key={index} className="hover:bg-gray-100 p-2 -m-2 rounded cursor-pointer transition-colors">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[#536471] text-sm">{trend.category}</p>
                <p className="font-bold text-[#0f1419]">{trend.topic}</p>
                <p className="text-[#536471] text-sm">{trend.posts}</p>
              </div>
              <Button variant="ghost" size="sm" className="w-8 h-8 p-0 text-[#536471]">
                <MoreHorizontal className="w-4 h-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>
      <button className="text-[#1d9bf0] text-sm hover:underline mt-3">더 보기</button>
    </div>
  );
}

function SuggestedFollows() {
  return (
    <div className="bg-[#f7f9fa] rounded-2xl p-4 mb-4">
      <h2 className="text-xl font-bold text-[#0f1419] mb-4">팔로우할 계정</h2>
      <div className="space-y-3">
        {suggestedFollows.map((user, index) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Avatar className="w-10 h-10">
                <img 
                  src={user.avatar || getImagePath('/avatars/default.jpg')} 
                  alt={user.name}
                  className="w-full h-full object-cover rounded-full"
                />
              </Avatar>
              <div>
                <div className="flex items-center space-x-1">
                  <span className="font-bold text-[#0f1419] text-sm">{user.name}</span>
                  {user.verified && (
                    <CheckCircle className="w-4 h-4 text-[#1d9bf0]" fill="currentColor" />
                  )}
                </div>
                <p className="text-[#536471] text-sm">@{user.handle}</p>
              </div>
            </div>
            <Button 
              className="bg-[#0f1419] text-white hover:bg-[#272c30] px-4 py-1 h-8 rounded-full font-bold text-sm"
            >
              팔로우
            </Button>
          </div>
        ))}
      </div>
      <button className="text-[#1d9bf0] text-sm hover:underline mt-3">더 보기</button>
    </div>
  );
}

export default function FeedPage() {
  const [newPostCount, setNewPostCount] = useState(70);
  
  return (
    <div className="max-w-6xl mx-auto bg-white min-h-screen">
      <div className="flex">
        {/* Main Content */}
        <main className="flex-1 max-w-2xl border-x border-[#eff3f4]">
          {/* Header Tabs */}
          <div className="sticky top-0 bg-white/80 backdrop-blur z-10 border-b border-[#eff3f4]">
            <div className="flex">
              <button className="flex-1 py-4 px-4 text-[#0f1419] font-bold border-b-2 border-[#1d9bf0] hover:bg-gray-50">
                추천
              </button>
              <button className="flex-1 py-4 px-4 text-[#536471] font-bold hover:bg-gray-50">
                팔로잉
              </button>
              <button className="flex-1 py-4 px-4 text-[#536471] font-bold hover:bg-gray-50">
                구독중
              </button>
            </div>
          </div>

          {/* Compose Tweet */}
          <div className="border-b border-[#eff3f4] p-4">
            <div className="flex space-x-3">
              <Avatar className="w-10 h-10">
                <img 
                  src={getImagePath("/avatars/me.jpg")} 
                  alt="Your avatar"
                  className="w-full h-full object-cover rounded-full"
                />
              </Avatar>
              <div className="flex-1">
                <div className="mb-3">
                  <Input
                    placeholder="무슨 일이 일어나고 있나요?"
                    className="border-0 text-xl placeholder-[#536471] p-0 focus:ring-0 resize-none"
                    style={{ boxShadow: 'none' }}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <Button variant="ghost" size="sm" className="w-9 h-9 p-0 text-[#1d9bf0] hover:bg-[#1d9bf0]/10">
                      <ImageIcon className="w-5 h-5" />
                    </Button>
                    <Button variant="ghost" size="sm" className="w-9 h-9 p-0 text-[#1d9bf0] hover:bg-[#1d9bf0]/10">
                      <span className="text-sm font-bold">GIF</span>
                    </Button>
                    <Button variant="ghost" size="sm" className="w-9 h-9 p-0 text-[#1d9bf0] hover:bg-[#1d9bf0]/10">
                      <span className="text-sm font-bold">📊</span>
                    </Button>
                    <Button variant="ghost" size="sm" className="w-9 h-9 p-0 text-[#1d9bf0] hover:bg-[#1d9bf0]/10">
                      <Smile className="w-5 h-5" />
                    </Button>
                    <Button variant="ghost" size="sm" className="w-9 h-9 p-0 text-[#1d9bf0] hover:bg-[#1d9bf0]/10">
                      <Calendar className="w-5 h-5" />
                    </Button>
                    <Button variant="ghost" size="sm" className="w-9 h-9 p-0 text-[#1d9bf0] hover:bg-[#1d9bf0]/10">
                      <MapPin className="w-5 h-5" />
                    </Button>
                    <div className="w-px h-6 bg-[#eff3f4] mx-2"></div>
                    <Button variant="ghost" size="sm" className="w-9 h-9 p-0 text-[#1d9bf0] hover:bg-[#1d9bf0]/10">
                      <Bold className="w-5 h-5" />
                    </Button>
                    <Button variant="ghost" size="sm" className="w-9 h-9 p-0 text-[#1d9bf0] hover:bg-[#1d9bf0]/10">
                      <Italic className="w-5 h-5" />
                    </Button>
                  </div>
                  <Button className="bg-[#1d9bf0] text-white hover:bg-[#1a8cd8] px-6 py-1.5 h-9 rounded-full font-bold">
                    게시하기
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* New Posts Notification */}
          <div className="border-b border-[#eff3f4] p-3 text-center hover:bg-gray-50 cursor-pointer transition-colors">
            <span className="text-[#1d9bf0] text-sm font-medium">
              {newPostCount} 게시물 보기
            </span>
          </div>

          {/* Feed */}
          <div>
            {dummyPosts.map((post) => (
              <XPost key={post.id} post={post} />
            ))}
          </div>
        </main>

        {/* Right Sidebar - Desktop only */}
        <aside className="w-80 p-4 hidden lg:block">
          {/* Search */}
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-[#536471]" />
              <Input
                placeholder="검색"
                className="pl-12 bg-[#f7f9fa] border-[#f7f9fa] rounded-full h-11 focus:bg-white focus:border-[#1d9bf0]"
              />
            </div>
          </div>

          <TrendingSection />
          <SuggestedFollows />

          {/* Footer Links */}
          <div className="text-[#536471] text-sm space-y-1">
            <div className="flex flex-wrap gap-x-3 gap-y-1">
              <a href="#" className="hover:underline">이용약관</a>
              <a href="#" className="hover:underline">개인정보 처리방침</a>
              <a href="#" className="hover:underline">쿠키 정책</a>
              <a href="#" className="hover:underline">접근성</a>
              <a href="#" className="hover:underline">광고 정보</a>
            </div>
            <div className="flex flex-wrap gap-x-3 gap-y-1">
              <a href="#" className="hover:underline">더 보기</a>
              <span>© 2026 InvestSNS.</span>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}