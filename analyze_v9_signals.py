# -*- coding: utf-8 -*-
import json
from collections import Counter, defaultdict
import sys

def analyze_v9_signals():
    print("=== 파이프라인 V9 시그널 품질 분석 ===")
    
    # JSON 파일 로드
    try:
        with open('pipeline_v9_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: pipeline_v9_results.json 파일을 찾을 수 없습니다.")
        return
    
    print(f"총 분석된 영상 수: {len(data)}개")
    
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
    
    print(f"시그널이 있는 영상: {video_with_signals}개")
    print(f"총 시그널 수: {len(all_signals)}개")
    
    if not all_signals:
        print("분석할 시그널이 없습니다.")
        return
    
    # 1. 시그널 타입 분석
    print("\n1. 시그널 타입 품질 분석:")
    signal_types = Counter(s.get('signal') for s in all_signals)
    valid_v9_types = {'매수', '긍정', '중립', '경계', '매도'}
    old_types = {'STRONG_BUY', 'BUY', 'POSITIVE', 'HOLD', 'NEUTRAL', 'CONCERN', 'SELL', 'STRONG_SELL'}
    
    print("V9 규칙 준수 여부:")
    for signal_type, count in signal_types.most_common():
        if signal_type in valid_v9_types:
            status = "[OK] V9 한글 타입"
        elif signal_type in old_types:
            status = "[ERROR] 구 영문 타입"
        else:
            status = "[ERROR] 알 수 없는 타입"
        print(f"  {status}: {signal_type} - {count}개")
    
    invalid_type_signals = [s for s in all_signals if s.get('signal') not in valid_v9_types]
    print(f"\n❌ V9 규칙 위반 시그널 타입: {len(invalid_type_signals)}개")
    
    # 2. key_quote 품질 분석
    print("\n2. key_quote 품질 분석:")
    empty_quotes = [s for s in all_signals if not s.get('key_quote') or len(s.get('key_quote', '').strip()) < 10]
    print(f"❌ key_quote 부정확 (비어있거나 10자 미만): {len(empty_quotes)}개")
    
    if empty_quotes:
        print("짧은 key_quote 예시:")
        for i, signal in enumerate(empty_quotes[:5]):
            quote = signal.get('key_quote', '(없음)').strip()
            print(f"   {i+1}. {signal.get('speaker')}: '{quote}' (길이: {len(quote)})")
    
    # 3. 타임스탬프 품질 분석
    print("\n3. 타임스탬프 품질 분석:")
    bad_timestamps = [s for s in all_signals if not s.get('timestamp') or s.get('timestamp') in ['00:00', '0:00', '0']]
    print(f"❌ 타임스탬프 이상: {len(bad_timestamps)}개")
    
    if bad_timestamps:
        print("타임스탬프 이상 예시:")
        for i, signal in enumerate(bad_timestamps[:5]):
            ts = signal.get('timestamp', '(없음)')
            print(f"   {i+1}. {signal.get('speaker')}: {signal.get('stock')} - '{ts}'")
    
    # 4. ticker 품질 분석
    print("\n4. ticker 품질 분석:")
    invalid_tickers = [s for s in all_signals if not s.get('ticker') or s.get('ticker') in ['', '없음', 'N/A', '-', 'null']]
    print(f"❌ ticker 이상: {len(invalid_tickers)}개")
    
    ticker_issues = Counter(s.get('ticker', '(없음)') for s in invalid_tickers)
    if ticker_issues:
        print("이상한 ticker 분포:")
        for ticker, count in ticker_issues.most_common(10):
            print(f"   '{ticker}': {count}개")
    
    # 5. 중복 시그널 분석
    print("\n5. 중복 시그널 분석:")
    duplicates = defaultdict(list)
    for signal in all_signals:
        key = (signal.get('video_id'), signal.get('ticker'), signal.get('signal'))
        duplicates[key].append(signal)
    
    duplicate_groups = {k: v for k, v in duplicates.items() if len(v) > 1}
    print(f"❌ 중복 시그널 그룹: {len(duplicate_groups)}개")
    
    if duplicate_groups:
        print("중복 예시:")
        for i, (key, signals_list) in enumerate(list(duplicate_groups.items())[:3]):
            video_id, ticker, signal_type = key
            print(f"   {i+1}. 영상 {video_id}, {ticker}, {signal_type}: {len(signals_list)}개")
    
    # 6. 화자 오류 분석 (채널명과 화자명 비교)
    print("\n6. 화자 오류 분석:")
    speaker_channel_mismatch = []
    for signal in all_signals:
        speaker = signal.get('speaker', '')
        channel = signal.get('channel_name', '')
        
        # 간단한 매칭 로직 (채널명에 화자명이 포함되어야 함)
        if '이효석' in speaker and '이효석' not in channel:
            speaker_channel_mismatch.append(signal)
        elif '슈카' in speaker and '슈카' not in channel:
            speaker_channel_mismatch.append(signal)
    
    print(f"❌ 화자-채널 불일치 (간단 체크): {len(speaker_channel_mismatch)}개")
    
    # 7. mention_type 분포 (V9 규칙 효과 분석)
    print("\n7. mention_type 분포 (V9 규칙 효과):")
    mention_types = Counter(s.get('mention_type') for s in all_signals)
    v9_mention_types = {'결론', '논거', '뉴스', '리포트', '교육', '티저', '보유', '컨센서스', '세무', '차익거래', '시나리오'}
    
    print("mention_type별 분포:")
    for mention_type, count in mention_types.most_common():
        status = "[OK]" if mention_type in v9_mention_types else "[ERROR]"
        print(f"   {status} {mention_type}: {count}개")
    
    # 8. confidence 분포
    print("\n8. confidence 분포:")
    confidences = Counter(s.get('confidence') for s in all_signals)
    v9_confidence_levels = {'very_high', 'high', 'medium', 'low', 'very_low'}
    
    print("confidence별 분포:")
    for conf in ['very_high', 'high', 'medium', 'low', 'very_low']:
        count = confidences.get(conf, 0)
        if count > 0:
            print(f"   {conf}: {count}개")
    
    invalid_confidence = [s for s in all_signals if s.get('confidence') not in v9_confidence_levels]
    if invalid_confidence:
        print(f"❌ 유효하지 않은 confidence: {len(invalid_confidence)}개")
    
    # 9. V9.1 규칙 효과 분석
    print("\n9. V9 → V9.1 추가 규칙 효과 분석:")
    
    # V9.1 추가 규칙 1: 나열형 종목 누락 방지
    conclusion_signals = [s for s in all_signals if s.get('mention_type') == '결론']
    etf_signals = [s for s in all_signals if 'ETF' in str(s.get('stock', '')).upper() or 'ETF' in str(s.get('ticker', '')).upper()]
    medium_analysis_signals = [s for s in all_signals if s.get('mention_type') == '결론' and s.get('confidence') in ['medium', 'high']]
    
    print(f"   - 결론 타입 시그널: {len(conclusion_signals)}개 (V9.1 나열형 종목 규칙)")
    print(f"   - ETF 관련 시그널: {len(etf_signals)}개 (V9.1 ETF 누락 방지)")
    print(f"   - 중간 분석 시그널: {len(medium_analysis_signals)}개 (V9.1 30초~2분 규칙)")
    
    # 10. market 분포
    print("\n10. market 분포:")
    markets = Counter(s.get('market') for s in all_signals)
    v9_markets = {'KR', 'US', 'US_ADR', 'CRYPTO', 'CRYPTO_DEFI', 'SECTOR', 'INDEX', 'ETF', 'OTHER'}
    
    for market, count in markets.most_common():
        status = "[OK]" if market in v9_markets else "[ERROR]"
        print(f"   {status} {market}: {count}개")
    
    # 11. 종합 품질 점수
    print("\n=== 종합 품질 분석 ===")
    total_issues = (
        len(invalid_type_signals) + 
        len(empty_quotes) + 
        len(bad_timestamps) + 
        len(invalid_tickers) + 
        len(duplicate_groups) +
        len(speaker_channel_mismatch) +
        len(invalid_confidence)
    )
    
    quality_score = max(0, (len(all_signals) - total_issues) / len(all_signals) * 100) if len(all_signals) > 0 else 0
    
    print(f"총 시그널: {len(all_signals)}개")
    print(f"품질 이슈: {total_issues}개")
    print(f"품질 점수: {quality_score:.1f}%")
    
    # 12. V10 개선점 제안
    print("\n=== V10 개선점 제안 (프롬프트 약점 분석) ===")
    print("1. [시그널 타입] V9 한글 5단계 강제 적용 - 영문 타입 완전 차단")
    print("2. [key_quote] 최소 길이 15자로 상향 + 의미있는 발언 검증")
    print("3. [타임스탬프] 필수 입력 + '00:00' 금지 + 형식 검증 (MM:SS)")
    print("4. [ticker] 시장별 형식 검증 (KR: 6자리, US: 심볼, CRYPTO: 약어)")
    print("5. [중복 방지] 같은 영상+종목+시그널타입 중복 생성 차단")
    print("6. [mention_type] '결론'과 '논거' 구분 강화 - '결론'은 직접적 투자 조언만")
    print("7. [confidence] 조건부 발언 시 무조건 medium 이하 강제 적용")
    print("8. [화자 정규화] 동일 인물 여러 채널 출연 시 일관된 이름 사용")
    
    # 13. 구체적 예시 제공
    print("\n=== 품질 이슈 구체적 예시 ===")
    
    if invalid_type_signals:
        print("시그널 타입 오류 예시:")
        for i, signal in enumerate(invalid_type_signals[:3]):
            print(f"   {i+1}. {signal.get('speaker')}: {signal.get('stock')} - '{signal.get('signal')}' (V9 규칙 위반)")
    
    if empty_quotes:
        print("\nkey_quote 품질 이슈 예시:")
        for i, signal in enumerate(empty_quotes[:3]):
            quote = signal.get('key_quote', '').strip()
            print(f"   {i+1}. {signal.get('speaker')}: '{quote}' (길이: {len(quote)}자)")
    
    if bad_timestamps:
        print("\n타임스탬프 이슈 예시:")
        for i, signal in enumerate(bad_timestamps[:3]):
            ts = signal.get('timestamp', '')
            print(f"   {i+1}. {signal.get('speaker')}: '{ts}' (영상 시작점 또는 null)")

    # 14. 화자별 시그널 분포
    print("\n=== 화자별 시그널 분포 ===")
    speakers = Counter(s.get('speaker') for s in all_signals)
    print("상위 화자:")
    for speaker, count in speakers.most_common(10):
        print(f"   {speaker}: {count}개")

if __name__ == "__main__":
    analyze_v9_signals()