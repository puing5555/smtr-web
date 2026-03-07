#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qa_checker.py - 자동 QA 체크
채널 처리 완료 후 자동 실행. 시그널 품질 검증.
"""

import json
import os
from datetime import datetime, date
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
QA_RESULTS_DIR = os.path.join(DATA_DIR, 'qa_results')
os.makedirs(QA_RESULTS_DIR, exist_ok=True)

# 비종목 지수명 목록
INDEX_NAMES = [
    '코스피', '코스닥', 'S&P500', 'S&P 500', '나스닥', '다우', 'KOSPI', 'KOSDAQ',
    'NASDAQ', 'DOW', 'Russell', '러셀', 'MSCI', 'VIX', '공포지수',
    '코스피200', 'KOSPI200', '다우존스'
]

# 너무 일반적인 단어 (3글자 이하 또는 일반 단어)
GENERIC_TERMS = ['금', '달러', '원', '엔', '유로', '위안', '원유', '은', '구리', '채권', '국채']

# 최소 유의미 종목명 길이
MIN_STOCK_NAME_LEN = 3


def check_signals(
    channel_handle: str,
    videos: list[dict],
    signals_by_video: dict[str, list[dict]]
) -> dict:
    """
    시그널 품질 체크.
    반환: QA 결과 딕셔너리
    """
    issues = []
    warnings = []
    stats = {
        'total_signals': 0,
        'signal_distribution': defaultdict(int),
        'index_extractions': [],
        'generic_extractions': [],
        'suspicious_timestamps': [],
        'duplicate_stock_in_video': [],
        'short_stock_names': [],
    }

    # 영상별 duration 맵
    duration_map = {v['video_id']: (v.get('duration') or 0) for v in videos}

    all_signals = []
    for vid_id, sigs in signals_by_video.items():
        for sig in sigs:
            sig['_video_id'] = vid_id
            all_signals.append(sig)

    stats['total_signals'] = len(all_signals)

    if not all_signals:
        warnings.append("시그널이 0개입니다. 채널 처리 또는 자막 추출 문제일 수 있습니다.")
        return _build_result(channel_handle, stats, issues, warnings)

    # 1. 시그널 분포 체크
    for sig in all_signals:
        stats['signal_distribution'][sig.get('signal', '?')] += 1

    total = stats['total_signals']
    buy_count = stats['signal_distribution'].get('매수', 0)
    sell_count = stats['signal_distribution'].get('매도', 0)
    caution_count = stats['signal_distribution'].get('경계', 0)

    if total > 0 and (buy_count / total) >= 0.80:
        warnings.append(f"⚠️ 매수 편향 의심: 매수 {buy_count}/{total} ({buy_count/total*100:.1f}%)")

    if sell_count + caution_count == 0 and total >= 5:
        warnings.append(f"⚠️ 부정 시그널 미검출: 매도/경계 0건 (전체 {total}건)")

    # 2. 비종목 지수 오추출 체크
    for sig in all_signals:
        stock = sig.get('stock', '')
        stock_upper = stock.upper()

        for idx_name in INDEX_NAMES:
            if idx_name.upper() == stock_upper or idx_name in stock:
                stats['index_extractions'].append({
                    'video_id': sig['_video_id'],
                    'stock': stock,
                    'signal': sig.get('signal'),
                    'key_quote': sig.get('key_quote', '')[:50],
                })
                issues.append(f"🚨 지수 오추출: '{stock}' (video: {sig['_video_id']})")
                break

        # 일반 단어 체크
        if stock in GENERIC_TERMS:
            stats['generic_extractions'].append({
                'video_id': sig['_video_id'],
                'stock': stock,
            })
            issues.append(f"🚨 일반 단어 오추출: '{stock}' (video: {sig['_video_id']})")

        # 너무 짧은 종목명 (2글자 이하)
        if len(stock) <= 2:
            stats['short_stock_names'].append({
                'video_id': sig['_video_id'],
                'stock': stock,
            })
            warnings.append(f"⚠️ 짧은 종목명: '{stock}' (video: {sig['_video_id']})")

    # 3. 타임스탬프 체크
    suspicious_ts_count = 0
    for sig in all_signals:
        ts = sig.get('timestamp_in_video', '00:00:00')
        duration = duration_map.get(sig['_video_id'], 0)

        is_zero = ts == '00:00:00'

        # 영상 길이의 90% 이상인지
        is_near_end = False
        if duration > 0:
            try:
                parts = ts.split(':')
                ts_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                if ts_seconds >= duration * 0.9:
                    is_near_end = True
            except:
                pass

        if is_zero or is_near_end:
            suspicious_ts_count += 1
            stats['suspicious_timestamps'].append({
                'video_id': sig['_video_id'],
                'stock': sig.get('stock'),
                'timestamp': ts,
                'duration': duration,
                'reason': 'zero' if is_zero else 'near_end',
            })

    if total > 0 and (suspicious_ts_count / total) >= 0.5:
        warnings.append(
            f"⚠️ 타임스탬프 부정확 의심: {suspicious_ts_count}/{total} ({suspicious_ts_count/total*100:.1f}%) "
            f"타임스탬프가 00:00:00 또는 영상 끝부분"
        )

    # 4. 같은 video에서 같은 stock 중복 체크
    video_stock_counts = defaultdict(lambda: defaultdict(int))
    for sig in all_signals:
        video_stock_counts[sig['_video_id']][sig.get('stock', '')] += 1

    for vid_id, stock_counts in video_stock_counts.items():
        for stock, count in stock_counts.items():
            if count >= 2:
                stats['duplicate_stock_in_video'].append({
                    'video_id': vid_id,
                    'stock': stock,
                    'count': count,
                })
                warnings.append(f"⚠️ 중복 시그널: video={vid_id}, stock='{stock}' x{count}회")

    return _build_result(channel_handle, stats, issues, warnings)


def _build_result(channel_handle: str, stats: dict, issues: list, warnings: list) -> dict:
    """QA 결과 빌드"""
    # defaultdict → 일반 dict 변환
    dist = dict(stats['signal_distribution'])

    result = {
        'channel': channel_handle,
        'checked_at': datetime.now().isoformat(),
        'date': date.today().isoformat(),
        'summary': {
            'total_signals': stats['total_signals'],
            'signal_distribution': dist,
            'issues_count': len(issues),
            'warnings_count': len(warnings),
            'passed': len(issues) == 0,
        },
        'issues': issues,
        'warnings': warnings,
        'details': {
            'index_extractions': stats['index_extractions'],
            'generic_extractions': stats['generic_extractions'],
            'suspicious_timestamps': stats['suspicious_timestamps'][:20],  # 최대 20개
            'duplicate_stock_in_video': stats['duplicate_stock_in_video'][:20],
            'short_stock_names': stats['short_stock_names'],
        }
    }
    return result


def run_qa(
    channel_handle: str,
    videos: list[dict],
    signals_by_video: dict[str, list[dict]]
) -> dict:
    """
    QA 실행 및 결과 저장.
    반환: QA 결과
    """
    print(f"\n[QA] 채널 '{channel_handle}' 품질 검사 시작...")

    result = check_signals(channel_handle, videos, signals_by_video)

    # 결과 저장
    today = date.today().strftime('%Y%m%d')
    result_path = os.path.join(QA_RESULTS_DIR, f'{channel_handle}_{today}.json')
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 요약 출력
    summary = result['summary']
    print(f"[QA] 결과: 총 {summary['total_signals']}개 시그널")
    print(f"  분포: {summary['signal_distribution']}")

    if result['issues']:
        print(f"\n  🚨 이슈 {len(result['issues'])}개:")
        for issue in result['issues'][:10]:
            print(f"    {issue}")

    if result['warnings']:
        print(f"\n  ⚠️ 경고 {len(result['warnings'])}개:")
        for warning in result['warnings'][:10]:
            print(f"    {warning}")

    if summary['passed'] and not result['warnings']:
        print(f"  ✅ QA 통과 - 이슈/경고 없음")

    print(f"[QA] 결과 저장: {result_path}")
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel-handle', required=True)
    parser.add_argument('--signals-file', required=True, help='signals JSON 파일')
    parser.add_argument('--filtered-file', required=True, help='filtered videos JSON 파일')
    args = parser.parse_args()

    with open(args.signals_file, 'r', encoding='utf-8') as f:
        signals_by_video = json.load(f)
    with open(args.filtered_file, 'r', encoding='utf-8') as f:
        videos = json.load(f)

    result = run_qa(args.channel_handle, videos, signals_by_video)
    print(json.dumps(result['summary'], ensure_ascii=False, indent=2))
