# -*- coding: utf-8 -*-
import requests
import json
from collections import Counter
import sys
import io

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"

headers = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
}

def get_signals():
    """전체 시그널 조회"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/signals?select=*",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

def get_videos():
    """전체 비디오 정보 조회"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/videos?select=id,title,channel_id",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

def analyze_signal_quality():
    print("Supabase 시그널 품질 분석 시작...")
    
    # 데이터 로드
    signals = get_signals()
    videos = get_videos()
    
    if not signals:
        print("❌ 시그널 데이터를 불러올 수 없습니다.")
        return
    
    # 비디오 데이터를 딕셔너리로 변환
    video_dict = {v['id']: v for v in videos}
    
    print(f"📊 총 시그널 수: {len(signals)}개")
    print(f"📊 총 비디오 수: {len(videos)}개")
    
    # 1. 시그널 타입 분석
    print("\n1️⃣ 시그널 타입 분석:")
    signal_types = Counter(s.get('signal_type') for s in signals)
    valid_types = {'STRONG_BUY', 'BUY', 'POSITIVE', 'HOLD', 'NEUTRAL', 'CONCERN', 'SELL', 'STRONG_SELL'}
    
    print("시그널 타입별 분포:")
    for signal_type, count in signal_types.most_common():
        status = "✅" if signal_type in valid_types else "❌"
        print(f"  {status} {signal_type}: {count}개")
    
    invalid_signals = [s for s in signals if s.get('signal_type') not in valid_types]
    print(f"\n❌ 유효하지 않은 시그널 타입: {len(invalid_signals)}개")
    if invalid_signals:
        for signal in invalid_signals[:5]:
            print(f"   - {signal.get('signal_type')}: {signal.get('ticker')} ({signal.get('speaker')})")
    
    # 2. key_quote 품질 분석  
    print("\n2️⃣ key_quote 품질 분석:")
    empty_quotes = [s for s in signals if not s.get('key_quote') or len(s.get('key_quote', '')) < 10]
    print(f"❌ key_quote 부정확 (비어있거나 10자 미만): {len(empty_quotes)}개")
    
    if empty_quotes:
        print("예시:")
        for signal in empty_quotes[:5]:
            quote = signal.get('key_quote', '(없음)')
            print(f"   - {signal.get('speaker')}: '{quote}' (길이: {len(quote)})")
    
    # 3. 타임스탬프 분석
    print("\n3️⃣ 타임스탬프 분석:")
    bad_timestamps = [s for s in signals if not s.get('timestamp') or s.get('timestamp') in ['00:00', '0:00', '0']]
    print(f"❌ 타임스탬프 이상: {len(bad_timestamps)}개")
    
    if bad_timestamps:
        print("예시:")
        for signal in bad_timestamps[:5]:
            ts = signal.get('timestamp', '(없음)')
            print(f"   - {signal.get('speaker')}: {signal.get('ticker')} - {ts}")
    
    # 4. ticker 품질 분석
    print("\n4️⃣ ticker 품질 분석:")
    invalid_tickers = [s for s in signals if not s.get('ticker') or s.get('ticker') in ['', '없음', 'N/A', '-', 'null']]
    print(f"❌ ticker 이상: {len(invalid_tickers)}개")
    
    ticker_counter = Counter(s.get('ticker') for s in invalid_tickers)
    if invalid_tickers:
        print("이상한 ticker 분포:")
        for ticker, count in ticker_counter.most_common(10):
            print(f"   - '{ticker}': {count}개")
    
    # 5. 중복 분석
    print("\n5️⃣ 중복 시그널 분석:")
    duplicates = {}
    for signal in signals:
        key = (signal.get('video_id'), signal.get('ticker'), signal.get('signal_type'))
        if key not in duplicates:
            duplicates[key] = []
        duplicates[key].append(signal)
    
    duplicate_groups = {k: v for k, v in duplicates.items() if len(v) > 1}
    print(f"❌ 중복 시그널 그룹: {len(duplicate_groups)}개")
    
    if duplicate_groups:
        print("중복 예시:")
        for i, (key, signals_list) in enumerate(list(duplicate_groups.items())[:3]):
            video_id, ticker, signal_type = key
            print(f"   - 영상ID {video_id}, {ticker}, {signal_type}: {len(signals_list)}개")
    
    # 6. 화자 분석  
    print("\n6️⃣ 화자 분석:")
    speakers = Counter(s.get('speaker') for s in signals)
    print("상위 화자:")
    for speaker, count in speakers.most_common(10):
        print(f"   - {speaker}: {count}개")
    
    # 7. mention_type 분석 (V9 규칙 효과)
    print("\n7️⃣ mention_type 분포 (V9 규칙 효과):")
    mention_types = Counter(s.get('mention_type') for s in signals)
    print("mention_type별 분포:")
    for mention_type, count in mention_types.most_common():
        print(f"   - {mention_type}: {count}개")
    
    # 8. confidence 분석
    print("\n8️⃣ confidence 분포:")
    confidences = Counter(s.get('confidence') for s in signals)
    confidence_order = ['very_high', 'high', 'medium', 'low', 'very_low']
    print("confidence별 분포:")
    for conf in confidence_order:
        if conf in confidences:
            print(f"   - {conf}: {confidences[conf]}개")
    
    # 9. 최신 시그널 예시
    print("\n9️⃣ 최신 시그널 예시 (5개):")
    sorted_signals = sorted(signals, key=lambda x: x.get('created_at', ''), reverse=True)
    for i, signal in enumerate(sorted_signals[:5]):
        video_title = video_dict.get(signal.get('video_id'), {}).get('title', '제목 없음')
        print(f"{i+1}. {signal.get('speaker')}: {signal.get('ticker')} - {signal.get('signal_type')}")
        print(f"   영상: {video_title[:50]}...")
        print(f"   인용: {signal.get('key_quote', '')[:50]}...")
    
    # 10. 종합 품질 점수
    print("\n🏆 종합 품질 분석:")
    total_signals = len(signals)
    issues = len(invalid_signals) + len(empty_quotes) + len(bad_timestamps) + len(invalid_tickers) + len(duplicate_groups)
    quality_score = max(0, (total_signals - issues) / total_signals * 100) if total_signals > 0 else 0
    
    print(f"총 시그널: {total_signals}개")
    print(f"품질 이슈: {issues}개")
    print(f"품질 점수: {quality_score:.1f}%")
    
    print("\n📋 V10 개선점 제안:")
    print("1. 시그널 타입 검증 강화 - 8가지 고정 타입만 허용")
    print("2. key_quote 최소 길이 검증 (15자 이상)")  
    print("3. 타임스탬프 필수 입력 및 형식 검증")
    print("4. ticker 유효성 검증 (시장별 형식 체크)")
    print("5. 영상+종목+시그널타입 중복 방지 로직")
    print("6. mention_type과 signal_type 일관성 검증")

if __name__ == "__main__":
    analyze_signal_quality()