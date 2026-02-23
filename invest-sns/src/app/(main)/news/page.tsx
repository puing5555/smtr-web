'use client';

import { useEffect, useState } from 'react';
import { Search, Filter, RefreshCw, ExternalLink, Newspaper, FileText, Calendar, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface Filing {
  id: number;
  time: string;
  grade: string;
  grade_icon: string;
  corp_name: string;
  report_name: string;
  ai_summary?: string;
  dart_url: string;
  receipt_date: string;
  stock_code?: string;
}

interface FilingsResponse {
  success: boolean;
  filings: Filing[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

interface NewsItem {
  id: number;
  title: string;
  summary: string;
  source: string;
  published_at: string;
  url: string;
  category: string;
  ai_summary?: string;
  stock_codes?: string[];
}

interface NewsResponse {
  success: boolean;
  news: NewsItem[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export default function NewsPage() {
  const [activeTab, setActiveTab] = useState('filings');
  
  // 공시 상태
  const [filings, setFilings] = useState<Filing[]>([]);
  const [isLoadingFilings, setIsLoadingFilings] = useState(false);
  const [filingsFilter, setFilingsFilter] = useState<'all' | 'A' | 'B'>('all');
  const [filingsPage, setFilingsPage] = useState(1);
  const [hasMoreFilings, setHasMoreFilings] = useState(true);
  const [filingsError, setFilingsError] = useState<string | null>(null);
  
  // 뉴스 상태  
  const [news, setNews] = useState<NewsItem[]>([]);
  const [isLoadingNews, setIsLoadingNews] = useState(false);
  const [newsFilter, setNewsFilter] = useState<'all' | 'market' | 'stock' | 'economy'>('all');
  const [newsPage, setNewsPage] = useState(1);
  const [hasMoreNews, setHasMoreNews] = useState(true);
  const [newsError, setNewsError] = useState<string | null>(null);
  
  // 공통 상태
  const [searchQuery, setSearchQuery] = useState('');

  // 공시 데이터 로드
  const loadFilings = async (reset: boolean = false, loadPage: number = 1) => {
    if (isLoadingFilings) return;
    
    setIsLoadingFilings(true);
    setFilingsError(null);

    try {
      const params = new URLSearchParams({
        page: loadPage.toString(),
        limit: '10'
      });

      if (filingsFilter !== 'all') {
        params.append('grade', filingsFilter);
      }

      if (searchQuery.trim()) {
        params.append('search', searchQuery.trim());
      }

      const response = await fetch(`http://localhost:8000/api/filings?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: FilingsResponse = await response.json();

      if (reset) {
        setFilings(data.filings);
      } else {
        setFilings(prev => [...prev, ...data.filings]);
      }

      setHasMoreFilings(data.pagination.has_next);
      setFilingsPage(loadPage);
    } catch (error) {
      console.error('Failed to load filings:', error);
      setFilingsError('공시 데이터를 불러올 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.');
    } finally {
      setIsLoadingFilings(false);
    }
  };

  // 뉴스 데이터 로드 (더미 데이터 포함)
  const loadNews = async (reset: boolean = false, loadPage: number = 1) => {
    if (isLoadingNews) return;
    
    setIsLoadingNews(true);
    setNewsError(null);

    try {
      const params = new URLSearchParams({
        page: loadPage.toString(),
        limit: '10'
      });

      if (newsFilter !== 'all') {
        params.append('category', newsFilter);
      }

      if (searchQuery.trim()) {
        params.append('search', searchQuery.trim());
      }

      let data: NewsResponse;
      
      try {
        const response = await fetch(`http://localhost:8000/api/news?${params}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          data = await response.json();
        } else {
          throw new Error('Backend not available');
        }
      } catch {
        // 백엔드 실패시 더미 데이터 사용
        data = generateDummyNews(loadPage, newsFilter, searchQuery.trim());
      }

      if (reset) {
        setNews(data.news);
      } else {
        setNews(prev => [...prev, ...data.news]);
      }

      setHasMoreNews(data.pagination.has_next);
      setNewsPage(loadPage);
    } catch (error) {
      console.error('Failed to load news:', error);
      setNewsError('뉴스 데이터를 불러올 수 없습니다.');
    } finally {
      setIsLoadingNews(false);
    }
  };

  // 더미 뉴스 생성
  const generateDummyNews = (page: number, filter: string, search: string): NewsResponse => {
    const dummyNewsItems: NewsItem[] = [
      {
        id: 1,
        title: '코스피, 장중 3000선 회복...외국인 순매수 지속',
        summary: '코스피가 장중 3000선을 회복하며 상승세를 보이고 있습니다. 외국인 투자자들의 순매수가 이어지고 있어 상승 모멘텀이 지속될 것으로 전망됩니다.',
        source: '한국경제',
        published_at: '2026-02-23 13:30',
        url: 'https://example.com/news/1',
        category: 'market',
        ai_summary: '코스피 3000선 회복, 외국인 순매수로 상승 모멘텀 지속 전망',
        stock_codes: ['005930', '000660']
      },
      {
        id: 2,
        title: '삼성전자, 차세대 반도체 기술 개발 성공 발표',
        summary: '삼성전자가 3나노 공정 기술 개발에 성공했다고 발표했습니다. 이로써 글로벌 반도체 시장에서의 경쟁력이 더욱 강화될 것으로 예상됩니다.',
        source: '전자신문',
        published_at: '2026-02-23 12:45',
        url: 'https://example.com/news/2',
        category: 'stock',
        ai_summary: '삼성전자 3나노 공정 기술 개발 성공, 글로벌 반도체 경쟁력 강화 기대',
        stock_codes: ['005930']
      },
      {
        id: 3,
        title: '한국은행, 기준금리 동결 결정...경기 회복세 주목',
        summary: '한국은행이 기준금리를 현행 3.5%로 동결하기로 결정했습니다. 최근 경기 회복세와 인플레이션 안정화를 종합적으로 고려한 결정으로 분석됩니다.',
        source: '연합뉴스',
        published_at: '2026-02-23 11:20',
        url: 'https://example.com/news/3',
        category: 'economy',
        ai_summary: '한은 기준금리 3.5% 동결, 경기 회복세와 인플레이션 안정화 고려',
        stock_codes: []
      },
      {
        id: 4,
        title: 'SK하이닉스, AI 메모리 반도체 수요 급증으로 실적 개선',
        summary: 'SK하이닉스가 AI 열풍으로 인한 고대역폭 메모리(HBM) 수요 급증에 힘입어 실적 개선이 지속되고 있다고 발표했습니다.',
        source: '매일경제',
        published_at: '2026-02-23 10:15',
        url: 'https://example.com/news/4',
        category: 'stock',
        ai_summary: 'SK하이닉스, AI 메모리 반도체 수요 급증으로 실적 개선 지속',
        stock_codes: ['000660']
      },
      {
        id: 5,
        title: 'K-뷰티 기업들, 중국 시장 재진출 본격화',
        summary: '국내 화장품 기업들이 중국 시장 재진출에 속도를 내고 있습니다. 규제 완화와 한류 열풍 재점화가 주요 배경으로 분석됩니다.',
        source: '파이낸셜뉴스',
        published_at: '2026-02-23 09:30',
        url: 'https://example.com/news/5',
        category: 'market',
        ai_summary: 'K-뷰티 기업 중국 재진출 본격화, 규제 완화와 한류 재점화 배경',
        stock_codes: ['090430', '002790']
      }
    ];

    // 필터링 로직
    let filteredNews = dummyNewsItems;
    if (filter !== 'all') {
      filteredNews = filteredNews.filter(item => item.category === filter);
    }
    if (search) {
      filteredNews = filteredNews.filter(item => 
        item.title.toLowerCase().includes(search.toLowerCase()) ||
        item.summary.toLowerCase().includes(search.toLowerCase())
      );
    }

    // 페이징 적용
    const startIndex = (page - 1) * 10;
    const endIndex = startIndex + 10;
    const paginatedNews = filteredNews.slice(startIndex, endIndex);

    return {
      success: true,
      news: paginatedNews,
      pagination: {
        page,
        limit: 10,
        total: filteredNews.length,
        pages: Math.ceil(filteredNews.length / 10),
        has_next: endIndex < filteredNews.length,
        has_prev: page > 1
      }
    };
  };

  // 초기 로드
  useEffect(() => {
    if (activeTab === 'filings') {
      setFilingsPage(1);
      loadFilings(true);
    } else if (activeTab === 'news') {
      setNewsPage(1);
      loadNews(true);
    }
  }, [activeTab, filingsFilter, newsFilter, searchQuery]);

  // 더보기 핸들러
  const handleLoadMoreFilings = () => {
    if (hasMoreFilings && !isLoadingFilings) {
      loadFilings(false, filingsPage + 1);
    }
  };

  const handleLoadMoreNews = () => {
    if (hasMoreNews && !isLoadingNews) {
      loadNews(false, newsPage + 1);
    }
  };

  // 새로고침 핸들러
  const handleRefresh = () => {
    if (activeTab === 'filings') {
      setFilingsPage(1);
      loadFilings(true);
    } else if (activeTab === 'news') {
      setNewsPage(1);  
      loadNews(true);
    }
  };

  // 검색 핸들러
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeTab === 'filings') {
      setFilingsPage(1);
      loadFilings(true);
    } else if (activeTab === 'news') {
      setNewsPage(1);
      loadNews(true);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">뉴스 & 공시</h1>
          <p className="text-gray-600 mt-1">
            최신 뉴스와 공시 정보를 한눈에 확인하세요
          </p>
        </div>
        <div className="flex items-center gap-3">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="검색..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 w-64"
              />
            </div>
            <Button type="submit" variant="outline" size="sm">
              <Search className="w-4 h-4" />
            </Button>
          </form>
          <Button
            onClick={handleRefresh}
            disabled={isLoadingFilings || isLoadingNews}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${(isLoadingFilings || isLoadingNews) ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">총 공시</p>
              <p className="text-2xl font-bold text-gray-900">{filings.length}</p>
            </div>
            <FileText className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">A등급 공시</p>
              <p className="text-2xl font-bold text-gray-900">
                {filings.filter(f => f.grade === 'A').length}
              </p>
            </div>
            <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
              <span className="text-green-600 font-bold">A</span>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">총 뉴스</p>
              <p className="text-2xl font-bold text-gray-900">{news.length}</p>
            </div>
            <Newspaper className="w-8 h-8 text-purple-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">오늘 업데이트</p>
              <p className="text-2xl font-bold text-gray-900">
                {filings.filter(f => f.receipt_date === '2026-02-23').length + news.length}
              </p>
            </div>
            <Calendar className="w-8 h-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="filings">공시</TabsTrigger>
          <TabsTrigger value="news">뉴스</TabsTrigger>
        </TabsList>

        <TabsContent value="filings" className="mt-6">
          <div className="space-y-6">
            {/* 공시 필터 */}
            <div className="flex flex-wrap gap-2">
              <Button
                variant={filingsFilter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilingsFilter('all')}
              >
                전체
              </Button>
              <Button
                variant={filingsFilter === 'A' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilingsFilter('A')}
                className={filingsFilter === 'A' ? 'bg-green-600 hover:bg-green-700' : ''}
              >
                📊 A등급
              </Button>
              <Button
                variant={filingsFilter === 'B' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilingsFilter('B')}
                className={filingsFilter === 'B' ? 'bg-yellow-600 hover:bg-yellow-700' : ''}
              >
                🔔 B등급
              </Button>
            </div>

            {/* 에러 메시지 */}
            {filingsError && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {filingsError}
              </div>
            )}

            {/* 공시 목록 */}
            {filings.length === 0 && !isLoadingFilings ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FileText className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-500 mb-2">공시 데이터가 없습니다</h3>
                <p className="text-gray-400">검색 조건을 변경하거나 잠시 후 다시 시도해보세요.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filings.map((filing) => (
                  <FilingCard key={filing.id} filing={filing} />
                ))}
              </div>
            )}

            {/* 더보기 버튼 */}
            {hasMoreFilings && !filingsError && (
              <div className="text-center mt-6">
                <Button 
                  onClick={handleLoadMoreFilings}
                  disabled={isLoadingFilings}
                  variant="outline"
                >
                  {isLoadingFilings ? '로딩 중...' : '더 보기'}
                </Button>
              </div>
            )}

            {/* 로딩 스켈레톤 */}
            {isLoadingFilings && filings.length === 0 && <LoadingSkeleton />}
          </div>
        </TabsContent>

        <TabsContent value="news" className="mt-6">
          <div className="space-y-6">
            {/* 뉴스 필터 */}
            <div className="flex flex-wrap gap-2">
              <Button
                variant={newsFilter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setNewsFilter('all')}
              >
                전체
              </Button>
              <Button
                variant={newsFilter === 'market' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setNewsFilter('market')}
              >
                📈 시장
              </Button>
              <Button
                variant={newsFilter === 'stock' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setNewsFilter('stock')}
              >
                🏢 종목
              </Button>
              <Button
                variant={newsFilter === 'economy' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setNewsFilter('economy')}
              >
                💰 경제
              </Button>
            </div>

            {/* 에러 메시지 */}
            {newsError && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {newsError}
              </div>
            )}

            {/* 뉴스 목록 */}
            {news.length === 0 && !isLoadingNews ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Newspaper className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-500 mb-2">뉴스 데이터가 없습니다</h3>
                <p className="text-gray-400">검색 조건을 변경하거나 잠시 후 다시 시도해보세요.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {news.map((item) => (
                  <NewsCard key={item.id} news={item} />
                ))}
              </div>
            )}

            {/* 더보기 버튼 */}
            {hasMoreNews && !newsError && (
              <div className="text-center mt-6">
                <Button 
                  onClick={handleLoadMoreNews}
                  disabled={isLoadingNews}
                  variant="outline"
                >
                  {isLoadingNews ? '로딩 중...' : '더 보기'}
                </Button>
              </div>
            )}

            {/* 로딩 스켈레톤 */}
            {isLoadingNews && news.length === 0 && <LoadingSkeleton />}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// 공시 카드 컴포넌트
interface FilingCardProps {
  filing: Filing;
}

function FilingCard({ filing }: FilingCardProps) {
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'bg-green-50 text-green-700 border-green-200';
      case 'B': return 'bg-yellow-50 text-yellow-700 border-yellow-200';
      default: return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="bg-white rounded-lg p-6 hover:shadow-md transition-shadow border border-gray-200">
      <div className="flex items-start space-x-4">
        {/* Time */}
        <div className="text-xs text-gray-500 font-mono min-w-[3rem]">
          {filing.time}
        </div>

        {/* Grade Icon */}
        <div className="text-xl">
          {filing.grade_icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="font-semibold text-gray-900 truncate">
              {filing.corp_name}
            </h3>
            <Badge 
              variant="outline" 
              className={`text-xs ${getGradeColor(filing.grade)}`}
            >
              {filing.grade}등급
            </Badge>
            {filing.stock_code && (
              <Badge variant="secondary" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
                {filing.stock_code}
              </Badge>
            )}
          </div>

          <p className="text-gray-700 text-sm mb-3 leading-relaxed">
            {filing.report_name}
          </p>

          {filing.ai_summary && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
              <div className="text-xs text-blue-600 font-medium mb-1">🤖 AI 요약</div>
              <p className="text-sm text-blue-800 leading-relaxed">
                {filing.ai_summary}
              </p>
            </div>
          )}
        </div>

        {/* DART Link */}
        <div className="flex-shrink-0">
          <Button
            onClick={() => window.open(filing.dart_url, '_blank')}
            size="sm"
            variant="outline"
            className="text-xs"
          >
            <ExternalLink className="w-3 h-3 mr-1" />
            DART
          </Button>
        </div>
      </div>
    </div>
  );
}

