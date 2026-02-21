#!/usr/bin/env python3
"""
파이프라인 최종 요약 보고서
"""
import json
import os
import sys
import io
from collections import Counter, defaultdict

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def analyze_dedup_results():
    """1단계: 중복 제거 결과 분석"""
    if not os.path.exists("_deduped_signals.json"):
        return None
    
    with open("_deduped_signals.json", 'r', encoding='utf-8') as f:
        deduped = json.load(f)
    
    merged_count = sum(1 for signal in deduped if signal.get('merged_from_count', 1) > 1)
    
    return {
        'total_signals': len(deduped),
        'merged_signals': merged_count,
        'reduction_count': 194 - len(deduped)
    }

def analyze_timestamp_results():
    """2단계: 타임스탬프 매핑 결과 분석"""
    if not os.path.exists("_signals_with_timestamps.json"):
        return None
    
    with open("_signals_with_timestamps.json", 'r', encoding='utf-8') as f:
        timestamped = json.load(f)
    
    with_timestamp = sum(1 for signal in timestamped if signal.get('timestamp_seconds') is not None)
    avg_similarity = sum(signal.get('timestamp_similarity', 0) for signal in timestamped if signal.get('timestamp_similarity')) / len([s for s in timestamped if s.get('timestamp_similarity')])
    
    return {
        'total_signals': len(timestamped),
        'with_timestamp': with_timestamp,
        'match_rate': with_timestamp / len(timestamped) * 100,
        'avg_similarity': avg_similarity
    }

def analyze_claude_results():
    """3단계: Claude 검증 결과 분석"""
    if not os.path.exists("_claude_verify_full.json"):
        return None
    
    with open("_claude_verify_full.json", 'r', encoding='utf-8') as f:
        claude_results = json.load(f)
    
    judgments = [signal.get('claude_verification', {}).get('judgment') for signal in claude_results]
    judgment_counts = Counter(judgments)
    
    confidences = [signal.get('claude_verification', {}).get('confidence', 0) for signal in claude_results if signal.get('claude_verification', {}).get('confidence')]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    # 비용 추정
    total_cost = 0
    for signal in claude_results:
        subtitle_content = ""  # 실제로는 자막 내용 길이를 계산해야 함
        input_tokens = len(str(signal)) // 4  # 대략적 추정
        output_tokens = len(str(signal.get('claude_verification', {}))) // 4
        cost = (input_tokens * 0.00000025) + (output_tokens * 0.00000125)  # Haiku 가격
        total_cost += cost
    
    return {
        'total_signals': len(claude_results),
        'judgment_counts': dict(judgment_counts),
        'avg_confidence': avg_confidence,
        'estimated_cost': total_cost
    }

def print_summary():
    """최종 요약 출력"""
    print("=" * 60)
    print("🎯 코린이 아빠 시그널 파이프라인 실행 완료")
    print("=" * 60)
    
    # 1단계: 중복 제거
    dedup = analyze_dedup_results()
    if dedup:
        print(f"\n📝 1단계: 중복 제거")
        print(f"   • 원본 시그널: 194개")
        print(f"   • 중복 제거 후: {dedup['total_signals']}개")
        print(f"   • 합쳐진 시그널: {dedup['merged_signals']}개")
        print(f"   • 감소량: {dedup['reduction_count']}개")
    else:
        print(f"\n📝 1단계: 중복 제거 - ❌ 결과 파일 없음")
    
    # 2단계: 타임스탬프 매핑
    timestamp = analyze_timestamp_results()
    if timestamp:
        print(f"\n⏰ 2단계: 타임스탬프 매핑")
        print(f"   • 전체 시그널: {timestamp['total_signals']}개")
        print(f"   • 타임스탬프 매핑: {timestamp['with_timestamp']}개")
        print(f"   • 매핑 성공률: {timestamp['match_rate']:.1f}%")
        print(f"   • 평균 유사도: {timestamp['avg_similarity']:.3f}")
    else:
        print(f"\n⏰ 2단계: 타임스탬프 매핑 - ❌ 결과 파일 없음")
    
    # 3단계: Claude 검증
    claude = analyze_claude_results()
    if claude:
        print(f"\n🤖 3단계: Claude 검증")
        print(f"   • 검증된 시그널: {claude['total_signals']}개")
        print(f"   • 평균 신뢰도: {claude['avg_confidence']:.3f}")
        print(f"   • 예상 비용: ${claude['estimated_cost']:.3f}")
        print(f"\n   판정 분포:")
        for judgment, count in claude['judgment_counts'].items():
            if judgment:
                percentage = count / claude['total_signals'] * 100
                emoji = {'confirmed': '✅', 'corrected': '🔧', 'rejected': '❌', 'error': '⚠️'}.get(judgment, '❓')
                print(f"   • {emoji} {judgment}: {count}개 ({percentage:.1f}%)")
    else:
        print(f"\n🤖 3단계: Claude 검증 - ❌ 진행 중 또는 결과 파일 없음")
        
        # 진행 중인 경우 진행률 표시
        if os.path.exists("_claude_progress.json"):
            with open("_claude_progress.json", 'r', encoding='utf-8') as f:
                progress = json.load(f)
            processed = progress.get('processed', 0)
            total = 164  # 알려진 전체 시그널 수
            print(f"   • 진행 상황: {processed}/{total} ({processed/total*100:.1f}%)")
    
    # 4단계: HTML 리뷰 페이지
    html_path = "C:\\Users\\Mario\\work\\invest-sns\\signal-review.html"
    if os.path.exists(html_path):
        file_size = os.path.getsize(html_path)
        print(f"\n📊 4단계: 리뷰 페이지")
        print(f"   • HTML 파일: {html_path}")
        print(f"   • 파일 크기: {file_size:,} bytes")
        print(f"   • 상태: ✅ 생성 완료")
    else:
        print(f"\n📊 4단계: 리뷰 페이지 - ❌ 아직 생성되지 않음")
    
    print(f"\n🎉 파이프라인 실행 요약:")
    if dedup and timestamp and claude:
        print(f"   • 최종 시그널 수: {claude['total_signals']}개")
        print(f"   • 중복 제거: -{dedup['reduction_count']}개")
        print(f"   • 타임스탬프 매핑: {timestamp['with_timestamp']}개 성공")
        print(f"   • Claude 확인됨: {claude['judgment_counts'].get('confirmed', 0)}개")
        print(f"   • Claude 수정필요: {claude['judgment_counts'].get('corrected', 0)}개")
        print(f"   • 예상 비용: ${claude['estimated_cost']:.3f}")
    else:
        print(f"   • 일부 단계가 아직 완료되지 않았습니다.")
    
    print("=" * 60)

if __name__ == "__main__":
    print_summary()