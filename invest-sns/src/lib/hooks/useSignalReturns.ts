import { useState, useEffect, useMemo, useRef } from 'react';
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

  // 怨좎쑀??肄붿씤?ㅺ낵 ?좎쭨??異붿텧
  const { uniqueCoins, signalsByDate } = useMemo(() => {
    const coinSet = new Set<string>();
    const dateMap: Record<string, CorinpapaSignal[]> = {};

    signals.forEach(signal => {
      const coinId = getCoinId(signal.stock, signal.stockName);
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

  const fetchedRef = useRef(false);

  useEffect(() => {
    const fetchReturns = async () => {
      if (signals.length === 0 || uniqueCoins.length === 0) return;
      if (fetchedRef.current) return; // ?대? fetch?덉쑝硫??ㅽ궢
      fetchedRef.current = true;

      setLoading(true);
      
      try {
        // 1. ?꾩옱 媛寃⑸뱾 媛?몄삤湲?        const currentPrices = await coinGeckoAPI.getCurrentPrices(uniqueCoins);
        
        // 2. 媛??쒓렇?먮퀎濡?怨쇨굅 媛寃⑷낵 ?섏씡瑜?怨꾩궛
        const newReturns: Record<number, SignalReturn> = {};
        
        // ?좎쭨蹂꾨줈 諛곗튂 泥섎━ (rate limit 理쒖쟻??
        const dates = Object.keys(signalsByDate);
        
        for (const date of dates) {
          const signalsForDate = signalsByDate[date];
          const coinsForDate = [...new Set(signalsForDate.map(s => getCoinId(s.stock, s.stockName)).filter(Boolean))];
          
          // ?대떦 ?좎쭨??紐⑤뱺 肄붿씤 媛寃⑹쓣 諛곗튂濡?媛?몄삤湲?          const historicalPrices = await Promise.all(
            coinsForDate.map(async (coinId) => ({
              coinId,
              price: await coinGeckoAPI.getHistoricalPrice(coinId, date)
            }))
          );
          
          const priceMap = Object.fromEntries(
            historicalPrices.map(({ coinId, price }) => [coinId, price])
          );
          
          // ?대떦 ?좎쭨???쒓렇?먮뱾??????섏씡瑜?怨꾩궛
          signalsForDate.forEach(signal => {
            const coinId = getCoinId(signal.stock, signal.stockName);
            if (!coinId) {
              newReturns[signal.id] = {
                signalId: signal.id,
                entryPrice: null,
                currentPrice: null,
                returnRate: null,
                loading: false,
                error: '吏?먰븯吏 ?딅뒗 肄붿씤'
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
              error = '怨쇨굅 媛寃??곗씠???놁쓬';
            } else if (!currentPrice) {
              error = '?꾩옱 媛寃??곗씠???놁쓬';
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

        // 留ㅽ븨?섏? ?딅뒗 肄붿씤??泥섎━
        signals.forEach(signal => {
          if (!newReturns[signal.id]) {
            const coinId = getCoinId(signal.stock, signal.stockName);
            if (!coinId) {
              newReturns[signal.id] = {
                signalId: signal.id,
                entryPrice: null,
                currentPrice: null,
                returnRate: null,
                loading: false,
                error: '吏?먰븯吏 ?딅뒗 肄붿씤'
              };
            }
          }
        });

        setReturns(newReturns);
      } catch (error) {
        console.error('?섏씡瑜?怨꾩궛 ?ㅻ쪟:', error);
        // ?먮윭 ??紐⑤뱺 ?쒓렇?먯뿉 ?먮윭 ?곹깭 ?ㅼ젙
        const errorReturns: Record<number, SignalReturn> = {};
        signals.forEach(signal => {
          errorReturns[signal.id] = {
            signalId: signal.id,
            entryPrice: null,
            currentPrice: null,
            returnRate: null,
            loading: false,
            error: 'API ?ㅻ쪟'
          };
        });
        setReturns(errorReturns);
      } finally {
        setLoading(false);
      }
    };

    fetchReturns();
  }, [signals, uniqueCoins, signalsByDate]);

  // 濡쒕뵫 ?곹깭??湲곕낯 return 媛앹껜???앹꽦
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
      // 罹먯떆 ?대━?????ъ슂泥?쓣 ?꾪빐 signals瑜?鍮?諛곗뿴濡?留뚮뱾?덈떎媛 ?먮옒?濡?蹂듭썝
      setReturns({});
    }
  };
}
