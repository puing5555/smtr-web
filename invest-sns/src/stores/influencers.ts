import { create } from 'zustand';
import { supabase } from '@/lib/supabase';

// 타입 정의
export interface Influencer {
  id: number;
  name: string;
  avatar: string;
  verified: boolean;
  totalSignals: number;
  accuracy: number;
  recentActivity: string;
  signalDistribution: Record<string, number>;
  // SMTR 스타일 추가 정보
  channelName: string;
  country: string;
  avgReturn: number; // 평균 수익률
  topStocks: string[]; // 주력 종목들
  radarStats: {
    accuracy: number;
    diversity: number;
    returns: number;
    riskMgmt: number;
    activity: number;
    consistency: number;
  };
}

export interface Signal {
  id: number;
  influencer: string;
  stock: string;
  stockName: string;
  signalType: 'STRONG_BUY' | 'BUY' | 'POSITIVE' | 'HOLD' | 'NEUTRAL' | 'CONCERN' | 'SELL' | 'STRONG_SELL';
  content: string;
  timestamp: string;
  price: number;
  youtubeLink?: string;
  // SMTR 스타일 추가 정보
  returnRate?: number; // 수익률
  analysis: {
    summary: string;
    detail: string;
  };
  videoDate: string; // 영상 날짜
}

export interface Stock {
  symbol: string;
  name: string;
  totalSignals: number;
  recentSignal: string;
  influencers: string[];
  signalDistribution: Record<string, number>;
}

interface InfluencersState {
  // Data
  influencers: Influencer[];
  signals: Signal[];
  stocks: Stock[];
  
  // Loading states
  isLoading: boolean;
  isLoadingSignals: boolean;
  isLoadingStocks: boolean;
  
  // Filters
  signalFilter: string;
  searchQuery: string;
  
  // Actions
  loadInfluencers: () => Promise<void>;
  loadSignals: () => Promise<void>;
  loadStocks: () => Promise<void>;
  setSignalFilter: (filter: string) => void;
  setSearchQuery: (query: string) => void;
  
  // Getters
  getFilteredSignals: () => Signal[];
  getFilteredInfluencers: () => Influencer[];
  getFilteredStocks: () => Stock[];
}

