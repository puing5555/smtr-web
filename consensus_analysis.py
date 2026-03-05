import json
from collections import defaultdict, Counter
from datetime import datetime

# 저장된 데이터 읽기
with open("C:\\Users\\Mario\\work\\consensus_raw_data.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

print("=== 유튜버 컨센서스 분석 ===")
print()

# 시그널 타입 매핑 (한글 -> 영어 카테고리)
signal_mapping = {
    "강매수": "STRONG_BUY",
    "매수": "BUY", 
    "긍정": "POSITIVE",
    "보유": "HOLD",
    "중립": "NEUTRAL",
    "경계": "CONCERN", 
    "매도": "SELL",
    "강매도": "STRONG_SELL"
}

# 시그널 점수 (매수=긍정, 매도=부정)
signal_scores = {
    "STRONG_BUY": 2,
    "BUY": 2,
    "POSITIVE": 1, 
    "HOLD": 0,
    "NEUTRAL": 0,
    "CONCERN": -1,
    "SELL": -2,
    "STRONG_SELL": -2
}

def analyze_stock_consensus(stock_name, signals):
    print(f"\n{'='*50}")
    print(f"{stock_name} 컨센서스 분석")
    print(f"{'='*50}")
    
    if not signals:
        print("ERROR: 시그널 데이터 없음")
        return None
        
    # 1. 시그널 타입별 집계
    signal_counts = Counter()
    signal_scores_sum = 0
    
    # 2. 유튜버별 분석
    influencer_signals = defaultdict(list)
    
    # 유튜버 이름 매핑을 위한 speaker_id -> name 맵 (일단 speaker_id 사용)
    speaker_names = {}
    
    for signal in signals:
        signal_type = signal.get("signal", "UNKNOWN")
        signal_counts[signal_type] += 1
        
        # 점수 계산
        english_signal = signal_mapping.get(signal_type, "NEUTRAL")
        score = signal_scores.get(english_signal, 0)
        signal_scores_sum += score
        
        # 유튜버별 정보
        speaker_id = signal.get("speaker_id", "")
        video_id = signal.get("video_id", "")
        created_at = signal.get("created_at", "")[:10] if signal.get("created_at") else ""
        key_quote = signal.get("key_quote", "")[:50] + "..." if len(signal.get("key_quote", "")) > 50 else signal.get("key_quote", "")
        
        # speaker 이름은 별도 테이블에서 가져와야 하지만, 일단 speaker_id 사용
        speaker_name = f"유튜버_{speaker_id[:8]}"
        speaker_names[speaker_id] = speaker_name
        
        influencer_signals[speaker_id].append({
            "name": speaker_name,
            "signal": signal_type,
            "english_signal": english_signal,
            "date": created_at,
            "quote": key_quote,
            "video_id": video_id,
            "score": score
        })
    
    # 3. 기본 통계
    total_signals = len(signals)
    unique_influencers = len(influencer_signals)
    avg_score = signal_scores_sum / total_signals if total_signals > 0 else 0
    
    print(f"총 시그널: {total_signals}개")
    print(f"유튜버 수: {unique_influencers}명")
    print(f"평균 점수: {avg_score:.2f}")
    print()
    
    # 4. 시그널 분포
    print("시그널 분포:")
    for signal_type, count in signal_counts.most_common():
        percentage = (count / total_signals) * 100
        english_signal = signal_mapping.get(signal_type, signal_type)
        print(f"  {signal_type} ({english_signal}): {count}개 ({percentage:.1f}%)")
    print()
    
    # 5. 유튜버별 상세 분석
    print("유튜버별 시그널:")
    for speaker_id, speaker_signals in influencer_signals.items():
        speaker_name = speaker_names[speaker_id]
        signal_types = [s["signal"] for s in speaker_signals]
        signal_counter = Counter(signal_types)
        total_score = sum(s["score"] for s in speaker_signals)
        
        print(f"\n  {speaker_name} ({len(speaker_signals)}개):")
        print(f"    시그널: {dict(signal_counter)}")
        print(f"    총점: {total_score}")
        
        # 최근 시그널 3개만 표시
        recent_signals = sorted(speaker_signals, key=lambda x: x["date"], reverse=True)[:3]
        for i, sig in enumerate(recent_signals):
            print(f"    {i+1}. {sig['date']} | {sig['signal']} | {sig['quote']}")
    
    # 6. 컨센서스 판단
    print(f"\n컨센서스 판단:")
    
    # 매수 계열 vs 매도 계열
    buy_signals = signal_counts.get("강매수", 0) + signal_counts.get("매수", 0) + signal_counts.get("긍정", 0)
    neutral_signals = signal_counts.get("보유", 0) + signal_counts.get("중립", 0)
    sell_signals = signal_counts.get("경계", 0) + signal_counts.get("매도", 0) + signal_counts.get("강매도", 0)
    
    buy_ratio = buy_signals / total_signals if total_signals > 0 else 0
    sell_ratio = sell_signals / total_signals if total_signals > 0 else 0
    
    print(f"  매수 계열: {buy_signals}개 ({buy_ratio*100:.1f}%)")
    print(f"  중립 계열: {neutral_signals}개 ({(neutral_signals/total_signals)*100:.1f}%)")
    print(f"  매도 계열: {sell_signals}개 ({sell_ratio*100:.1f}%)")
    
    # 컨센서스 강도 판단
    consensus_strength = ""
    consensus_direction = ""
    
    if buy_ratio >= 0.7:
        consensus_strength = "강한"
        consensus_direction = "매수"
    elif sell_ratio >= 0.7:
        consensus_strength = "강한"
        consensus_direction = "매도"
    elif buy_ratio >= 0.6:
        consensus_strength = "중간"
        consensus_direction = "매수"
    elif sell_ratio >= 0.6:
        consensus_strength = "중간"
        consensus_direction = "매도"
    elif abs(buy_ratio - sell_ratio) <= 0.2:
        consensus_strength = "약한"
        consensus_direction = "의견분산"
    else:
        consensus_strength = "약한"
        if buy_ratio > sell_ratio:
            consensus_direction = "매수 성향"
        else:
            consensus_direction = "매도 성향"
    
    print(f"\n  결론: {consensus_strength} {consensus_direction} 컨센서스")
    if avg_score > 1:
        print(f"     -> 매우 긍정적 ({avg_score:.2f}점)")
    elif avg_score > 0.5:
        print(f"     -> 긍정적 ({avg_score:.2f}점)")
    elif avg_score > -0.5:
        print(f"     -> 중립적 ({avg_score:.2f}점)")
    elif avg_score > -1:
        print(f"     -> 부정적 ({avg_score:.2f}점)")
    else:
        print(f"     -> 매우 부정적 ({avg_score:.2f}점)")
    
    return {
        "stock_name": stock_name,
        "total_signals": total_signals,
        "unique_influencers": unique_influencers,
        "avg_score": avg_score,
        "signal_distribution": dict(signal_counts),
        "buy_ratio": buy_ratio,
        "sell_ratio": sell_ratio,
        "consensus_strength": consensus_strength,
        "consensus_direction": consensus_direction,
        "influencer_details": influencer_signals
    }

# 각 종목 분석
analysis_results = {}

for stock_name, signals in raw_data.items():
    result = analyze_stock_consensus(stock_name, signals)
    if result:
        analysis_results[stock_name] = result

# 분석 결과 저장
with open("C:\\Users\\Mario\\work\\consensus_analysis_result.json", "w", encoding="utf-8") as f:
    json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)

print(f"\n{'='*50}")
print("전체 요약")
print(f"{'='*50}")

for stock_name, result in analysis_results.items():
    print(f"\n{stock_name}:")
    print(f"  시그널: {result['total_signals']}개 | 유튜버: {result['unique_influencers']}명")
    print(f"  매수비율: {result['buy_ratio']*100:.1f}% | 매도비율: {result['sell_ratio']*100:.1f}%")
    print(f"  컨센서스: {result['consensus_strength']} {result['consensus_direction']}")

print(f"\n분석 완료! 결과 저장: consensus_analysis_result.json")