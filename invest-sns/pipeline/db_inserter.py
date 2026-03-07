#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
db_inserter.py - Supabase DB INSERT
influencer_channels → influencer_videos → influencer_signals
REST API 직접 사용
"""

import json
import uuid
import requests
from datetime import datetime, timezone

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"


def get_headers(prefer: str = None) -> dict:
    headers = {
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'application/json',
    }
    if prefer:
        headers['Prefer'] = prefer
    return headers


def supabase_get(table: str, params: dict) -> list[dict]:
    """Supabase REST GET"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.get(url, params=params, headers=get_headers())
    if resp.status_code == 200:
        return resp.json()
    return []


def supabase_post(table: str, data: dict, upsert: bool = False) -> dict | None:
    """Supabase REST POST"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    prefer = 'return=representation'
    if upsert:
        prefer += ',resolution=merge-duplicates'
    
    resp = requests.post(url, json=data, headers=get_headers(prefer))
    if resp.status_code in (200, 201):
        result = resp.json()
        if isinstance(result, list) and result:
            return result[0]
        return data
    else:
        print(f"  [DB] INSERT 실패 ({table}): {resp.status_code} - {resp.text[:200]}")
        return None


def upsert_channel(channel_name: str, channel_handle: str, channel_url: str) -> str | None:
    """
    채널 UPSERT.
    반환: channel UUID (id)
    """
    # 기존 채널 조회
    existing = supabase_get('influencer_channels', {
        'channel_handle': f'eq.{channel_handle}',
        'platform': 'eq.youtube',
        'select': 'id,channel_name'
    })
    
    if existing:
        channel_id = existing[0]['id']
        print(f"  [DB] 채널 이미 존재: {channel_name} ({channel_id[:8]}...)")
        return channel_id
    
    # 신규 생성
    channel_data = {
        'id': str(uuid.uuid4()),
        'channel_name': channel_name,
        'channel_handle': channel_handle,
        'channel_url': channel_url,
        'platform': 'youtube',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    
    result = supabase_post('influencer_channels', channel_data)
    if result:
        channel_id = channel_data['id']
        print(f"  [DB] 채널 생성: {channel_name} ({channel_id[:8]}...)")
        return channel_id
    
    return None


def upsert_video(
    channel_id: str,
    video_id: str,
    title: str,
    duration_seconds: int,
    upload_date: str,
    has_subtitle: bool,
    signal_count: int = 0
) -> str | None:
    """
    영상 INSERT (video_id 기준 중복 체크).
    반환: videos 테이블의 UUID (id)
    """
    # 기존 영상 조회
    existing = supabase_get('influencer_videos', {
        'video_id': f'eq.{video_id}',
        'select': 'id,video_id'
    })
    
    if existing:
        vid_uuid = existing[0]['id']
        # has_subtitle, signal_count 업데이트
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
        update_data = {
            'has_subtitle': has_subtitle,
            'signal_count': signal_count,
            'analyzed_at': datetime.now(timezone.utc).isoformat(),
            'pipeline_version': 'v10.11',
        }
        requests.patch(
            url,
            params={'id': f'eq.{vid_uuid}'},
            json=update_data,
            headers=get_headers('return=minimal')
        )
        print(f"  [DB] 영상 이미 존재 (업데이트): {video_id}")
        return vid_uuid
    
    # 날짜 파싱
    published_at = None
    if upload_date and len(upload_date) == 8:
        try:
            from datetime import datetime as dt
            published_at = dt.strptime(upload_date, '%Y%m%d').replace(tzinfo=timezone.utc).isoformat()
        except:
            pass
    
    video_data = {
        'id': str(uuid.uuid4()),
        'channel_id': channel_id,
        'video_id': video_id,
        'title': title,
        'published_at': published_at,
        'duration_seconds': duration_seconds,
        'has_subtitle': has_subtitle,
        'subtitle_language': 'ko',
        'analyzed_at': datetime.now(timezone.utc).isoformat(),
        'pipeline_version': 'v10.11',
        'signal_count': signal_count,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    
    result = supabase_post('influencer_videos', video_data)
    if result:
        vid_uuid = video_data['id']
        print(f"  [DB] 영상 INSERT: {video_id} ({title[:40]})")
        return vid_uuid
    
    return None


def insert_signal(video_uuid: str, signal: dict) -> bool:
    """
    시그널 INSERT (중복 방지: video_id + stock + signal 조합).
    """
    stock = signal.get('stock', '')
    sig_value = signal.get('signal', '')
    
    # 중복 확인
    existing = supabase_get('influencer_signals', {
        'video_id': f'eq.{video_uuid}',
        'stock': f'eq.{stock}',
        'signal': f'eq.{sig_value}',
        'select': 'id'
    })
    
    if existing:
        return False  # 이미 존재
    
    signal_data = {
        'id': str(uuid.uuid4()),
        'video_id': video_uuid,
        'speaker': signal.get('speaker', ''),
        'stock': stock,
        'ticker': signal.get('ticker'),
        'market': signal.get('market', 'KR'),
        'mention_type': '결론',  # 기본값
        'signal': sig_value,
        'confidence': signal.get('confidence', 'medium'),
        'timestamp': signal.get('timestamp_in_video', '00:00:00'),
        'key_quote': signal.get('key_quote', ''),
        'reasoning': signal.get('reasoning', ''),
        'review_status': 'approved',
        'pipeline_version': 'v10.11',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    
    result = supabase_post('influencer_signals', signal_data)
    return result is not None


def insert_pipeline_results(
    channel_name: str,
    channel_handle: str,
    channel_url: str,
    videos: list[dict],
    subtitles: dict[str, str],
    signals_by_video: dict[str, list[dict]]
) -> dict:
    """
    파이프라인 전체 결과 DB INSERT.
    반환: 통계 딕셔너리
    """
    stats = {
        'channel_id': None,
        'videos_inserted': 0,
        'videos_skipped': 0,
        'signals_inserted': 0,
        'signals_skipped': 0,
    }
    
    # 1. 채널 upsert
    channel_id = upsert_channel(channel_name, channel_handle, channel_url)
    if not channel_id:
        print("[DB] 채널 생성 실패")
        return stats
    
    stats['channel_id'] = channel_id
    
    # 2. 영상별 INSERT
    for video in videos:
        video_id = video['video_id']
        title = video.get('title', '')
        duration = video.get('duration', 0) or 0
        upload_date = video.get('upload_date', '')
        
        has_subtitle = video_id in subtitles
        video_signals = signals_by_video.get(video_id, [])
        signal_count = len(video_signals)
        
        video_uuid = upsert_video(
            channel_id=channel_id,
            video_id=video_id,
            title=title,
            duration_seconds=int(duration),
            upload_date=upload_date,
            has_subtitle=has_subtitle,
            signal_count=signal_count
        )
        
        if not video_uuid:
            stats['videos_skipped'] += 1
            continue
        
        stats['videos_inserted'] += 1
        
        # 3. 시그널 INSERT (신호가 있는 경우만)
        for signal in video_signals:
            ok = insert_signal(video_uuid, signal)
            if ok:
                stats['signals_inserted'] += 1
            else:
                stats['signals_skipped'] += 1
    
    print(f"[DB] 완료 - 영상: {stats['videos_inserted']}개, 시그널: {stats['signals_inserted']}개")
    return stats


if __name__ == '__main__':
    # 간단한 연결 테스트
    print("Supabase 연결 테스트...")
    result = supabase_get('influencer_channels', {'select': 'id,channel_name', 'limit': '3'})
    print(f"채널 목록: {result}")
