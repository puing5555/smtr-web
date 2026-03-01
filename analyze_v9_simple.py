# -*- coding: utf-8 -*-
import json
from collections import Counter, defaultdict

def analyze_v9_signals():
    print("=== Pipeline V9 Signal Quality Analysis ===")
    
    # JSON 파일 로드
    try:
        with open('pipeline_v9_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: {e}")
        return
    
    print(f"Total analyzed videos: {len(data)}")
    
    # 모든 시그널 추출
    all_signals = []
    video_with_signals = 0
    
    for video in data:
        if video.get('signals'):
            video_with_signals += 1
            for signal in video['signals']:
                signal['video_id'] = video['video_id']
                signal['channel_name'] = video['channel']['name']
                all_signals.append(signal)
    
    print(f"Videos with signals: {video_with_signals}")
    print(f"Total signals: {len(all_signals)}")
    
    if not all_signals:
        print("No signals to analyze.")
        return
    
    # 1. 시그널 타입 분석
    print("\n1. Signal Type Analysis:")
    signal_types = Counter(s.get('signal') for s in all_signals)
    valid_v9_types = {'매수', '긍정', '중립', '경계', '매도'}
    old_types = {'STRONG_BUY', 'BUY', 'POSITIVE', 'HOLD', 'NEUTRAL', 'CONCERN', 'SELL', 'STRONG_SELL'}
    
    for signal_type, count in signal_types.most_common():
        if signal_type in valid_v9_types:
            status = "[OK] V9 Korean"
        elif signal_type in old_types:
            status = "[ERROR] Old English"
        else:
            status = "[ERROR] Unknown"
        print(f"  {status}: {signal_type} - {count}")
    
    invalid_type_signals = [s for s in all_signals if s.get('signal') not in valid_v9_types]
    print(f"Invalid signal types: {len(invalid_type_signals)}")
    
    # 2. key_quote 품질 분석
    print("\n2. Key Quote Quality:")
    empty_quotes = [s for s in all_signals if not s.get('key_quote') or len(s.get('key_quote', '').strip()) < 10]
    print(f"Short/empty key_quotes (under 10 chars): {len(empty_quotes)}")
    
    if empty_quotes:
        print("Examples:")
        for i, signal in enumerate(empty_quotes[:3]):
            quote = signal.get('key_quote', '').strip()
            print(f"   {i+1}. {signal.get('speaker')}: '{quote}' (len: {len(quote)})")
    
    # 3. 타임스탬프 품질
    print("\n3. Timestamp Quality:")
    bad_timestamps = [s for s in all_signals if not s.get('timestamp') or s.get('timestamp') in ['00:00', '0:00', '0']]
    print(f"Bad timestamps: {len(bad_timestamps)}")
    
    # 4. ticker 품질
    print("\n4. Ticker Quality:")
    invalid_tickers = [s for s in all_signals if not s.get('ticker') or s.get('ticker') in ['', '없음', 'N/A', '-', 'null']]
    print(f"Invalid tickers: {len(invalid_tickers)}")
    
    # 5. 중복 분석
    print("\n5. Duplicate Analysis:")
    duplicates = defaultdict(list)
    for signal in all_signals:
        key = (signal.get('video_id'), signal.get('ticker'), signal.get('signal'))
        duplicates[key].append(signal)
    
    duplicate_groups = {k: v for k, v in duplicates.items() if len(v) > 1}
    print(f"Duplicate signal groups: {len(duplicate_groups)}")
    
    # 6. mention_type 분포
    print("\n6. Mention Type Distribution:")
    mention_types = Counter(s.get('mention_type') for s in all_signals)
    for mention_type, count in mention_types.most_common():
        print(f"   {mention_type}: {count}")
    
    # 7. confidence 분포
    print("\n7. Confidence Distribution:")
    confidences = Counter(s.get('confidence') for s in all_signals)
    for conf in ['very_high', 'high', 'medium', 'low', 'very_low']:
        count = confidences.get(conf, 0)
        if count > 0:
            print(f"   {conf}: {count}")
    
    # 8. market 분포
    print("\n8. Market Distribution:")
    markets = Counter(s.get('market') for s in all_signals)
    for market, count in markets.most_common():
        print(f"   {market}: {count}")
    
    # 9. 화자별 분포
    print("\n9. Speaker Distribution:")
    speakers = Counter(s.get('speaker') for s in all_signals)
    for speaker, count in speakers.most_common(10):
        print(f"   {speaker}: {count}")
    
    # 10. 종합 품질 점수
    print("\n=== Overall Quality Analysis ===")
    total_issues = (
        len(invalid_type_signals) + 
        len(empty_quotes) + 
        len(bad_timestamps) + 
        len(invalid_tickers) + 
        len(duplicate_groups)
    )
    
    quality_score = max(0, (len(all_signals) - total_issues) / len(all_signals) * 100) if len(all_signals) > 0 else 0
    
    print(f"Total signals: {len(all_signals)}")
    print(f"Quality issues: {total_issues}")
    print(f"Quality score: {quality_score:.1f}%")
    
    # 11. V9.1 규칙 효과
    print("\n=== V9.1 Rule Effect Analysis ===")
    conclusion_signals = [s for s in all_signals if s.get('mention_type') == '결론']
    etf_signals = [s for s in all_signals if 'ETF' in str(s.get('stock', '')).upper()]
    
    print(f"Conclusion type signals: {len(conclusion_signals)}")
    print(f"ETF related signals: {len(etf_signals)}")
    
    # 12. V10 개선점 제안
    print("\n=== V10 Improvement Suggestions ===")
    print("1. Enforce V9 Korean signal types only")
    print("2. Increase key_quote minimum length to 15 chars") 
    print("3. Mandatory timestamp validation (not 00:00)")
    print("4. Market-specific ticker format validation")
    print("5. Duplicate prevention logic")
    print("6. Strengthen mention_type '결론' vs '논거' distinction")
    print("7. Force confidence<=medium for conditional statements")
    print("8. Normalize speaker names across channels")

if __name__ == "__main__":
    analyze_v9_signals()