'use client';

import { useEffect, useState } from 'react';
import { Search, Filter, RefreshCw, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

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

export default function TimelinePage() {
  const [filings, setFilings] = useState<Filing[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'A' | 'B'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load filings from backend
  const loadFilings = async (reset: boolean = false, loadPage: number = 1) => {
    if (isLoading) return;
    
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        page: loadPage.toString(),
        limit: '20'
      });

      if (filter !== 'all') {
        params.append('grade', filter);
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

      setHasMore(data.pagination.has_next);
      setPage(loadPage);
    } catch (error) {
      console.error('Failed to load filings:', error);
      setError('공시 데이터를 불러올 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    loadFilings(true);
  }, [filter, searchQuery]);

  // Load more
  const handleLoadMore = () => {
    if (hasMore && !isLoading) {
      loadFilings(false, page + 1);
    }
  };

  // Refresh
  const handleRefresh = () => {
    setPage(1);
    loadFilings(true);
  };

  // Search handler
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadFilings(true);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                실시간 공시 타임라인
              </h1>
              <p className="text-gray-400 mt-1">
                한국거래소 DART 공시를 실시간으로 확인하세요
              </p>
            </div>
            <Button
              onClick={handleRefresh}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              새로고침
            </Button>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4 items-center">
            <form onSubmit={handleSearch} className="flex-1 flex gap-2">
              <Input
                type="text"
                placeholder="회사명 또는 공시명으로 검색..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 bg-gray-800 border-gray-700 text-white placeholder:text-gray-400"
              />
              <Button type="submit" variant="outline" className="border-gray-700">
                <Search className="w-4 h-4" />
              </Button>
            </form>

            <div className="flex gap-2">
              <Button
                variant={filter === 'all' ? 'default' : 'outline'}
                onClick={() => setFilter('all')}
                size="sm"
                className={filter === 'all' 
                  ? 'bg-blue-600 hover:bg-blue-700' 
                  : 'border-gray-700 text-gray-300 hover:bg-gray-800'
                }
              >
                전체
              </Button>
              <Button
                variant={filter === 'A' ? 'default' : 'outline'}
                onClick={() => setFilter('A')}
                size="sm"
                className={filter === 'A' 
                  ? 'bg-green-600 hover:bg-green-700' 
                  : 'border-gray-700 text-gray-300 hover:bg-gray-800'
                }
              >
                📊 A등급
              </Button>
              <Button
                variant={filter === 'B' ? 'default' : 'outline'}
                onClick={() => setFilter('B')}
                size="sm"
                className={filter === 'B' 
                  ? 'bg-yellow-600 hover:bg-yellow-700' 
                  : 'border-gray-700 text-gray-300 hover:bg-gray-800'
                }
              >
                🔔 B등급
              </Button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-300">
            {error}
          </div>
        )}

        {/* Timeline */}
        {filings.length === 0 && !isLoading ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <Filter className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-300 mb-2">공시 데이터가 없습니다</h3>
            <p className="text-gray-500">
              검색 조건을 변경하거나 잠시 후 다시 시도해보세요.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filings.map((filing) => (
              <FilingCard key={filing.id} filing={filing} />
            ))}
          </div>
        )}

        {/* Load More */}
        {hasMore && !error && (
          <div className="text-center mt-8">
            <Button 
              onClick={handleLoadMore}
              disabled={isLoading}
              variant="outline"
              className="border-gray-700 text-gray-300 hover:bg-gray-800"
            >
              {isLoading ? '로딩 중...' : '더 보기'}
            </Button>
          </div>
        )}

        {/* Loading skeleton */}
        {isLoading && filings.length === 0 && (
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="bg-gray-800 rounded-lg p-6 animate-pulse">
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-gray-700 rounded"></div>
                  <div className="flex-1 space-y-3">
                    <div className="h-5 bg-gray-700 rounded w-3/4"></div>
                    <div className="h-4 bg-gray-700 rounded w-1/2"></div>
                    <div className="h-4 bg-gray-700 rounded w-full"></div>
                  </div>
                  <div className="w-16 h-8 bg-gray-700 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Filing Card Component
interface FilingCardProps {
  filing: Filing;
}

function FilingCard({ filing }: FilingCardProps) {
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'bg-green-900/20 text-green-300 border-green-800';
      case 'B': return 'bg-yellow-900/20 text-yellow-300 border-yellow-800';
      default: return 'bg-gray-900/20 text-gray-300 border-gray-700';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition-colors border border-gray-700">
      <div className="flex items-start space-x-4">
        {/* Time */}
        <div className="text-xs text-gray-400 font-mono min-w-[3rem]">
          {filing.time}
        </div>

        {/* Grade Icon */}
        <div className="text-xl">
          {filing.grade_icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="font-semibold text-white truncate">
              {filing.corp_name}
            </h3>
            <Badge 
              variant="outline" 
              className={`text-xs ${getGradeColor(filing.grade)}`}
            >
              {filing.grade}등급
            </Badge>
            {filing.stock_code && (
              <Badge variant="secondary" className="text-xs bg-gray-700 text-gray-300">
                {filing.stock_code}
              </Badge>
            )}
          </div>

          <p className="text-gray-300 text-sm mb-3 leading-relaxed">
            {filing.report_name}
          </p>

          {filing.ai_summary && (
            <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-3 mb-3">
              <div className="text-xs text-blue-300 font-medium mb-1">🤖 AI 요약</div>
              <p className="text-sm text-blue-100 leading-relaxed">
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
            className="border-gray-600 text-gray-300 hover:bg-gray-700 text-xs"
          >
            <ExternalLink className="w-3 h-3 mr-1" />
            DART
          </Button>
        </div>
      </div>
    </div>
  );
}