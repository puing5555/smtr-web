import urllib.request, json
from collections import Counter

SUPA_URL = 'https://arypzhotxflimroprmdk.supabase.co'
SUPA_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
GODOFITT_CH = '227ad970-4f05-4fea-9a94-90f9649ca714'

def get(path):
    req = urllib.request.Request(
        f'{SUPA_URL}/rest/v1/{path}',
        headers={'apikey': SUPA_KEY, 'Authorization': f'Bearer {SUPA_KEY}'}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def delete(path):
    req = urllib.request.Request(
        f'{SUPA_URL}/rest/v1/{path}',
        headers={'apikey': SUPA_KEY, 'Authorization': f'Bearer {SUPA_KEY}'},
        method='DELETE'
    )
    with urllib.request.urlopen(req) as r:
        return r.status

# 1. GODofIT 영상 총계 + wsaj_ 확인
vids = get('influencer_videos?select=id,video_id&channel_id=eq.' + GODOFITT_CH + '&limit=200')
wsaj_vids = [v for v in vids if v['video_id'].startswith('wsaj_')]
normal_vids = [v for v in vids if not v['video_id'].startswith('wsaj_')]
print(f'=== GODofIT 영상 총계: {len(vids)} ===')
print(f'  정상(YouTube ID): {len(normal_vids)}개')
print(f'  wsaj_ 잘못 INSERT: {len(wsaj_vids)}개')
for v in wsaj_vids:
    print(f'    - [{v["id"]}] {v["video_id"][:60]}')

# 2. wsaj_ 영상의 시그널 확인
wsaj_sig_count = 0
wsaj_sig_ids = []
for v in wsaj_vids:
    sigs = get(f'influencer_signals?select=id,signal&video_id=eq.{v["id"]}&limit=100')
    wsaj_sig_count += len(sigs)
    wsaj_sig_ids.extend([s['id'] for s in sigs])
print(f'\n  wsaj_ 관련 시그널: {wsaj_sig_count}개')

# 3. GODofIT 오늘 추가된 시그널 (정상 영상)
today_sigs_total = 0
today_dist = Counter()
for v in normal_vids:
    sigs = get(f'influencer_signals?select=id,signal&video_id=eq.{v["id"]}&created_at=gte.2026-03-07T00:00:00&limit=100')
    today_sigs_total += len(sigs)
    today_dist.update(s['signal'] for s in sigs)
print(f'\n=== 오늘(3/7) 새로 추가된 GODofIT 시그널: {today_sigs_total}개 ===')
for k, v in sorted(today_dist.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}개')

# 4. 전체 DB 시그널 (signal 컬럼 사용)
all_sig = get('influencer_signals?select=signal&limit=2000&offset=0')
all_dist = Counter(s['signal'] for s in all_sig)
print(f'\n=== 전체 DB 시그널: {len(all_sig)}개 ===')
for k, v in sorted(all_dist.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}개')
