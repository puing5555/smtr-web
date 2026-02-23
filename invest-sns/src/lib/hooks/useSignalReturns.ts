import { useState, useEffect, useMemo } from 'react';
import { coinGeckoAPI, getCoinId, calculateReturn } from '@/lib/api/coingecko';
import type { CorinpapaSignal } from '@/data/corinpapa-signals';

export interface SignalReturn {
  signalId: number;
  entryPrice: number | null;
  currentPrice: number | null;
  returnRate: number | null;
  loading: boolean;
  error: string | null;
}

export function useSignalReturns(signals: CorinpapaSignal[]) {
  const [returns, setReturns] = useState<Record<number, SignalReturn>>({});
  const [loading, setLoading] = useState(false);

  // 고유한 코인들과 날짜들 추출
  const { uniqueCoins, signalsByDate } = useMemo(() => {
    const coinSet = new Set<string>();
    const dateMap: Record<string, CorinpapaSignal[]> = {};

    signals.forEach(signal => {
      const coinId = getCoinId(signal.stock);
      if (coinId) {
        coinSet.add(coinId);
        const dateKey = signal.videoDate;
        if (!dateMap[dateKey]) {
          dateMap[dateKey] = [];
        }
        dateMap[dateKey].push(signal);
      }
    });

    return {
      uniqueCoins: Array.from(coinSet),
      signalsByDate: dateMap
    };
  }, [signals]);

  useEffect(() => {
    const fetchReturns = async () => {
      if (signals.length === 0 || uniqueCoins.length === 0) return;

      setLoading(true);
      
      try {
        // 1. 현재 가격들 가져오기
        const currentPrices = await coinGeckoAPI.getCurrentPrices(uniqueCoins);
        
        // 2. 각 시그널별로 과거 가격과 수익률 계산
        const newReturns: Record<number, SignalReturn> = {};
        
        // 날짜별로 배치 처리 (rate limit 최적화)
        const dates = Object.keys(signalsByDate);
        
        for (const date of dates) {
          const signalsForDate = signalsByDate[date];
          const coinsForDate = [...new Set(signalsForDate.map(s => getCoinId(s.stock)).filter(Boolean))];
          
          // 해당 날짜의 모든 코인 가격을 배치로 가져오기
          const historicalPrices = await Promise.all(
            coinsForDate.map(async (coinId) => ({
              coinId,
              price: await coinGeckoAPI.getHistoricalPrice(coinId, date)
            }))
          );
          
          const priceMap = Object.fromEntries(
            historicalPrices.map(({ coinId, price }) => [coinId, price])
          );
          
          // 해당 날짜의 시그널들에 대해 수익률 계산
          signalsForDate.forEach(signal => {
            const coinId = getCoinId(signal.stock);
            if (!coinId) {
              newReturns[signal.id] = {
                signalId: signal.id,
                entryPrice: null,
                currentPrice: null,
                returnRate: null,
                loading: false,
                error: '지원하지 않는 코인'
              };
              return;
            }

            const entryPrice = priceMap[coinId];
            const currentPriceData = currentPrices[coinId];
            const currentPrice = currentPriceData?.current_price || null;

            let returnRate: number | null = null;
            let error: string | null = null;

            if (entryPrice && currentPrice) {
              returnRate = calculateReturn(entryPrice, currentPrice);
            } else if (!entryPrice) {
              error = '과거 가격 데이터 없음';
            } else if (!currentPrice) {
              error = '현재 가격 데이터 없음';
            }

            newReturns[signal.id] = {
              signalId: signal.id,
              entryPrice,
              currentPrice,
              returnRate,
              loading: false,
              error
            };
          });
        }

        // 매핑되지 않는 코인들 처리
        signals.forEach(signal => {
          if (!newReturns[signal.id]) {
            const coinId = getCoinId(signal.stock);
            if (!coinId) {
              newReturns[signal.id] = {
                signalId: signal.id,
                entryPrice: null,
                currentPrice: null,
                returnRate: null,
                loading: false,
                error: '지원하지 않는 코인'
              };
            }
          }
        });

        setReturns(newReturns);
      } catch (error) {
        console.error('수익률 계산 오류:', error);
        // 에러 시 모든 시그널에 에러 상태 설정
        const errorReturns: Record<number, SignalReturn> = {};
        signals.forEach(signal => {
          errorReturns[signal.id] = {
            signalId: signal.id,
            entryPrice: null,
            currentPrice: null,
            returnRate: null,
            loading: false,
            error: 'API 오류'
          };
        });
        setReturns(errorReturns);
      } finally {
        setLoading(false);
      }
    };

    fetchReturns();
  }, [signals, uniqueCoins, signalsByDate]);

  // 로딩 상태의 기본 return 객체들 생성
  const returnsWithLoading = useMemo(() => {
    const result: Record<number, SignalReturn> = { ...returns };
    
    signals.forEach(signal => {
      if (!result[signal.id]) {
        result[signal.id] = {
          signalId: signal.id,
          entryPrice: null,
          currentPrice: null,
          returnRate: null,
          loading: loading,
          error: null
        };
      }
    });

    return result;
  }, [returns, signals, loading]);

  return {
    returns: returnsWithLoading,
    loading,
    refetch: () => {
      // 캐시 클리어 후 재요청을 위해 signals를 빈 배열로 만들었다가 원래대로 복원
      setReturns({});
    }
  };
}