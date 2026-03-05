import json
from datetime import datetime, timedelta

# 데이터 로드
with open('real_buy_signals.json', 'r', encoding='utf-8') as f:
    real_buy_signals = json.load(f)

with open('C:\\Users\\Mario\\work\\invest-sns\\data\\stockPrices.json', 'r', encoding='utf-8') as f:
    stock_prices = json.load(f)

print("=== 진짜 매수 시그널 수익률 계산 ===")
print(f"분석 대상: {len(real_buy_signals)}개 시그널\n")

results = []

for i, signal in enumerate(real_buy_signals):
    print(f"{i+1}. {signal['stock']} ({signal['ticker']})")
    print(f"   발언: {signal['key_quote'][:100]}...")
    print(f"   신뢰도: {signal['confidence']}")
    print(f"   타임스탬프: {signal['timestamp']}")
    
    ticker = signal['ticker']
    
    # 주가 데이터 확인
    if ticker in stock_prices:
        price_data = stock_prices[ticker]
        current_price = price_data.get('currentPrice', 0)
        
        print(f"   현재가: {current_price:,.0f}원")
        
        # 히스토리 데이터가 있는지 확인
        if 'prices' in price_data and price_data['prices']:
            print(f"   히스토리 데이터: {len(price_data['prices'])}개 가격")
            
            # 최근 데이터로 추정 계산 (실제로는 시그널 날짜 기준이어야 함)
            recent_prices = price_data['prices'][-10:]  # 최근 10개 데이터
            if recent_prices:
                # 임시로 최근 가격 변화로 수익률 추정
                oldest_recent = recent_prices[0]['close']
                newest_recent = recent_prices[-1]['close']
                
                print(f"   최근 변화: {oldest_recent:,.2f} → {newest_recent:,.2f}")
                
                # 수익률 계산 (현재가 기준)
                if oldest_recent > 0:
                    return_pct = (current_price - oldest_recent) / oldest_recent * 100
                    print(f"   추정 수익률: {return_pct:.2f}%")
                else:
                    print("   수익률 계산 불가")
        else:
            print("   히스토리 데이터 없음")
            
        # 결과 저장
        result = {
            "stock": signal['stock'],
            "ticker": signal['ticker'],
            "speaker_id": signal['speaker_id'],
            "current_price": current_price,
            "confidence": signal['confidence'],
            "key_quote": signal['key_quote'],
            "estimated_return": "데이터 부족으로 계산 불가"
        }
        results.append(result)
        
    else:
        print(f"   ❌ {ticker} 가격 데이터 없음")
        result = {
            "stock": signal['stock'],
            "ticker": signal['ticker'],
            "speaker_id": signal['speaker_id'],
            "error": "가격 데이터 없음"
        }
        results.append(result)
    
    print("-" * 80)

# 요약 통계
print("\n=== 수익률 분석 요약 ===")
available_data = len([r for r in results if 'current_price' in r])
print(f"가격 데이터 보유: {available_data}/{len(results)}개")

# 결과 저장
with open('returns_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("분석 결과를 returns_analysis.json에 저장했습니다.")

# 현재 상황 요약
print("\n=== 현재 상황 요약 ===")
print("⚠️ 시그널 정확도 문제:")
print(f"  - 총 분석 시그널: 50개")
print(f"  - 진짜 매수 판정: 3개 (6.0%)")
print(f"  - 대부분 시그널이 애매한 표현으로 구성")
print("\n💡 개선 방안:")
print("  - 키워드 기반이 아닌 LLM 기반 분류 필요")
print("  - 영상별 전체 맥락 고려한 종합 판단")
print("  - 유튜버별 발언 패턴 분석")