"""
코린이 아빠 시그널 중복 합치기
- 1영상 1종목 1시그널 원칙 적용
- 같은 video_id + 같은 asset의 시그널들을 1개로 합치기
- 대표 인용구, 최종 방향, 종합 맥락 생성
"""
import json
import os
import sys
import io
from collections import defaultdict
from datetime import datetime

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def get_signal_priority(signal_type):
    """시그널 타입별 우선순위 (강한 신호일수록 높은 점수)"""
    priority_map = {
        'STRONG_BUY': 8,
        'BUY': 7, 
        'POSITIVE': 6,
        'HOLD': 5,
        'NEUTRAL': 4,
        'CONCERN': 3,
        'SELL': 2,
        'STRONG_SELL': 1
    }
    return priority_map.get(signal_type, 0)

def get_confidence_score(confidence_str):
    """신뢰도 문자열을 숫자로 변환"""
    confidence_map = {
        'HIGH': 3,
        'MEDIUM': 2, 
        'LOW': 1
    }
    return confidence_map.get(confidence_str, 1)

def choose_dominant_signal(signals):
    """여러 시그널 중 가장 지배적인 시그널 타입 결정"""
    if not signals:
        return 'NEUTRAL'
    
    # 각 시그널의 가중점수 계산 (우선순위 * 신뢰도)
    signal_scores = defaultdict(float)
    
    for signal in signals:
        signal_type = signal.get('signal_type', 'NEUTRAL')
        confidence = signal.get('confidence', 'LOW')
        
        priority_score = get_signal_priority(signal_type)
        confidence_score = get_confidence_score(confidence)
        
        # 가중점수 = 우선순위 * 신뢰도 가중치
        weighted_score = priority_score * confidence_score
        signal_scores[signal_type] += weighted_score
    
    # 가장 높은 점수의 시그널 타입 반환
    if signal_scores:
        dominant_signal = max(signal_scores.items(), key=lambda x: x[1])
        return dominant_signal[0]
    
    return 'NEUTRAL'

def choose_best_quote(signals):
    """가장 대표적인 인용구 선택"""
    if not signals:
        return ""
    
    # 길이가 적당하고 구체적인 인용구 우선
    quotes_with_scores = []
    
    for signal in signals:
        content = signal.get('content', '').strip()
        if not content:
            continue
        
        # 점수 기준:
        # 1. 적당한 길이 (50-200자)
        # 2. 구체적 언급 ("사라", "팔아라", "매수", "매도" 등)
        # 3. 시그널 강도
        
        score = 0
        length = len(content)
        
        # 길이 점수
        if 50 <= length <= 200:
            score += 3
        elif 20 <= length <= 50:
            score += 2
        elif length > 200:
            score += 1
        
        # 구체적 표현 점수
        action_keywords = ['사라', '팔아라', '매수', '매도', '담아라', '들고가라', '빼라', '올인', '몰빵']
        for keyword in action_keywords:
            if keyword in content:
                score += 2
                break
        
        # 시그널 강도 점수
        signal_type = signal.get('signal_type', 'NEUTRAL')
        score += get_signal_priority(signal_type) * 0.5
        
        quotes_with_scores.append((content, score))
    
    if quotes_with_scores:
        # 가장 높은 점수의 인용구 선택
        best_quote = max(quotes_with_scores, key=lambda x: x[1])
        return best_quote[0]
    
    return signals[0].get('content', '')

def merge_contexts(signals):
    """모든 맥락 정보를 종합"""
    contexts = []
    
    for signal in signals:
        context = signal.get('context', '').strip()
        if context and context not in contexts:
            contexts.append(context)
    
    return ' | '.join(contexts) if contexts else ""

def determine_final_confidence(signals, final_signal_type):
    """최종 신뢰도 결정"""
    if not signals:
        return 'LOW'
    
    # 최종 시그널과 일치하는 시그널들의 신뢰도 고려
    matching_confidences = []
    
    for signal in signals:
        if signal.get('signal_type') == final_signal_type:
            confidence = signal.get('confidence', 'LOW')
            matching_confidences.append(get_confidence_score(confidence))
    
    if not matching_confidences:
        # 일치하는 시그널이 없으면 모든 시그널의 평균 신뢰도
        all_confidences = [get_confidence_score(s.get('confidence', 'LOW')) for s in signals]
        avg_confidence = sum(all_confidences) / len(all_confidences)
    else:
        # 일치하는 시그널의 평균 신뢰도
        avg_confidence = sum(matching_confidences) / len(matching_confidences)
    
    # 숫자를 다시 문자열로 변환
    if avg_confidence >= 2.5:
        return 'HIGH'
    elif avg_confidence >= 1.5:
        return 'MEDIUM'
    else:
        return 'LOW'

