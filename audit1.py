import requests, json

H = {
    'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
}
SK = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
WH = {'apikey': SK, 'Authorization': f'Bearer {SK}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}
U = 'https://arypzhotxflimroprmdk.supabase.co/rest/v1'

# Get all data
speakers = requests.get(f'{U}/speakers?select=*', headers=H).json()
channels = requests.get(f'{U}/influencer_channels?select=*', headers=H).json()
videos = requests.get(f'{U}/influencer_videos?select=id,channel_id,video_id,title,published_at', headers=H).json()
signals = requests.get(f'{U}/influencer_signals?select=id,video_id,speaker_id,stock,ticker,signal,review_status', headers=H).json()

print(f"스피커: {len(speakers)}명, 채널: {len(channels)}개, 영상: {len(videos)}개, 시그널: {len(signals)}개")

# Print all speakers
for s in speakers:
    print(f"  스피커: {s['name']} | id={s['id'][:8]}... | aliases={s.get('aliases')}")

# Print all channels
for c in channels:
    print(f"  채널: {c['channel_name']} | id={c['id'][:8]}...")

# Figure out which speaker is host of which channel
# Approach: for each channel, find the most common speaker_id in its videos' signals
print("\n=== 채널별 호스트 추정 ===")
video_map = {v['id']: v for v in videos}
channel_speaker_counts = {}
for sig in signals:
    vid = video_map.get(sig['video_id'])
    if not vid:
        continue
    ch = vid['channel_id']
    sp = sig['speaker_id']
    key = (ch, sp)
    channel_speaker_counts[key] = channel_speaker_counts.get(key, 0) + 1

# For each channel, find top speaker
channel_hosts = {}
ch_map = {c['id']: c for c in channels}
for ch_id in set(v['channel_id'] for v in videos):
    counts = {sp: cnt for (c, sp), cnt in channel_speaker_counts.items() if c == ch_id}
    if counts:
        top_sp = max(counts, key=counts.get)
        sp_name = next((s['name'] for s in speakers if s['id'] == top_sp), '?')
        ch_name = ch_map.get(ch_id, {}).get('channel_name', '?')
        channel_hosts[ch_id] = top_sp
        print(f"  {ch_name}: 호스트={sp_name} ({counts[top_sp]}건)")
        # Show all speakers for this channel
        for sp_id, cnt in sorted(counts.items(), key=lambda x: -x[1]):
            sp_n = next((s['name'] for s in speakers if s['id'] == sp_id), '?')
            if sp_id != top_sp:
                print(f"    게스트: {sp_n} ({cnt}건)")

# Now find guest videos where all signals point to host
GUEST_KW = ["작가", "대표", "교수", "애널리스트", "전문가", "저자", "박사", "위원", "본부장", "센터장", "팀장", "이사", "실장", "소장", "원장", "연구원", "기자"]

print("\n=== 게스트 키워드 포함 영상 조사 ===")
import re

issues = []
for v in videos:
    title = v.get('title') or ''
    has_kw = any(kw in title for kw in GUEST_KW)
    if not has_kw:
        continue
    
    ch_id = v['channel_id']
    host_sp = channel_hosts.get(ch_id)
    if not host_sp:
        continue
    
    # Get signals for this video that point to host
    vid_sigs = [s for s in signals if s['video_id'] == v['video_id'] and s['speaker_id'] == host_sp]
    if vid_sigs:
        host_name = next((s['name'] for s in speakers if s['id'] == host_sp), '?')
        print(f"\n⚠️  [{ch_map.get(ch_id,{}).get('channel_name','?')}] {title}")
        print(f"   호스트({host_name})로 연결된 시그널 {len(vid_sigs)}건:")
        for s in vid_sigs:
            print(f"   - sig#{s['id'][:8]}: {s['stock']} ({s['ticker']}) {s['signal']}")
            issues.append({
                'signal_id': s['id'],
                'video_id': v['video_id'],
                'title': title,
                'channel_id': ch_id,
                'host_speaker_id': host_sp,
                'host_name': host_name,
                'stock': s['stock'],
                'ticker': s['ticker'],
                'signal': s['signal'],
            })

print(f"\n총 문제 시그널: {len(issues)}건")

# Extract guest names
def extract_guest(title):
    patterns = [
        r'(거스\s*쿤)\s*작가',
        r'([가-힣]{2,4})\s*(작가|대표|교수|박사|애널리스트|전문가|위원|본부장|센터장|팀장|이사|실장|소장|원장|연구원|기자|저자)',
    ]
    for p in patterns:
        m = re.search(p, title)
        if m:
            if len(m.groups()) == 1:
                return m.group(1).strip()
            return f"{m.group(1).strip()} {m.group(2).strip()}"
    return None

# Group by video and extract guest name
from collections import defaultdict
video_issues = defaultdict(list)
for i in issues:
    video_issues[i['video_id']].append(i)

print("\n=== 게스트 이름 추출 ===")
fixes_plan = []
for vid, sigs in video_issues.items():
    title = sigs[0]['title']
    guest = extract_guest(title)
    print(f"  {title} → 게스트: {guest or '❓추출실패'}")
    if guest:
        for s in sigs:
            fixes_plan.append({**s, 'guest_name': guest})

print(f"\n수정 예정: {len(fixes_plan)}건")

# Execute fixes
if fixes_plan:
    # Find or create guest speakers
    sp_by_name = {s['name']: s for s in speakers}
    created = {}
    updated = []
    
    for fix in fixes_plan:
        gname = fix['guest_name']
        
        # Check existing
        existing = sp_by_name.get(gname) or created.get(gname)
        if not existing:
            # Create
            r = requests.post(f'{U}/speakers', headers=WH, json={'name': gname, 'aliases': [gname]})
            r.raise_for_status()
            new_sp = r.json()[0] if isinstance(r.json(), list) else r.json()
            created[gname] = new_sp
            existing = new_sp
            print(f"🆕 스피커 생성: {gname} (id={existing['id'][:8]}...)")
        
        # Update signal
        r = requests.patch(
            f"{U}/influencer_signals?id=eq.{fix['signal_id']}",
            headers=WH,
            json={'speaker_id': existing['id']}
        )
        r.raise_for_status()
        updated.append({
            'signal_id': fix['signal_id'],
            'old': fix['host_name'],
            'new': gname,
            'stock': fix['stock'],
        })
        print(f"🔄 시그널#{fix['signal_id'][:8]}: {fix['host_name']} → {gname} ({fix['stock']})")
    
    print(f"\n✅ 완료: {len(created)}명 스피커 생성, {len(updated)}건 시그널 수정")
    
    # Save report
    report = {
        'issues_found': len(issues),
        'fixes_applied': len(updated),
        'new_speakers': list(created.keys()),
        'updates': updated,
    }
    with open('guest_speaker_audit_result.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
else:
    print("수정할 건 없음")
