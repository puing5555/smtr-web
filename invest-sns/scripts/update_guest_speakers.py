"""
게스트 스피커 DB 등록 + 시그널 speaker_id UPDATE
"""
import json, os, sys
from dotenv import load_dotenv
from supabase import create_client

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))
url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
sb = create_client(url, key)

# Load guest data
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'hs_guest_signals_v2.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

guests = data['guests']
print(f"게스트 수: {len(guests)}, 총 시그널: {data['summary']['total_affected_signals']}")

# Step 0: 이효석아카데미 channel_id 및 이효석 speaker_id 조회
channel = sb.table('channels').select('id').eq('name', '이효석아카데미').single().execute()
channel_id = channel.data['id']
print(f"이효석아카데미 channel_id: {channel_id}")

hs_speaker = sb.table('speakers').select('id').eq('name', '이효석').eq('channel_id', channel_id).single().execute()
hs_speaker_id = hs_speaker.data['id']
print(f"이효석 speaker_id: {hs_speaker_id}")

# Step 0.5: 이효석의 현재 시그널 수 (before)
before_count = sb.table('influencer_signals').select('id', count='exact').eq('speaker_id', hs_speaker_id).execute()
print(f"\n[BEFORE] 이효석 시그널 수: {before_count.count}")

# Step 1: speakers 테이블에 게스트 등록
print("\n=== Step 1: 게스트 스피커 등록 ===")
guest_names = [g['name'] for g in guests]
speaker_map = {}  # name -> speaker_id

# Check existing speakers
existing = sb.table('speakers').select('id, name').eq('channel_id', channel_id).in_('name', guest_names).execute()
for s in existing.data:
    speaker_map[s['name']] = s['id']
print(f"이미 존재하는 스피커: {len(speaker_map)}명")

# Insert new speakers
new_speakers = [n for n in guest_names if n not in speaker_map]
if new_speakers:
    rows = [{'name': n, 'channel_id': channel_id} for n in new_speakers]
    # batch insert
    result = sb.table('speakers').insert(rows).execute()
    for s in result.data:
        speaker_map[s['name']] = s['id']
    print(f"새로 등록: {len(result.data)}명")
else:
    print("새로 등록할 스피커 없음")

print(f"총 매핑된 스피커: {len(speaker_map)}명")

# Step 2: 시그널 speaker_id UPDATE
print("\n=== Step 2: 시그널 speaker_id UPDATE ===")
total_updated = 0
failed = []

for guest in guests:
    name = guest['name']
    speaker_id = speaker_map.get(name)
    if not speaker_id:
        failed.append({'name': name, 'reason': 'speaker_id not found'})
        continue
    
    video_ids = [v['video_id'] for v in guest['videos']]
    expected_signals = sum(v['signal_count'] for v in guest['videos'])
    
    # Get signal ids for these videos that currently have hs_speaker_id
    # Update in batches by video_id
    updated_count = 0
    for vid in video_ids:
        # Find signals: join through videos or use video_id directly
        # influencer_signals has video_id column
        res = sb.table('influencer_signals').update({'speaker_id': speaker_id}).eq('video_id', vid).eq('speaker_id', hs_speaker_id).execute()
        updated_count += len(res.data)
    
    total_updated += updated_count
    if updated_count != expected_signals:
        print(f"  ⚠ {name}: expected {expected_signals}, updated {updated_count}")
    else:
        print(f"  ✓ {name}: {updated_count}개 UPDATE")

print(f"\n총 UPDATE: {total_updated}개")

# Step 3: 검증
print("\n=== Step 3: 검증 ===")
after_count = sb.table('influencer_signals').select('id', count='exact').eq('speaker_id', hs_speaker_id).execute()
print(f"[AFTER] 이효석 시그널 수: {after_count.count}")
print(f"감소량: {before_count.count - after_count.count} (기대: 242)")

# 게스트별 시그널 수 합계
guest_signal_total = 0
for guest in guests:
    name = guest['name']
    sid = speaker_map.get(name)
    if sid:
        cnt = sb.table('influencer_signals').select('id', count='exact').eq('speaker_id', sid).execute()
        guest_signal_total += cnt.count

print(f"게스트별 시그널 합계: {guest_signal_total}")
print(f"총 UPDATE된 시그널: {total_updated}")

if failed:
    print(f"\n실패 건: {len(failed)}")
    for f in failed:
        print(f"  - {f}")

print("\n=== 완료 ===")