def merge_duplicate_signals(signals):
    """중복 시그널 합치기"""
    print(f"📊 원본 시그널: {len(signals)}개")
    
    # video_id + asset별로 그룹화
    grouped_signals = defaultdict(list)
    
    for i, signal in enumerate(signals):
        video_id = signal.get('video_id', '')
        asset = signal.get('asset', '').strip().lower()  # 대소문자 통일
        
        # 자산명 정규화 (유사한 표기 통합)
        asset_normalized = normalize_asset_name(asset)
        
        key = f"{video_id}||{asset_normalized}"
        signal['original_index'] = i  # 원본 인덱스 보존
        grouped_signals[key].append(signal)
    
    print(f"🔄 그룹화 결과: {len(grouped_signals)}개 그룹")
    
    merged_signals = []
    merge_stats = {
        'total_groups': len(grouped_signals),
        'merged_groups': 0,
        'single_signal_groups': 0,
        'max_signals_in_group': 0,
        'total_original': len(signals),
        'total_merged': 0
    }
    
    for key, group_signals in grouped_signals.items():
        video_id, asset_normalized = key.split('||')
        
        if len(group_signals) == 1:
            # 단일 시그널은 그대로 유지
            merged_signal = group_signals[0].copy()
            merge_stats['single_signal_groups'] += 1
        else:
            # 다중 시그널 합치기
            print(f"🔀 합치기: {asset_normalized} in {video_id} - {len(group_signals)}개 시그널")
            merge_stats['merged_groups'] += 1
            merge_stats['max_signals_in_group'] = max(merge_stats['max_signals_in_group'], len(group_signals))
            
            # 기본 정보는 첫 번째 시그널에서
            base_signal = group_signals[0]
            
            # 최종 시그널 타입 결정
            final_signal_type = choose_dominant_signal(group_signals)
            
            # 대표 인용구 선택
            best_quote = choose_best_quote(group_signals)
            
            # 맥락 합치기
            merged_context = merge_contexts(group_signals)
            
            # 최종 신뢰도 결정
            final_confidence = determine_final_confidence(group_signals, final_signal_type)
            
            # 원본 인덱스들 기록
            original_indices = [s['original_index'] for s in group_signals]
            
            merged_signal = {
                'asset': base_signal.get('asset', ''),  # 원본 표기 유지
                'signal_type': final_signal_type,
                'content': best_quote,
                'confidence': final_confidence,
                'context': merged_context,
                'video_id': video_id,
                'title': base_signal.get('title', ''),
                'merged_from_indices': original_indices,
                'merged_from_count': len(group_signals),
                'original_signals': [
                    {
                        'signal_type': s.get('signal_type'),
                        'content': s.get('content', '')[:100] + '...' if len(s.get('content', '')) > 100 else s.get('content', ''),
                        'confidence': s.get('confidence')
                    } for s in group_signals
                ]
            }
        
        merged_signals.append(merged_signal)
    
    merge_stats['total_merged'] = len(merged_signals)
    
    print(f"✅ 합치기 완료:")
    print(f"   - 원본: {merge_stats['total_original']}개")
    print(f"   - 합친 결과: {merge_stats['total_merged']}개") 
    print(f"   - 단일 그룹: {merge_stats['single_signal_groups']}개")
    print(f"   - 합쳐진 그룹: {merge_stats['merged_groups']}개")
    print(f"   - 최대 합친 개수: {merge_stats['max_signals_in_group']}개")
    
    return merged_signals, merge_stats

def normalize_asset_name(asset_name):
    """자산명 정규화 (유사한 표기 통합)"""
    asset_name = asset_name.lower().strip()
    
    # 공통 정규화 규칙
    normalizations = {
        '이더륨': '이더리움',
        'ethereum': '이더리움',
        'bitcoin': '비트코인',
        'btc': '비트코인',
        'eth': '이더리움',
        'xrp': 'xrp',
        'ripple': 'xrp',
        '비트마인': '비트마인',
        'bitmine': '비트마인',
        'bmnr': '비트마인',
        'bmr': '비트마인',
        'bm': '비트마인',
        '켄톤': '켄톤',
        'canton': '켄톤',
        'cc코인': 'cc코인',
        'cctoken': 'cc코인'
    }
    
    for original, normalized in normalizations.items():
        if original in asset_name:
            return normalized
    
    return asset_name

def save_merged_signals(merged_signals, merge_stats):
    """합친 시그널 저장"""
    output_data = {
        'metadata': {
            'merge_timestamp': str(datetime.now()),
            'merge_rule': '1영상 1종목 1시그널',
            'total_original': merge_stats['total_original'],
            'total_merged': merge_stats['total_merged'],
            'compression_ratio': f"{merge_stats['total_merged']}/{merge_stats['total_original']} ({(merge_stats['total_merged']/merge_stats['total_original']*100):.1f}%)"
        },
        'merge_stats': merge_stats,
        'signals': merged_signals
    }
    
    # 합친 시그널 저장
    output_file = 'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\_merged_signals.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 합친 시그널 저장: {output_file}")
    
    # 시그널만 따로 저장 (Claude 검증용)
    signal_only_file = 'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\_merged_signals_only.json'  
    with open(signal_only_file, 'w', encoding='utf-8') as f:
        json.dump(merged_signals, f, indent=2, ensure_ascii=False)
    
    print(f"💾 시그널만 저장: {signal_only_file}")
    
    return output_file