// 뉴스 카드 컴포넌트
interface NewsCardProps {
  news: NewsItem;
}

function NewsCard({ news }: NewsCardProps) {
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'market': return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'stock': return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'economy': return 'bg-orange-50 text-orange-700 border-orange-200';
      default: return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'market': return '시장';
      case 'stock': return '종목'; 
      case 'economy': return '경제';
      default: return '기타';
    }
  };

  return (
    <div className="bg-white rounded-lg p-6 hover:shadow-md transition-shadow border border-gray-200">
      <div className="flex items-start space-x-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <Badge 
              variant="outline" 
              className={`text-xs ${getCategoryColor(news.category)}`}
            >
              {getCategoryLabel(news.category)}
            </Badge>
            <span className="text-sm text-gray-500">{news.source}</span>
            <span className="text-sm text-gray-500">{news.published_at}</span>
          </div>

          <h3 className="font-semibold text-gray-900 mb-2 leading-tight">
            {news.title}
          </h3>
          
          <p className="text-gray-700 text-sm mb-3 leading-relaxed">
            {news.summary}
          </p>

          {news.ai_summary && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-3">
              <div className="text-xs text-green-600 font-medium mb-1">🤖 AI 요약</div>
              <p className="text-sm text-green-800 leading-relaxed">
                {news.ai_summary}
              </p>
            </div>
          )}

          {news.stock_codes && news.stock_codes.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {news.stock_codes.map((code) => (
                <Badge key={code} variant="secondary" className="text-xs">
                  {code}
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* External Link */}
        <div className="flex-shrink-0">
          <Button
            onClick={() => window.open(news.url, '_blank')}
            size="sm"
            variant="outline"
            className="text-xs"
          >
            <ExternalLink className="w-3 h-3 mr-1" />
            원문
          </Button>
        </div>
      </div>
    </div>
  );
}

// 로딩 스켈레톤 컴포넌트
function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="bg-white rounded-lg p-6 border border-gray-200 animate-pulse">
          <div className="flex items-start space-x-4">
            <div className="w-8 h-8 bg-gray-200 rounded"></div>
            <div className="flex-1 space-y-3">
              <div className="h-5 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-4 bg-gray-200 rounded w-full"></div>
            </div>
            <div className="w-16 h-8 bg-gray-200 rounded"></div>
          </div>
        </div>
      ))}
    </div>
  );
}