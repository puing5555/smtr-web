// CoinGecko API 유틸리티
// 무료 API: 분당 10-30회 제한, 캐싱으로 최적화

export interface CoinPrice {
  id: string;
  current_price: number;
  price_change_percentage_24h: number;
  last_updated: string;
}

export interface HistoricalPrice {
  timestamp: number;
  price: number;
}

// 코인 심볼 -> CoinGecko ID 매핑
export const COIN_MAPPING: Record<string, string> = {
  // 크립토
  'XRP': 'ripple',
  '리플 (XRP)': 'ripple',
  '이더리움': 'ethereum',
  'ETH': 'ethereum',
  '비트코인': 'bitcoin',
  'BTC': 'bitcoin',
  '캔톤네트워크 (CC)': 'canton-network',
  '캐톤네트워크 (CC)': 'canton-network',
  'CC': 'canton-network',
  'BNB': 'binancecoin',
  '솔라나': 'solana',
  'SOL': 'solana',
  '체인링크': 'chainlink',
  '모네로': 'monero',
  '월드코인': 'worldcoin-wld',
  '퍼지펭귄 (PENGU)': 'pudgy-penguins',
  'PENGU': 'pudgy-penguins',
  '이더질라 (ATNF)': '',
  // 주식 (CoinGecko 미지원)
  '마이크로스트래티지 (MSTR)': '',
  '마이크로스트레티지 (MSTR)': '',
  'MSTR': '',
  '엔비디아': '',
  '엔비디아 (NVDA)': '',
  'NVDA': '',
  '팔란티어 (PLTR)': '',
  'PLTR': '',
  '구글 (GOOGL)': '',
  'GOOGL': '',
  '알파벳': '',
  'SBI': '',
  'SBI 홀딩스': '',
  'SK': '',
  '삼성ENA': '',
  '오뚜기': '',
  '율촌화학': '',
  '라이나스 희토류': '',
  '코스피': '',
  '캔톤 스트레티지 홀딩스 (CNTN)': '',
  'CNTN': '',
  '코인베이스 (COIN)': '',
  'COIN': '',
  '타르 (THAR)': '',
  'THAR': '',
  '비트마인 (BMNR)': '',
  'BMNR': '',
  '블리시': '',
  '샤프링크': '',
  // 카테고리 (가격 추적 불가)
  '알트코인': '',
  '스테이블코인': '',
  '암호화폐': '',
  '기술주': '',
  '미국 주식': '',
  '금': '',
  '서클 (Circle)': '',
  '월드리버티파이낸셜 (WLFI)': '',
  'WLFI': '',
  '오픈AI (ChatGPT)': '',
};

class CoinGeckoAPI {
  private baseUrl = 'https://api.coingecko.com/api/v3';
  private cache = new Map<string, { data: any; timestamp: number }>();
  private cacheTimeout = 5 * 60 * 1000; // 5분 캐시

  private async fetchWithCache<T>(url: string, cacheKey: string): Promise<T | null> {
    // 캐시 확인
    const cached = this.cache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    try {
      // rate limit 주의: 요청 간 100ms 지연
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const response = await fetch(url, {
        headers: {
          'accept': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // 캐시 저장
      this.cache.set(cacheKey, { data, timestamp: Date.now() });
      
      return data;
    } catch (error) {
      console.error(`CoinGecko API Error (${url}):`, error);
      return null;
    }
  }

  async getCurrentPrices(coinIds: string[]): Promise<Record<string, CoinPrice>> {
    if (coinIds.length === 0) return {};
    
    // 빈 문자열 필터링 (매핑되지 않는 코인들)
    const validIds = coinIds.filter(id => id.length > 0);
    if (validIds.length === 0) return {};

    const idsParam = validIds.join(',');
    const url = `${this.baseUrl}/simple/price?ids=${idsParam}&vs_currencies=usd&include_24hr_change=true&include_last_updated_at=true`;
    const cacheKey = `prices_${idsParam}`;

    const data = await this.fetchWithCache<Record<string, any>>(url, cacheKey);
    if (!data) return {};

    const result: Record<string, CoinPrice> = {};
    Object.entries(data).forEach(([id, priceData]: [string, any]) => {
      result[id] = {
        id,
        current_price: priceData.usd || 0,
        price_change_percentage_24h: priceData.usd_24h_change || 0,
        last_updated: new Date(priceData.last_updated_at * 1000).toISOString(),
      };
    });

    return result;
  }

  async getHistoricalPrice(coinId: string, date: string): Promise<number | null> {
    if (!coinId) return null;

    // 날짜를 DD-MM-YYYY 포맷으로 변환
    const dateObj = new Date(date);
    const formattedDate = `${dateObj.getDate().toString().padStart(2, '0')}-${(dateObj.getMonth() + 1).toString().padStart(2, '0')}-${dateObj.getFullYear()}`;
    
    const url = `${this.baseUrl}/coins/${coinId}/history?date=${formattedDate}`;
    const cacheKey = `history_${coinId}_${formattedDate}`;

    const data = await this.fetchWithCache<any>(url, cacheKey);
    if (!data || !data.market_data || !data.market_data.current_price) {
      return null;
    }

    return data.market_data.current_price.usd || null;
  }

  // 배치로 여러 날짜의 가격 데이터 가져오기 (rate limit 주의)
  async getHistoricalPricesBatch(coinId: string, dates: string[]): Promise<Record<string, number | null>> {
    if (!coinId || dates.length === 0) return {};

    const result: Record<string, number | null> = {};
    
    // 순차 처리로 rate limit 준수
    for (const date of dates) {
      result[date] = await this.getHistoricalPrice(coinId, date);
    }

    return result;
  }
}

export const coinGeckoAPI = new CoinGeckoAPI();

// 수익률 계산 헬퍼 함수
export function calculateReturn(entryPrice: number, currentPrice: number): number {
  if (entryPrice <= 0) return 0;
  return ((currentPrice - entryPrice) / entryPrice) * 100;
}

// 코인 심볼에서 CoinGecko ID 가져오기
export function getCoinId(symbol: string, stockName?: string): string {
  return COIN_MAPPING[symbol] || COIN_MAPPING[stockName || ''] || '';
}

// 수익률 표시용 포맷팅
export function formatReturn(returnRate: number): string {
  const sign = returnRate >= 0 ? '+' : '';
  return `${sign}${returnRate.toFixed(1)}%`;
}

// 수익률 색상 클래스
export function getReturnColor(returnRate: number): string {
  return returnRate >= 0 ? 'text-green-600' : 'text-red-600';
}