def generate_merge_report(merged_signals, merge_stats):
    """합치기 보고서 생성"""
    
    # 합쳐진 그룹 분석
    merged_groups = [s for s in merged_signals if s.get('merged_from_count', 1) > 1]
    
    report = f"""# 📊 코린이 아빠 시그널 중복 합치기 보고서

## 🎯 합치기 규칙
- **1영상 1종목 1시그널** 원칙 적용
- 같은 video_id + 같은 asset의 시그널들을 1개로 통합
- 가장 강한 시그널 타입 우선 (STRONG_BUY > BUY > ... > STRONG_SELL)
- 대표 인용구 선택 (구체적이고 명확한 표현 우선)
- 모든 맥락 정보 종합

## 📈 합치기 결과

### 전체 통계
- **원본 시그널**: {merge_stats['total_original']}개
- **합친 결과**: {merge_stats['total_merged']}개
- **압축률**: {(merge_stats['total_merged']/merge_stats['total_original']*100):.1f}%
- **단일 시그널 그룹**: {merge_stats['single_signal_groups']}개
- **합쳐진 그룹**: {merge_stats['merged_groups']}개

### 주요 통합 사례 (상위 10개)
"""
    
    # 가장 많이 합쳐진 그룹들 표시
    top_merged = sorted(merged_groups, key=lambda x: x.get('merged_from_count', 1), reverse=True)[:10]
    
    for i, signal in enumerate(top_merged, 1):
        asset = signal.get('asset', 'N/A')
        video_id = signal.get('video_id', 'N/A')
        count = signal.get('merged_from_count', 1)
        final_type = signal.get('signal_type', 'N/A')
        
        report += f"\n{i}. **{asset}** ({video_id}) - {count}개 → {final_type}\n"
        
        original_types = [s['signal_type'] for s in signal.get('original_signals', [])]
        if original_types:
            report += f"   원본: {' + '.join(original_types)}\n"
        
        content = signal.get('content', '')
        if content:
            report += f"   대표 인용: \"{content[:100]}{'...' if len(content) > 100 else ''}\"\n"

    # 종목별 통계
    asset_counts = {}
    for signal in merged_signals:
        asset = signal.get('asset', 'UNKNOWN')
        asset_counts[asset] = asset_counts.get(asset, 0) + 1
    
    top_assets = sorted(asset_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    report += f"""

### 종목별 시그널 분포 (상위 10개)
"""
    
    for i, (asset, count) in enumerate(top_assets, 1):
        percentage = (count / len(merged_signals)) * 100
        report += f"{i}. **{asset}**: {count}개 ({percentage:.1f}%)\n"

    # 시그널 타입별 분포
    signal_type_counts = {}
    for signal in merged_signals:
        signal_type = signal.get('signal_type', 'UNKNOWN')
        signal_type_counts[signal_type] = signal_type_counts.get(signal_type, 0) + 1
    
    report += f"""

### 최종 시그널 타입 분포
"""
    
    for signal_type, count in sorted(signal_type_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(merged_signals)) * 100
        report += f"- **{signal_type}**: {count}개 ({percentage:.1f}%)\n"

    report += f"""

## 💡 다음 단계
1. 합친 시그널 {merge_stats['total_merged']}개에 대해 Claude 검증 실행
2. 타임스탬프 추출 (1영상 1종목당 1개만)
3. HTML 리뷰 페이지 업데이트
4. 최종 보고서 생성

---
생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # 보고서 저장
    report_file = "C:\\Users\\Mario\\work\\invest-sns\\MERGE_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 합치기 보고서 생성: {report_file}")
    return report_file

def main():
    """메인 실행"""
    print("🔀 코린이 아빠 시그널 중복 합치기 시작")
    print("📋 규칙: 1영상 1종목 1시그널")
    
    # 원본 시그널 로드
    signal_file = 'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\_all_signals_194.json'
    
    if not os.path.exists(signal_file):
        print(f"❌ 원본 시그널 파일 없음: {signal_file}")
        return
    
    with open(signal_file, 'r', encoding='utf-8') as f:
        original_signals = json.load(f)
    
    # 중복 합치기
    merged_signals, merge_stats = merge_duplicate_signals(original_signals)
    
    # 결과 저장
    output_file = save_merged_signals(merged_signals, merge_stats)
    
    # 보고서 생성
    report_file = generate_merge_report(merged_signals, merge_stats)
    
    print(f"\n✅ 시그널 합치기 완료!")
    print(f"📊 결과: {merge_stats['total_original']}개 → {merge_stats['total_merged']}개")
    print(f"📁 파일:")
    print(f"   - 합친 시그널: _merged_signals.json")
    print(f"   - 시그널만: _merged_signals_only.json")
    print(f"   - 보고서: MERGE_REPORT.md")

if __name__ == "__main__":
    main()