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
      
      // For now, use dummy data
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
      
      // For now, use dummy data
      const dummySignals: Signal[] = [
        {
          id: 1,
          influencer: '박두환',
          stock: 'NVDA',
          stockName: '엔비디아',
          signalType: 'STRONG_BUY',
          content: '엔비디아의 AI 시장 독점적 지위가 지속될 것으로 전망됩니다. 데이터센터 수요 급증으로 실적 성장이 예상됩니다.',
          timestamp: '2시간 전',
          price: 875.32,
          youtubeLink: 'https://youtube.com/watch?v=example1'
        },
        {
          id: 2,
          influencer: '이효석',
          stock: 'TSLA',
          stockName: '테슬라',
          signalType: 'BUY',
          content: '테슬라의 자율주행 기술 발전과 에너지 사업 확장이 주목됩니다. 중국 시장 회복세도 긍정적입니다.',
          timestamp: '4시간 전',
          price: 248.67,
          youtubeLink: 'https://youtube.com/watch?v=example2'
        },
        {
          id: 3,
          influencer: '세상학개론',
          stock: 'AAPL',
          stockName: '애플',
          signalType: 'POSITIVE',
          content: '애플의 비전 프로 판매량이 예상보다 좋고, 아이폰 16 시리즈도 안정적인 판매를 보이고 있습니다.',
          timestamp: '1일 전',
          price: 187.25,
          youtubeLink: 'https://youtube.com/watch?v=example3'
        },
        {
          id: 4,
          influencer: '코린이 아빠',
          stock: 'BTC',
          stockName: '비트코인',
          signalType: 'HOLD',
          content: '비트코인이 $60,000 근처에서 횡보하고 있습니다. 단기적으로는 관망이 좋을 것 같습니다.',
          timestamp: '6시간 전',
          price: 60125,
          youtubeLink: 'https://youtube.com/watch?v=example4'
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