#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_channel.py - 채널 파이프라인 메인 오케스트레이션 (9단계)
STEP 1: 메타데이터 수집
STEP 2: 필터링 → 결과 보고 + 중간 저장
STEP 3: 자막 추출
STEP 4: V10.11 신호 분석
STEP 5: 종목명 정규화 (stock_normalizer.py 있으면 사용)
STEP 6: DB INSERT
STEP 7: QA 체크
STEP 8: 오류 패턴 누적
STEP 9: 완료 리포트
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
if PIPELINE_DIR not in sys.path:
    sys.path.insert(0, PIPELINE_DIR)

from video_filter import filter_videos, fetch_channel_metadata, apply_hard_rules, ai_filter_batch
from subtitle_extractor import extract_subtitles
from signal_analyzer import analyze_batch
from db_inserter import insert_pipeline_results
from qa_checker import run_qa
from error_tracker import track_errors

DATA_DIR = os.path.join(PIPELINE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 종목명 정규화 스크립트 경로
STOCK_NORMALIZER_PATH = r'C:\Users\Mario\work\invest-sns\scripts\stock_normalizer.py'


def get_channel_handle(channel_url: str) -> str:
    """채널 URL에서 핸들 추출"""
    handle = channel_url.rstrip('/')
    if '/@' in handle:
        handle = handle.split('/@')[-1]
    elif '@' in handle:
        handle = handle.split('@')[-1]
    # 특수문자 제거 (파일명 안전)
    safe_handle = handle.replace('.', '_').replace('/', '_')
    return safe_handle, handle


def load_checkpoint(path: str) -> dict:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_checkpoint(path: str, data: dict):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def detailed_filter_report(
    all_videos: list[dict],
    included: list[dict],
    channel_handle: str,
    channel_name: str,
    channel_url: str,
    report_path: str
):
    """상세 필터링 리포트 생성 및 저장"""
    total = len(all_videos)

    # 각 제외 이유 카운트
    shorts_excluded = 0
    live_excluded = 0
    low_view_excluded = 0
    keyword_excluded = 0
    other_excluded = 0

    EXCLUDE_TITLE_KEYWORDS = ['일상', '먹방', '여행', '브이로그', 'vlog', '구독', '이벤트', '경품', '광고', '협찬', '소개', '인사']
    EXCLUDE_SHORTS = ['#shorts', '#쇼츠']

    for v in all_videos:
        duration = v.get('duration', 0) or 0
        view_count = v.get('view_count', 0) or 0
        title = (v.get('title', '') or '').lower()

        if v in included:
            continue

        if duration < 60:
            shorts_excluded += 1
        elif duration > 7200:
            live_excluded += 1
        elif view_count < 1000:
            low_view_excluded += 1
        else:
            excluded_by_kw = False
            for kw in EXCLUDE_TITLE_KEYWORDS:
                if kw in title:
                    excluded_by_kw = True
                    break
            for kw in EXCLUDE_SHORTS:
                if kw in title:
                    excluded_by_kw = True
                    break
            if excluded_by_kw:
                keyword_excluded += 1
            else:
                other_excluded += 1  # AI 판단 제외

    passed = len(included)
    filter_ratio = f"{passed/max(total,1)*100:.1f}%"

    # 샘플 10개 (통과 영상)
    sample_titles = []
    for v in included[:10]:
        sample_titles.append(f"- [{v.get('video_id','')}] {v.get('title','')[:70]}")

    lines = [
        f"# @{channel_handle} 필터링 리포트",
        f"",
        f"**채널**: {channel_name} ({channel_url})",
        f"**생성 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"## 필터링 결과",
        f"",
        f"| 항목 | 수치 |",
        f"|------|------|",
        f"| 전체 영상 수 | {total}개 |",
        f"| Shorts 제외 (60초 미만) | {shorts_excluded}개 |",
        f"| 라이브 제외 (2시간 초과) | {live_excluded}개 |",
        f"| 조회수 부족 제외 (<1000) | {low_view_excluded}개 |",
        f"| 제목 키워드 제외 | {keyword_excluded}개 |",
        f"| AI 판단 제외 | {other_excluded}개 |",
        f"| **최종 통과** | **{passed}개 ({filter_ratio})** |",
        f"",
        f"## 통과 영상 샘플 (최대 10개)",
        f"",
    ]
    lines.extend(sample_titles)
    lines.append("")

    report = '\n'.join(lines)
    print("\n" + "="*60)
    print(report)
    print("="*60)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n[필터] 리포트 저장: {report_path}")


def try_normalize_stocks(signals_by_video: dict) -> dict:
    """stock_normalizer.py 있으면 종목명 정규화 적용"""
    if not os.path.exists(STOCK_NORMALIZER_PATH):
        return signals_by_video

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location('stock_normalizer', STOCK_NORMALIZER_PATH)
        normalizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(normalizer)

        normalized = {}
        for vid_id, sigs in signals_by_video.items():
            normalized_sigs = []
            for sig in sigs:
                if hasattr(normalizer, 'normalize'):
                    sig['stock'] = normalizer.normalize(sig.get('stock', ''))
                normalized_sigs.append(sig)
            normalized[vid_id] = normalized_sigs
        print("[정규화] stock_normalizer.py 적용 완료")
        return normalized
    except Exception as e:
        print(f"[정규화] stock_normalizer.py 오류 (skip): {e}")
        return signals_by_video


def run_pipeline(channel_url: str, channel_name: str, filter_only: bool = False):
    """메인 파이프라인 실행"""
    start_time = datetime.now()

    safe_handle, raw_handle = get_channel_handle(channel_url)
    print(f"\n{'='*60}")
    print(f"채널 파이프라인 시작: {channel_name} (@{raw_handle})")
    print(f"URL: {channel_url}")
    print(f"시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if filter_only:
        print(f"모드: 필터링만 실행")
    print(f"{'='*60}\n")

    checkpoint_path = os.path.join(DATA_DIR, f'{safe_handle}_checkpoint.json')
    filtered_path = os.path.join(DATA_DIR, f'{safe_handle}_filtered.json')
    all_meta_path = os.path.join(DATA_DIR, f'{safe_handle}_all_meta.json')
    subtitles_path = os.path.join(DATA_DIR, f'{safe_handle}_subtitles.json')
    signals_path = os.path.join(DATA_DIR, f'{safe_handle}_signals.json')
    filter_report_path = os.path.join(PIPELINE_DIR, f'{safe_handle}_FILTER_REPORT.md')
    final_report_path = os.path.join(PIPELINE_DIR, f'GODOFTI_REPORT.md')

    checkpoint = load_checkpoint(checkpoint_path)

    # ==========================================
    # STEP 1+2: 메타데이터 수집 + 필터링
    # ==========================================
    if checkpoint.get('step2_done') and os.path.exists(filtered_path):
        print("[STEP 1+2] 체크포인트에서 필터 결과 로드...")
        with open(filtered_path, 'r', encoding='utf-8') as f:
            filtered_videos = json.load(f)
        if os.path.exists(all_meta_path):
            with open(all_meta_path, 'r', encoding='utf-8') as f:
                all_videos = json.load(f)
        else:
            all_videos = filtered_videos
        print(f"  → {len(filtered_videos)}개 통과 영상 로드됨")
    else:
        print("[STEP 1] 채널 메타데이터 수집...")
        from video_filter import fetch_channel_metadata
        all_videos = fetch_channel_metadata(channel_url)

        if not all_videos:
            print("[오류] 메타데이터 수집 실패. 종료.")
            return

        # 메타데이터 저장
        with open(all_meta_path, 'w', encoding='utf-8') as f:
            json.dump(all_videos, f, ensure_ascii=False, indent=2)
        print(f"  → 총 {len(all_videos)}개 영상 메타데이터 수집")

        print("\n[STEP 2] 필터링...")
        # 하드 룰 먼저
        hard_included = []
        hard_excluded = []
        ambiguous = []

        for v in all_videos:
            decision = apply_hard_rules(v)
            v['filter_decision'] = decision
            if decision == 'include':
                hard_included.append(v)
            elif decision == 'exclude':
                hard_excluded.append(v)
            else:
                ambiguous.append(v)

        print(f"  하드룰 - 포함: {len(hard_included)}, 제외: {len(hard_excluded)}, 모호: {len(ambiguous)}")

        # AI 판단
        filtered_videos = list(hard_included)
        if ambiguous:
            print(f"  AI 판단 시작: {len(ambiguous)}개")
            batch_size = 50
            for i in range(0, len(ambiguous), batch_size):
                batch = ambiguous[i:i + batch_size]
                titles = [v['title'] for v in batch]
                decisions = ai_filter_batch(titles)
                for j, v in enumerate(batch):
                    if j < len(decisions) and decisions[j]:
                        v['filter_decision'] = 'include_ai'
                        filtered_videos.append(v)
                    else:
                        v['filter_decision'] = 'exclude_ai'
                if i + batch_size < len(ambiguous):
                    time.sleep(2)

        # 저장
        with open(filtered_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_videos, f, ensure_ascii=False, indent=2)

        checkpoint['step2_done'] = True
        checkpoint['total_videos_count'] = len(all_videos)
        checkpoint['filtered_count'] = len(filtered_videos)
        save_checkpoint(checkpoint_path, checkpoint)

        print(f"\n  ✅ 필터링 완료: {len(filtered_videos)}/{len(all_videos)}개 통과")

    # 필터링 리포트 저장 (항상)
    detailed_filter_report(
        all_videos=all_videos,
        included=filtered_videos,
        channel_handle=safe_handle,
        channel_name=channel_name,
        channel_url=channel_url,
        report_path=filter_report_path,
    )

    if filter_only:
        print("\n[완료] 필터링 전용 모드. 자막 추출은 다음에 실행하세요.")
        print(f"  다음 실행: python run_channel.py --channel \"{channel_url}\" --name \"{channel_name}\"")
        return

    total_videos = len(all_videos)
    filtered_count = len(filtered_videos)

    # ==========================================
    # STEP 3: 자막 추출
    # ==========================================
    if checkpoint.get('step3_done') and os.path.exists(subtitles_path):
        print("\n[STEP 3] 체크포인트에서 자막 로드...")
        with open(subtitles_path, 'r', encoding='utf-8') as f:
            subtitles = json.load(f)
        print(f"  → {len(subtitles)}개 자막 로드됨")
    else:
        print("\n[STEP 3] 자막 추출...")
        subtitles = extract_subtitles(filtered_videos, safe_handle)
        with open(subtitles_path, 'w', encoding='utf-8') as f:
            json.dump(subtitles, f, ensure_ascii=False, indent=2)
        checkpoint['step3_done'] = True
        checkpoint['subtitle_count'] = len(subtitles)
        save_checkpoint(checkpoint_path, checkpoint)

    subtitle_count = len(subtitles)
    print(f"\n  자막 추출 성공: {subtitle_count}/{filtered_count}개\n")

    videos_with_subs = [
        (v, subtitles[v['video_id']])
        for v in filtered_videos
        if v['video_id'] in subtitles
    ]

    # ==========================================
    # STEP 4: 신호 분석
    # ==========================================
    if checkpoint.get('step4_done') and os.path.exists(signals_path):
        print("[STEP 4] 체크포인트에서 신호 로드...")
        with open(signals_path, 'r', encoding='utf-8') as f:
            signals_by_video = json.load(f)
        total_signals = sum(len(v) for v in signals_by_video.values())
        print(f"  → 총 {total_signals}개 신호 로드됨")
    else:
        print("[STEP 4] V10.11 신호 분석...")
        signals_by_video = analyze_batch(
            channel_name=channel_name,
            videos_with_subs=videos_with_subs,
            batch_size=5
        )
        with open(signals_path, 'w', encoding='utf-8') as f:
            json.dump(signals_by_video, f, ensure_ascii=False, indent=2)
        checkpoint['step4_done'] = True
        checkpoint['total_signals'] = sum(len(v) for v in signals_by_video.values())
        save_checkpoint(checkpoint_path, checkpoint)

    total_signals = sum(len(v) for v in signals_by_video.values())
    print(f"\n  신호 추출: {total_signals}개\n")

    # ==========================================
    # STEP 5: 종목명 정규화 (있으면 사용)
    # ==========================================
    print("[STEP 5] 종목명 정규화...")
    signals_by_video = try_normalize_stocks(signals_by_video)

    # ==========================================
    # STEP 6: DB INSERT
    # ==========================================
    print("[STEP 6] DB INSERT...")
    db_stats = insert_pipeline_results(
        channel_name=channel_name,
        channel_handle=raw_handle,
        channel_url=channel_url,
        videos=filtered_videos,
        subtitles=subtitles,
        signals_by_video=signals_by_video
    )
    checkpoint['step6_done'] = True
    checkpoint['db_stats'] = db_stats
    save_checkpoint(checkpoint_path, checkpoint)

    # ==========================================
    # STEP 7: QA 체크
    # ==========================================
    print("[STEP 7] QA 자동 체크...")
    qa_result = run_qa(safe_handle, filtered_videos, signals_by_video)

    # ==========================================
    # STEP 8: 오류 패턴 누적
    # ==========================================
    print("[STEP 8] 오류 패턴 누적...")
    track_errors(safe_handle, qa_result)

    # ==========================================
    # STEP 9: 완료 리포트
    # ==========================================
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    filter_ratio = f"{filtered_count}/{total_videos} ({filtered_count/max(total_videos,1)*100:.1f}%)"

    qa_summary = qa_result.get('summary', {})
    qa_passed = "✅ 통과" if qa_summary.get('passed') else f"⚠️ 이슈 {qa_summary.get('issues_count',0)}건"

    report_lines = [
        f"# @{raw_handle} 파이프라인 완료 리포트",
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
        f"| QA 결과 | {qa_passed} |",
        f"",
        f"## QA 상세",
        f"- 시그널 분포: {qa_summary.get('signal_distribution', {})}",
        f"- 경고: {qa_summary.get('warnings_count', 0)}건",
        f"",
        f"## 파일 경로",
        f"- 필터 리포트: `{filter_report_path}`",
        f"- 자막 데이터: `{subtitles_path}`",
        f"- 신호 데이터: `{signals_path}`",
        f"- 체크포인트: `{checkpoint_path}`",
    ]

    report = '\n'.join(report_lines)
    print("\n" + "="*60)
    print(report)
    print("="*60)

    with open(final_report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n[완료] 최종 리포트: {final_report_path}")

    return {
        'total_videos': total_videos,
        'filtered': filtered_count,
        'subtitles': subtitle_count,
        'signals': total_signals,
        'db_videos': db_stats.get('videos_inserted', 0),
        'db_signals': db_stats.get('signals_inserted', 0),
        'qa_passed': qa_summary.get('passed', False),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YouTube 채널 파이프라인 (9단계)')
    parser.add_argument('--channel', required=True, help='YouTube 채널 URL')
    parser.add_argument('--name', required=True, help='채널 이름')
    parser.add_argument('--filter-only', action='store_true', help='필터링만 실행하고 중단')
    args = parser.parse_args()

    run_pipeline(args.channel, args.name, filter_only=args.filter_only)