export const useInfluencersStore = create<InfluencersState>((set, get) => ({
  // Initial state
  influencers: [],
  signals: [],
  stocks: [],
  isLoading: false,
  isLoadingSignals: false,
  isLoadingStocks: false,
  signalFilter: 'ALL',
  searchQuery: '',
  
  // Actions
  loadInfluencers: async () => {
    set({ isLoading: true });
    try {
      // TODO: Replace with actual Supabase query
      // const { data, error } = await supabase
      //   .from('influencers')
      //   .select('*');
      
      // if (error) throw error;
      
      // For now, use dummy data with SMTR-style expanded info
      const dummyInfluencers: Influencer[] = [
        {
          id: 1,
          name: '박두환',
          avatar: '👨‍💼',
          verified: true,
          totalSignals: 156,
          accuracy: 78,
          recentActivity: '2시간 전',
          signalDistribution: {
            STRONG_BUY: 25,
            BUY: 45,
            POSITIVE: 30,
            HOLD: 20,
            NEUTRAL: 15,
            CONCERN: 12,
            SELL: 8,
            STRONG_SELL: 1
          },
          channelName: '부자들의 선택',
          country: '🇰🇷',
          avgReturn: 24.8,
          topStocks: ['두산에너빌리티', '삼성전자', '엔비디아'],
          radarStats: {
            accuracy: 78,
            diversity: 85,
            returns: 75,
            riskMgmt: 82,
            activity: 92,
            consistency: 71
          }
        },
        {
          id: 2,
          name: '이효석',
          avatar: '👨‍🎓',
          verified: true,
          totalSignals: 89,
          accuracy: 82,
          recentActivity: '4시간 전',
          signalDistribution: {
            STRONG_BUY: 15,
            BUY: 25,
            POSITIVE: 20,
            HOLD: 12,
            NEUTRAL: 8,
            CONCERN: 6,
            SELL: 2,
            STRONG_SELL: 1
          },
          channelName: '이효석의 주식 카페',
          country: '🇰🇷',
          avgReturn: 32.1,
          topStocks: ['테슬라', '애플', 'SK하이닉스'],
          radarStats: {
            accuracy: 82,
            diversity: 78,
            returns: 88,
            riskMgmt: 85,
            activity: 65,
            consistency: 89
          }
        },
        {
          id: 3,
          name: '세상학개론',
          avatar: '🎓',
          verified: true,
          totalSignals: 234,
          accuracy: 75,
          recentActivity: '1일 전',
          signalDistribution: {
            STRONG_BUY: 40,
            BUY: 60,
            POSITIVE: 50,
            HOLD: 35,
            NEUTRAL: 25,
            CONCERN: 15,
            SELL: 8,
            STRONG_SELL: 1
          },
          channelName: '세상학개론',
          country: '🇰🇷',
          avgReturn: 18.7,
          topStocks: ['비트코인', '이더리움', '솔라나'],
          radarStats: {
            accuracy: 75,
            diversity: 92,
            returns: 68,
            riskMgmt: 71,
            activity: 88,
            consistency: 75
          }
        },
        {
          id: 4,
          name: '코린이 아빠',
          avatar: '👨‍👧‍👦',
          verified: false,
          totalSignals: 169,
          accuracy: 71,
          recentActivity: '6시간 전',
          signalDistribution: {
            STRONG_BUY: 28,
            BUY: 42,
            POSITIVE: 35,
            HOLD: 25,
            NEUTRAL: 20,
            CONCERN: 12,
            SELL: 6,
            STRONG_SELL: 1
          },
          channelName: '코린이 아빠의 주식일기',
          country: '🇰🇷',
          avgReturn: 15.3,
          topStocks: ['삼성전자', '현대차', 'LG전자'],
          radarStats: {
            accuracy: 71,
            diversity: 82,
            returns: 64,
            riskMgmt: 76,
            activity: 85,
            consistency: 68
          }
        }
      ];
      
      set({ influencers: dummyInfluencers });
    } catch (error) {
      console.error('Failed to load influencers:', error);
    } finally {
      set({ isLoading: false });
    }
  },
  
  loadSignals: async () => {
    set({ isLoadingSignals: true });
    try {
      // TODO: Replace with actual Supabase query
      // const { data, error } = await supabase
      //   .from('signals')
      //   .select('*')
      //   .order('created_at', { ascending: false });
      
      // For now, use dummy data with extended SMTR-style information
      const dummySignals: Signal[] = [
        {
          id: 1,
          influencer: '박두환',
          stock: '034020.KS',
          stockName: '두산에너빌리티',
          signalType: 'STRONG_BUY',
          content: '두산에너빌리티가 원전 관련 호재로 급등할 것으로 예상됩니다. 미국 원전 재가동과 소형모듈원전(SMR) 기대감이 높습니다.',
          timestamp: '2시간 전',
          price: 24800,
          youtubeLink: 'https://youtube.com/watch?v=example1',
          returnRate: 32.5,
          analysis: {
            summary: '원전 재가동 호재로 급등 전망',
            detail: '바이든 행정부의 원전 정책 전환과 SMR 기술력을 바탕으로 한 성장 스토리가 매력적. 목표주가 35,000원.'
          },
          videoDate: '2026-02-23'
        },
        {
          id: 2,
          influencer: '박두환',
          stock: '034020.KS',
          stockName: '두산에너빌리티',
          signalType: 'BUY',
          content: '두산에너빌리티 추가 매수 타이밍입니다. 해외 원전 수주 가능성이 높아지고 있습니다.',
          timestamp: '1일 전',
          price: 23500,
          youtubeLink: 'https://youtube.com/watch?v=example2',
          returnRate: 28.1,
          analysis: {
            summary: '해외 수주 기대감으로 추가 매수',
            detail: '체코, 폴란드 등 유럽 원전 시장 진출 가능성 증대. 기술력과 경험을 바탕으로 한 수주 경쟁력 확보.'
          },
          videoDate: '2026-02-22'
        },
        {
          id: 3,
          influencer: '이효석',
          stock: 'NVDA',
          stockName: '엔비디아',
          signalType: 'STRONG_BUY',
          content: '엔비디아의 AI 시장 독점적 지위가 지속될 것으로 전망됩니다. 데이터센터 수요 급증으로 실적 성장이 예상됩니다.',
          timestamp: '4시간 전',
          price: 875.32,
          youtubeLink: 'https://youtube.com/watch?v=example3',
          returnRate: 18.7,
          analysis: {
            summary: 'AI 반도체 시장 독점으로 지속 성장',
            detail: 'H100, H200 칩셋의 압도적 성능과 CUDA 생태계 장벽. 2026년 매출 1500억 달러 전망.'
          },
          videoDate: '2026-02-23'
        },
        {
          id: 4,
          influencer: '이효석',
          stock: 'TSLA',
          stockName: '테슬라',
          signalType: 'BUY',
          content: '테슬라의 자율주행 기술 발전과 에너지 사업 확장이 주목됩니다. 중국 시장 회복세도 긍정적입니다.',
          timestamp: '1일 전',
          price: 248.67,
          youtubeLink: 'https://youtube.com/watch?v=example4',
          returnRate: 15.2,
          analysis: {
            summary: '자율주행과 에너지 사업 성장 기대',
            detail: 'FSD 기술 완성도 향상과 중국 시장 판매 회복. 에너지 저장 사업도 고성장 지속 전망.'
          },
          videoDate: '2026-02-22'
        },
        {
          id: 5,
          influencer: '세상학개론',
          stock: 'BTC-USD',
          stockName: '비트코인',
          signalType: 'POSITIVE',
          content: '비트코인이 기관 투자자들의 관심을 받으며 상승세를 이어가고 있습니다. ETF 자금 유입도 긍정적입니다.',
          timestamp: '1일 전',
          price: 96500,
          youtubeLink: 'https://youtube.com/watch?v=example5',
          returnRate: 12.8,
          analysis: {
            summary: '기관 투자자 유입으로 상승세',
            detail: '비트코인 ETF 순유입 증가와 기관들의 비트코인 추가 매수. 100K 돌파 시나리오 유력.'
          },
          videoDate: '2026-02-22'
        },
        {
          id: 6,
          influencer: '세상학개론',
          stock: 'ETH-USD',
          stockName: '이더리움',
          signalType: 'BUY',
          content: '이더리움의 업그레이드가 완료되면서 스테이킹 수익률이 개선될 전망입니다.',
          timestamp: '2일 전',
          price: 3420,
          youtubeLink: 'https://youtube.com/watch?v=example6',
          returnRate: 8.5,
          analysis: {
            summary: '업그레이드 완료로 스테이킹 수익 개선',
            detail: '프로토댕커샤딩 업그레이드로 트랜잭션 처리 속도 향상. DeFi 활성화 기대.'
          },
          videoDate: '2026-02-21'
        },
        {
          id: 7,
          influencer: '코린이 아빠',
          stock: '005930.KS',
          stockName: '삼성전자',
          signalType: 'HOLD',
          content: '삼성전자가 메모리 반도체 사이클 회복을 기다리는 구간입니다. 장기적으로는 긍정적입니다.',
          timestamp: '6시간 전',
          price: 58900,
          youtubeLink: 'https://youtube.com/watch?v=example7',
          returnRate: 5.2,
          analysis: {
            summary: '메모리 반도체 사이클 회복 대기',
            detail: '2026년 하반기 메모리 슈퍼사이클 기대. AI 서버용 HBM 메모리 수요 급증 전망.'
          },
          videoDate: '2026-02-23'
        },
        {
          id: 8,
          influencer: '코린이 아빠',
          stock: '000660.KS',
          stockName: 'SK하이닉스',
          signalType: 'BUY',
          content: 'SK하이닉스의 HBM 메모리 독점 공급으로 실적 개선이 기대됩니다.',
          timestamp: '1일 전',
          price: 142000,
          youtubeLink: 'https://youtube.com/watch?v=example8',
          returnRate: 24.7,
          analysis: {
            summary: 'HBM 메모리 독점 공급으로 실적 급성장',
            detail: '엔비디아 H100/H200 칩셋에 독점 공급. HBM4 양산으로 마진 개선 기대.'
          },
          videoDate: '2026-02-22'
        }
      ];
      
      set({ signals: dummySignals });
    } catch (error) {
      console.error('Failed to load signals:', error);
    } finally {
      set({ isLoadingSignals: false });
    }
  },
  
  loadStocks: async () => {
    set({ isLoadingStocks: true });
    try {
      // TODO: Replace with actual Supabase query
      const dummyStocks: Stock[] = [
        {
          symbol: 'NVDA',
          name: '엔비디아',
          totalSignals: 45,
          recentSignal: 'STRONG_BUY',
          influencers: ['박두환', '이효석'],
          signalDistribution: {
            STRONG_BUY: 18,
            BUY: 15,
            POSITIVE: 8,
            HOLD: 3,
            NEUTRAL: 1,
            CONCERN: 0,
            SELL: 0,
            STRONG_SELL: 0
          }
        },
        {
          symbol: 'TSLA',
          name: '테슬라',
          totalSignals: 32,
          recentSignal: 'BUY',
          influencers: ['이효석', '세상학개론'],
          signalDistribution: {
            STRONG_BUY: 8,
            BUY: 12,
            POSITIVE: 7,
            HOLD: 3,
            NEUTRAL: 2,
            CONCERN: 0,
            SELL: 0,
            STRONG_SELL: 0
          }
        },
        {
          symbol: 'AAPL',
          name: '애플',
          totalSignals: 28,
          recentSignal: 'POSITIVE',
          influencers: ['세상학개론', '박두환'],
          signalDistribution: {
            STRONG_BUY: 5,
            BUY: 8,
            POSITIVE: 10,
            HOLD: 3,
            NEUTRAL: 2,
            CONCERN: 0,
            SELL: 0,
            STRONG_SELL: 0
          }
        }
      ];
      
      set({ stocks: dummyStocks });
    } catch (error) {
      console.error('Failed to load stocks:', error);
    } finally {
      set({ isLoadingStocks: false });
    }
  },
  
  setSignalFilter: (filter: string) => set({ signalFilter: filter }),
  setSearchQuery: (query: string) => set({ searchQuery: query }),
  
  // Getters
  getFilteredSignals: () => {
    const { signals, signalFilter, searchQuery } = get();
    return signals.filter(signal => {
      if (signalFilter !== 'ALL' && signal.signalType !== signalFilter) return false;
      if (searchQuery && !signal.stock.toLowerCase().includes(searchQuery.toLowerCase()) &&
          !signal.stockName.toLowerCase().includes(searchQuery.toLowerCase()) &&
          !signal.influencer.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    });
  },
  
  getFilteredInfluencers: () => {
    const { influencers, searchQuery } = get();
    return influencers.filter(influencer => {
      if (searchQuery && !influencer.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    });
  },
  
  getFilteredStocks: () => {
    const { stocks, searchQuery } = get();
    return stocks.filter(stock => {
      if (searchQuery && !stock.symbol.toLowerCase().includes(searchQuery.toLowerCase()) &&
          !stock.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    });
  },
}));