"""
코린이 아빠 시그널 품질 상세 분석
- 종목별, 시그널 타입별 품질 분석
- 문제가 있는 시그널 식별
- 개선 가능 영역 발견
"""
import json
import os
import sys
import io
from collections import defaultdict, Counter
import re

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def load_verification_data():
    """검증 데이터 로드"""
    base_path = "C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106"
    
    # Claude 검증 결과
    claude_file = f"{base_path}\\_claude_verify_full.json"
    claude_data = None
    
    if os.path.exists(claude_file):
        with open(claude_file, 'r', encoding='utf-8') as f:
            claude_data = json.load(f)
    
    return claude_data

def analyze_by_asset(claude_data):
    """종목별 품질 분석"""
    if not claude_data or 'results' not in claude_data:
        return {}
    
    asset_analysis = defaultdict(lambda: {
        'total': 0,
        'confirmed': 0,
        'corrected': 0,
        'rejected': 0,
        'errors': 0,
        'avg_confidence': 0,
        'confidence_sum': 0,
        'signal_types': Counter(),
        'problem_signals': []
    })
    
    for result in claude_data['results']:
        original_signal = result.get('original_signal', {})
        claude_verification = result.get('claude_verification', {})
        
        asset = original_signal.get('asset', 'UNKNOWN')
        signal_type = original_signal.get('signal_type', 'UNKNOWN')
        verdict = claude_verification.get('verdict', 'error')
        confidence = claude_verification.get('confidence', 0)
        
        asset_stats = asset_analysis[asset]
        asset_stats['total'] += 1
        asset_stats['signal_types'][signal_type] += 1
        asset_stats['confidence_sum'] += confidence
        
        if verdict in ['confirmed', 'corrected', 'rejected', 'errors']:
            asset_stats[verdict] += 1
        else:
            asset_stats['errors'] += 1
        
        # 문제 시그널 수집 (낮은 신뢰도, 거부/수정됨)
        if confidence < 0.7 or verdict in ['corrected', 'rejected']:
            asset_stats['problem_signals'].append({
                'signal_index': result.get('signal_index'),
                'signal_type': signal_type,
                'verdict': verdict,
                'confidence': confidence,
                'reason': claude_verification.get('reason', ''),
                'content': original_signal.get('content', '')[:100] + '...'
            })
    
    # 평균 신뢰도 계산
    for asset, stats in asset_analysis.items():
        if stats['total'] > 0:
            stats['avg_confidence'] = stats['confidence_sum'] / stats['total']
            stats['quality_score'] = (stats['confirmed'] / stats['total']) * stats['avg_confidence']
    
    return dict(asset_analysis)

def analyze_by_signal_type(claude_data):
    """시그널 타입별 품질 분석"""
    if not claude_data or 'results' not in claude_data:
        return {}
    
    signal_analysis = defaultdict(lambda: {
        'total': 0,
        'confirmed': 0,
        'corrected': 0,
        'rejected': 0,
        'errors': 0,
        'avg_confidence': 0,
        'confidence_sum': 0,
        'assets': Counter(),
        'problem_reasons': Counter()
    })
    
    for result in claude_data['results']:
        original_signal = result.get('original_signal', {})
        claude_verification = result.get('claude_verification', {})
        
        asset = original_signal.get('asset', 'UNKNOWN')
        signal_type = original_signal.get('signal_type', 'UNKNOWN')
        verdict = claude_verification.get('verdict', 'error')
        confidence = claude_verification.get('confidence', 0)
        reason = claude_verification.get('reason', '')
        
        signal_stats = signal_analysis[signal_type]
        signal_stats['total'] += 1
        signal_stats['assets'][asset] += 1
        signal_stats['confidence_sum'] += confidence
        
        if verdict in ['confirmed', 'corrected', 'rejected', 'errors']:
            signal_stats[verdict] += 1
        else:
            signal_stats['errors'] += 1
        
        # 문제 이유 수집
        if verdict in ['corrected', 'rejected']:
            signal_stats['problem_reasons'][reason[:50]] += 1
    
    # 평균 신뢰도 계산
    for signal_type, stats in signal_analysis.items():
        if stats['total'] > 0:
            stats['avg_confidence'] = stats['confidence_sum'] / stats['total']
            stats['success_rate'] = (stats['confirmed'] / stats['total']) * 100
    
    return dict(signal_analysis)

