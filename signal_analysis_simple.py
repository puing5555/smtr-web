# -*- coding: utf-8 -*-
import requests
import json
from collections import Counter

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"

headers = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
}

def get_signals():
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/signals?select=*",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

def analyze_signal_quality():
    print("=== Supabase 시그널 품질 분석 ===")
    
    signals = get_signals()
    if not signals:
        print("ERROR: 시그널 데이터를 불러올 수 없습니다.")
        return
    
    print(f"총 시그널 수: {len(signals)}개")
    
    # 1. 시그널 타입 분석
    print("\n1. 시그널 타입 분석:")
    signal_types = Counter(s.get('signal_type') for s in signals)
    valid_types = {'STRONG_BUY', 'BUY', 'POSITIVE', 'HOLD', 'NEUTRAL', 'CONCERN', 'SELL', 'STRONG_SELL'}
    
    for signal_type, count in signal_types.most_common():
        status = "OK" if signal_type in valid_types else "ERROR"
        print(f"  [{status}] {signal_type}: {count}개")
    
    invalid_signals = [s for s in signals if s.get('signal_type') not in valid_types]
    print(f"잘못된 시그널 타입: {len(invalid_signals)}개")
    
    # 2. key_quote 품질 분석
    print("\n2. key_quote 품질 분석:")
    empty_quotes = [s for s in signals if not s.get('key_quote') or len(s.get('key_quote', '')) < 10]
    print(f"key_quote 부정확 (비어있거나 10자 미만): {len(empty_quotes)}개")
    
    # 3. 타임스탬프 분석
    print("\n3. 타임스탬프 분석:")
    bad_timestamps = [s for s in signals if not s.get('timestamp') or s.get('timestamp') in ['00:00', '0:00', '0']]
    print(f"타임스탬프 이상: {len(bad_timestamps)}개")
    
    # 4. ticker 품질 분석
    print("\n4. ticker 품질 분석:")
    invalid_tickers = [s for s in signals if not s.get('ticker') or s.get('ticker') in ['', '없음', 'N/A', '-', 'null']]
    print(f"ticker 이상: {len(invalid_tickers)}개")
    
    ticker_counter = Counter(s.get('ticker') for s in invalid_tickers)
    print("이상한 ticker 분포:")
    for ticker, count in ticker_counter.most_common(5):
        print(f"   '{ticker}': {count}개")
    
    # 5. 중복 분석
    print("\n5. 중복 시그널 분석:")
    duplicates = {}
    for signal in signals:
        key = (signal.get('video_id'), signal.get('ticker'), signal.get('signal_type'))
        if key not in duplicates:
            duplicates[key] = []
        duplicates[key].append(signal)
    
    duplicate_groups = {k: v for k, v in duplicates.items() if len(v) > 1}
    print(f"중복 시그널 그룹: {len(duplicate_groups)}개")
    
    # 6. mention_type 분석
    print("\n6. mention_type 분포:")
    mention_types = Counter(s.get('mention_type') for s in signals)
    for mention_type, count in mention_types.most_common():
        print(f"   {mention_type}: {count}개")
    
    # 7. confidence 분석
    print("\n7. confidence 분포:")
    confidences = Counter(s.get('confidence') for s in signals)
    for conf in ['very_high', 'high', 'medium', 'low', 'very_low']:
        if conf in confidences:
            print(f"   {conf}: {confidences[conf]}개")
    
    # 8. 종합 분석
    print("\n=== 종합 품질 분석 ===")
    total_issues = len(invalid_signals) + len(empty_quotes) + len(bad_timestamps) + len(invalid_tickers) + len(duplicate_groups)
    quality_score = max(0, (len(signals) - total_issues) / len(signals) * 100) if len(signals) > 0 else 0
    
    print(f"총 시그널: {len(signals)}개")
    print(f"품질 이슈: {total_issues}개")
    print(f"품질 점수: {quality_score:.1f}%")
    
    print("\n=== V9.1 규칙 효과 분석 ===")
    # mention_type이 "결론"인 것들 중 signal이 적절히 분류되었는지
    conclusion_signals = [s for s in signals if s.get('mention_type') == '결론']
    print(f"결론 타입 시그널: {len(conclusion_signals)}개")
    
    # ETF 시그널이 누락되지 않았는지
    etf_signals = [s for s in signals if 'ETF' in str(s.get('ticker', '')).upper() or 'ETF' in str(s.get('stock', '')).upper()]
    print(f"ETF 관련 시그널: {len(etf_signals)}개")
    
    print("\n=== V10 개선점 제안 ===")
    print("1. 시그널 타입 validation 강화")
    print("2. key_quote 최소 길이 15자로 상향")
    print("3. 타임스탬프 필수 입력 검증")
    print("4. ticker 표준화 및 검증")
    print("5. 중복 방지 로직 추가")

if __name__ == "__main__":
    analyze_signal_quality()