#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_channel.py - 채널 파이프라인 메인 오케스트레이션
STEP 1: 필터링 → STEP 2: 자막 추출 → STEP 3: 신호 분석 → STEP 4: DB INSERT
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

# 파이프라인 디렉토리를 sys.path에 추가
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
if PIPELINE_DIR not in sys.path:
    sys.path.insert(0, PIPELINE_DIR)

from video_filter import filter_videos
from subtitle_extractor import extract_subtitles
from signal_analyzer import analyze_batch
from db_inserter import insert_pipeline_results

DATA_DIR = os.path.join(PIPELINE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)


def get_channel_handle(channel_url: str) -> str:
    """채널 URL에서 핸들 추출 (예: @GODofIT → GODofIT)"""
    handle = channel_url.rstrip('/')
    if '/@' in handle:
        handle = handle.split('/@')[-1]
    elif '@' in handle:
        handle = handle.split('@')[-1]
    return handle


def load_checkpoint(checkpoint_path: str) -> dict:
    """체크포인트 로드 (재실행 이어서 하기)"""
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_checkpoint(checkpoint_path: str, data: dict):
    """체크포인트 저장"""
    with open(checkpoint_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run_pipeline(channel_url: str, channel_name: str):
    """메인 파이프라인 실행"""
    start_time = datetime.now()
    
    channel_handle = get_channel_handle(channel_url)
    print(f"\n{'='*60}")
    print(f"채널 파이프라인 시작: {channel_name} (@{channel_handle})")
    print(f"URL: {channel_url}")
    print(f"시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    checkpoint_path = os.path.join(DATA_DIR, f'{channel_handle}_checkpoint.json')
    filtered_path = os.path.join(DATA_DIR, f'{channel_handle}_filtered.json')
    subtitles_path = os.path.join(DATA_DIR, f'{channel_handle}_subtitles.json')
    signals_path = os.path.join(DATA_DIR, f'{channel_handle}_signals.json')
    
    checkpoint = load_checkpoint(checkpoint_path)
    
    # ==========================================
    # STEP 1: 영상 필터링
    # ==========================================
    if checkpoint.get('step1_done') and os.path.exists(filtered_path):
        print("[STEP 1] 체크포인트에서 필터 결과 로드...")
        with open(filtered_path, 'r', encoding='utf-8') as f:
            filtered_videos = json.load(f)
        print(f"  → {len(filtered_videos)}개 영상 로드됨")
    else:
        print("[STEP 1] 영상 필터링...")
        filtered_videos = filter_videos(channel_url, filtered_path)
        
        if not filtered_videos:
            print("[오류] 필터 통과 영상 없음. 종료.")
            return
        
        checkpoint['step1_done'] = True
        checkpoint['total_videos_count'] = len(filtered_videos)
        save_checkpoint(checkpoint_path, checkpoint)
    
    total_videos = checkpoint.get('total_videos_count', len(filtered_videos))
    filtered_count = len(filtered_videos)
    
    print(f"\n  필터 통과: {filtered_count}개\n")
    
    # ==========================================
    # STEP 2: 자막 추출
    # ==========================================
    if checkpoint.get('step2_done') and os.path.exists(subtitles_path):
        print("[STEP 2] 체크포인트에서 자막 로드...")
        with open(subtitles_path, 'r', encoding='utf-8') as f:
            subtitles = json.load(f)
        print(f"  → {len(subtitles)}개 자막 로드됨")
    else:
        print("[STEP 2] 자막 추출...")
        subtitles = extract_subtitles(filtered_videos, channel_handle)
        
        # 중간 결과 저장
        with open(subtitles_path, 'w', encoding='utf-8') as f:
            json.dump(subtitles, f, ensure_ascii=False, indent=2)
        
        checkpoint['step2_done'] = True
        checkpoint['subtitle_count'] = len(subtitles)
        save_checkpoint(checkpoint_path, checkpoint)
    
    subtitle_count = len(subtitles)
    print(f"\n  자막 추출 성공: {subtitle_count}/{filtered_count}개\n")
    
    # 자막 있는 영상만 분석
    videos_with_subs = [
        (v, subtitles[v['video_id']])
        for v in filtered_videos
        if v['video_id'] in subtitles
    ]
    
    # ==========================================
    # STEP 3: 신호 분석
    # ==========================================
    if checkpoint.get('step3_done') and os.path.exists(signals_path):
        print("[STEP 3] 체크포인트에서 신호 로드...")
        with open(signals_path, 'r', encoding='utf-8') as f:
            signals_by_video = json.load(f)
        total_signals = sum(len(v) for v in signals_by_video.values())
        print(f"  → {len(signals_by_video)}개 영상, 총 {total_signals}개 신호 로드됨")
    else:
        print("[STEP 3] V10.11 신호 분석...")
        signals_by_video = analyze_batch(
            channel_name=channel_name,
            videos_with_subs=videos_with_subs,
            batch_size=5
        )
        
        # 중간 결과 저장
        with open(signals_path, 'w', encoding='utf-8') as f:
            json.dump(signals_by_video, f, ensure_ascii=False, indent=2)
        
        checkpoint['step3_done'] = True
        checkpoint['total_signals'] = sum(len(v) for v in signals_by_video.values())
        save_checkpoint(checkpoint_path, checkpoint)
    
    total_signals = sum(len(v) for v in signals_by_video.values())
    print(f"\n  신호 추출: {total_signals}개\n")
    
    # ==========================================
    # STEP 4: DB INSERT
    # ==========================================
    print("[STEP 4] DB INSERT...")
    db_stats = insert_pipeline_results(
        channel_name=channel_name,
        channel_handle=channel_handle,
        channel_url=channel_url,
        videos=filtered_videos,
        subtitles=subtitles,
        signals_by_video=signals_by_video
    )
    
    checkpoint['step4_done'] = True
    checkpoint['db_stats'] = db_stats
    save_checkpoint(checkpoint_path, checkpoint)
    
    # ==========================================
    # 완료 리포트
    # ==========================================
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    
    filter_ratio = f"{filtered_count}/{total_videos} ({filtered_count/max(total_videos,1)*100:.1f}%)"
    
    report_lines = [
        f"# @{channel_handle} 파이프라인 완료 리포트",
        f"",
        f"**채널**: {channel_name} ({channel_url})",
        f"**실행 시간**: {start_time.strftime('%Y-%m-%d %H:%M:%S')} ~ {end_time.strftime('%H:%M:%S')} ({elapsed:.0f}초)",
        f"**파이프라인 버전**: v10.11",
        f"",
        f"## 결과 요약",
        f"",
        f"| 항목 | 수치 |",
        f"|------|------|",
        f"| 전체 영상 수 | {total_videos}개 |",
        f"| 필터 통과 | {filter_ratio} |",
        f"| 자막 추출 성공 | {subtitle_count}개 |",
        f"| 신호 추출 | {total_signals}개 |",
        f"| DB INSERT 성공 (영상) | {db_stats.get('videos_inserted', 0)}개 |",
        f"| DB INSERT 성공 (신호) | {db_stats.get('signals_inserted', 0)}개 |",
        f"| DB 중복 스킵 (신호) | {db_stats.get('signals_skipped', 0)}개 |",
        f"",
        f"## 파일 경로",
        f"- 필터 결과: `{filtered_path}`",
        f"- 자막 데이터: `{subtitles_path}`",
        f"- 신호 데이터: `{signals_path}`",
        f"- 체크포인트: `{checkpoint_path}`",
    ]
    
    report = '\n'.join(report_lines)
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    report_path = os.path.join(PIPELINE_DIR, f'GODOFTI_REPORT.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[완료] 리포트 저장: {report_path}")
    
    return {
        'total_videos': total_videos,
        'filtered': filtered_count,
        'subtitles': subtitle_count,
        'signals': total_signals,
        'db_videos': db_stats.get('videos_inserted', 0),
        'db_signals': db_stats.get('signals_inserted', 0),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YouTube 채널 파이프라인')
    parser.add_argument('--channel', required=True, help='YouTube 채널 URL')
    parser.add_argument('--name', required=True, help='채널 이름')
    args = parser.parse_args()
    
    run_pipeline(args.channel, args.name)