def find_problematic_patterns(claude_data):
    """문제가 있는 패턴 식별"""
    if not claude_data or 'results' not in claude_data:
        return {}
    
    patterns = {
        'low_confidence_signals': [],
        'rejected_signals': [],
        'corrected_signals': [],
        'common_issues': Counter(),
        'asset_issues': defaultdict(list),
        'video_issues': defaultdict(int)
    }
    
    for result in claude_data['results']:
        original_signal = result.get('original_signal', {})
        claude_verification = result.get('claude_verification', {})
        
        signal_index = result.get('signal_index')
        asset = original_signal.get('asset', 'UNKNOWN')
        video_id = original_signal.get('video_id', 'UNKNOWN')
        verdict = claude_verification.get('verdict', 'error')
        confidence = claude_verification.get('confidence', 0)
        reason = claude_verification.get('reason', '')
        
        # 낮은 신뢰도 시그널
        if confidence < 0.7:
            patterns['low_confidence_signals'].append({
                'index': signal_index,
                'asset': asset,
                'confidence': confidence,
                'verdict': verdict,
                'reason': reason
            })
        
        # 거부된 시그널
        if verdict == 'rejected':
            patterns['rejected_signals'].append({
                'index': signal_index,
                'asset': asset,
                'reason': reason,
                'content': original_signal.get('content', '')[:100]
            })
        
        # 수정된 시그널
        if verdict == 'corrected':
            patterns['corrected_signals'].append({
                'index': signal_index,
                'asset': asset,
                'reason': reason,
                'corrected_asset': claude_verification.get('corrected_asset', ''),
                'corrected_signal': claude_verification.get('corrected_signal', '')
            })
        
        # 공통 이슈 패턴
        if verdict in ['corrected', 'rejected']:
            patterns['common_issues'][reason[:100]] += 1
            patterns['asset_issues'][asset].append(reason)
            patterns['video_issues'][video_id] += 1
    
    return patterns

