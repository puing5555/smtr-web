#!/usr/bin/env python3
import json
import os
from collections import defaultdict

def merge_signals(signals):
    """같은 video_id + asset의 시그널들을 1개로 합치기"""
    # video_id + asset로 그룹핑
    groups = defaultdict(list)
    for signal in signals:
        key = f"{signal['video_id']}_{signal['asset']}"
        groups[key].append(signal)
    
    deduped = []
    for key, signal_list in groups.items():
        if len(signal_list) == 1:
            # 중복 없음, 그대로 유지
            deduped.append(signal_list[0])
        else:
            # 중복 있음, 합치기
            print(f"Merging {len(signal_list)} signals for {key}")
            
            # 대표 시그널 선택 (가장 긴 content를 가진 것)
            representative = max(signal_list, key=lambda s: len(s.get('content', '')))
            
            # 모든 content를 수집해서 맥락 정보로 활용
            all_contents = [s['content'] for s in signal_list if s.get('content')]
            all_contexts = [s.get('context', '') for s in signal_list if s.get('context')]
            
            # 합친 시그널 생성
            merged = representative.copy()
            merged['merged_from_count'] = len(signal_list)
            merged['all_contents'] = all_contents
            merged['merged_context'] = '; '.join(set(all_contexts)) if all_contexts else merged.get('context', '')
            
            deduped.append(merged)
    
    return deduped

def main():
    input_path = "_all_signals_8types.json"
    output_path = "_deduped_signals.json"
    
    print(f"Loading signals from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        signals = json.load(f)
    
    print(f"Original signals: {len(signals)}")
    
    # 중복 제거
    deduped_signals = merge_signals(signals)
    
    print(f"Deduped signals: {len(deduped_signals)}")
    print(f"Reduction: {len(signals) - len(deduped_signals)} signals merged")
    
    # 결과 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(deduped_signals, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {output_path}")
    
    # 통계 출력
    asset_counts = defaultdict(int)
    video_counts = defaultdict(int)
    merged_counts = 0
    
    for signal in deduped_signals:
        asset_counts[signal['asset']] += 1
        video_counts[signal['video_id']] += 1
        if signal.get('merged_from_count', 1) > 1:
            merged_counts += 1
    
    print(f"\n=== Statistics ===")
    print(f"Total signals: {len(deduped_signals)}")
    print(f"Merged signals: {merged_counts}")
    print(f"Unique assets: {len(asset_counts)}")
    print(f"Unique videos: {len(video_counts)}")
    
    print(f"\nTop assets:")
    for asset, count in sorted(asset_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {asset}: {count}")

if __name__ == "__main__":
    main()