def generate_quality_report(asset_analysis, signal_analysis, patterns):
    """품질 분석 보고서 생성"""
    report = f"""# 🔍 코린이 아빠 시그널 품질 상세 분석

## 📊 종목별 품질 분석

### 상위 품질 종목 (품질점수 = 확인률 × 평균신뢰도)
"""
    
    # 종목별 품질 순위
    asset_quality = [(asset, stats['quality_score']) for asset, stats in asset_analysis.items() if stats['total'] >= 2]
    asset_quality.sort(key=lambda x: x[1], reverse=True)
    
    for i, (asset, quality) in enumerate(asset_quality[:10], 1):
        stats = asset_analysis[asset]
        confirmed_rate = (stats['confirmed'] / stats['total']) * 100
        report += f"{i}. **{asset}** (품질점수: {quality:.3f})\n"
        report += f"   - 총 {stats['total']}개, 확인률 {confirmed_rate:.1f}%, 평균신뢰도 {stats['avg_confidence']:.3f}\n"
        report += f"   - 시그널 분포: {dict(stats['signal_types'])}\n\n"

    # 문제 종목
    problem_assets = [(asset, stats) for asset, stats in asset_analysis.items() 
                     if stats['total'] >= 2 and (stats['rejected'] > 0 or stats['corrected'] >= stats['total']*0.3)]
    
    if problem_assets:
        report += f"""
### ⚠️ 문제 종목 ({len(problem_assets)}개)
"""
        for asset, stats in problem_assets[:5]:
            issue_rate = ((stats['corrected'] + stats['rejected']) / stats['total']) * 100
            report += f"- **{asset}**: 총 {stats['total']}개 중 {issue_rate:.1f}% 문제 (수정 {stats['corrected']}, 거부 {stats['rejected']})\n"

    # 시그널 타입별 분석
    report += f"""

## 📈 시그널 타입별 품질 분석

### 성공률 순위
"""
    
    signal_success = [(signal_type, stats['success_rate']) for signal_type, stats in signal_analysis.items() 
                     if stats['total'] >= 3]
    signal_success.sort(key=lambda x: x[1], reverse=True)
    
    for i, (signal_type, success_rate) in enumerate(signal_success, 1):
        stats = signal_analysis[signal_type]
        report += f"{i}. **{signal_type}**: {success_rate:.1f}% 성공률 (총 {stats['total']}개)\n"
        report += f"   - 평균 신뢰도: {stats['avg_confidence']:.3f}\n"
        report += f"   - 주요 종목: {', '.join([asset for asset, _ in stats['assets'].most_common(3)])}\n\n"

    # 문제 패턴 분석
    report += f"""

## 🚨 문제 패턴 분석

### 낮은 신뢰도 시그널 ({len(patterns['low_confidence_signals'])}개)
"""
    
    if patterns['low_confidence_signals']:
        for signal in patterns['low_confidence_signals'][:5]:
            report += f"- 시그널 #{signal['index']}: {signal['asset']} (신뢰도: {signal['confidence']:.2f})\n"
            report += f"  이유: {signal['reason'][:100]}\n\n"

    report += f"""
### 거부된 시그널 ({len(patterns['rejected_signals'])}개)
"""
    
    if patterns['rejected_signals']:
        for signal in patterns['rejected_signals'][:3]:
            report += f"- 시그널 #{signal['index']}: {signal['asset']}\n"
            report += f"  이유: {signal['reason']}\n"
            report += f"  내용: {signal['content']}\n\n"

    report += f"""
### 수정된 시그널 ({len(patterns['corrected_signals'])}개)
"""
    
    if patterns['corrected_signals']:
        for signal in patterns['corrected_signals'][:3]:
            report += f"- 시그널 #{signal['index']}: {signal['asset']}\n"
            report += f"  이유: {signal['reason']}\n"
            if signal['corrected_asset']:
                report += f"  수정된 종목: {signal['corrected_asset']}\n"
            if signal['corrected_signal']:
                report += f"  수정된 시그널: {signal['corrected_signal']}\n"
            report += "\n"

    # 공통 이슈
    report += f"""
### 가장 흔한 문제들
"""
    
    for issue, count in patterns['common_issues'].most_common(5):
        report += f"- **{count}회**: {issue}\n"

    # 문제가 많은 비디오
    problem_videos = [(video_id, count) for video_id, count in patterns['video_issues'].items() if count >= 2]
    problem_videos.sort(key=lambda x: x[1], reverse=True)
    
    if problem_videos:
        report += f"""

### 문제가 많은 비디오
"""
        for video_id, count in problem_videos[:5]:
            report += f"- **{video_id}**: {count}개 문제\n"

    return report

def main():
    """메인 실행 함수"""
    print("🔍 코린이 아빠 시그널 품질 상세 분석 시작...")
    
    # 데이터 로드
    claude_data = load_verification_data()
    
    if not claude_data:
        print("❌ Claude 검증 데이터가 없습니다. 검증이 완료된 후 실행해주세요.")
        return
    
    # 분석 수행
    print("📊 종목별 분석 중...")
    asset_analysis = analyze_by_asset(claude_data)
    
    print("📈 시그널 타입별 분석 중...")
    signal_analysis = analyze_by_signal_type(claude_data)
    
    print("🚨 문제 패턴 식별 중...")
    patterns = find_problematic_patterns(claude_data)
    
    # 보고서 생성
    print("📝 품질 보고서 생성 중...")
    report = generate_quality_report(asset_analysis, signal_analysis, patterns)
    
    # 보고서 저장
    report_file = "C:\\Users\\Mario\\work\\invest-sns\\QUALITY_ANALYSIS.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 품질 분석 완료: {report_file}")
    
    # 요약 출력
    total_signals = len(claude_data.get('results', []))
    problem_count = len(patterns['rejected_signals']) + len(patterns['corrected_signals'])
    
    print(f"\n📊 품질 분석 요약:")
    print(f"   - 총 시그널: {total_signals}개")
    print(f"   - 문제 시그널: {problem_count}개 ({problem_count/total_signals*100:.1f}%)")
    print(f"   - 분석된 종목: {len(asset_analysis)}개")
    print(f"   - 시그널 타입: {len(signal_analysis)}개")

if __name__ == "__main__":
    main()