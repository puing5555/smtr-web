import requests, json, re

H = {
    'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
}
SK = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
WH = {'apikey': SK, 'Authorization': f'Bearer {SK}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}
U = 'https://arypzhotxflimroprmdk.supabase.co/rest/v1'

speakers = requests.get(f'{U}/speakers?select=*', headers=H).json()
channels = requests.get(f'{U}/influencer_channels?select=*', headers=H).json()
videos = requests.get(f'{U}/influencer_videos?select=id,channel_id,video_id,title', headers=H).json()
signals = requests.get(f'{U}/influencer_signals?select=id,video_id,speaker_id,stock,ticker,signal', headers=H).json()

sp_map = {s['id']: s['name'] for s in speakers}
sp_by_name = {s['name']: s for s in speakers}
vid_map = {v['id']: v for v in videos}
ch_map = {c['id']: c for c in channels}

# Known channel hosts (manually mapped based on data)
CHANNEL_HOSTS = {
    '이효석아카데미': '이효석',
    '삼프로TV': None,  # Multiple hosts
    '코린이 아빠': '코린이 아빠',
    '부읽남TV': None,  # Multiple hosts  
    '슈카월드': '슈카',
    '달란트투자': '달란트투자',
    '세상학개론': '세상학개론',
    '월가아재': '월가아재',
}

# Build channel_id -> host speaker_id
ch_host_map = {}
for ch in channels:
    host_name = CHANNEL_HOSTS.get(ch['channel_name'])
    if host_name:
        host_sp = sp_by_name.get(host_name)
        if host_sp:
            ch_host_map[ch['id']] = host_sp['id']

print("채널-호스트 매핑:")
for ch_id, sp_id in ch_host_map.items():
    print(f"  {ch_map[ch_id]['channel_name']} → {sp_map[sp_id]}")

# Guest keywords
GUEST_KW = ["작가", "대표", "교수", "애널리스트", "전문가", "저자", "박사", "위원", "본부장", "센터장", "팀장", "이사", "실장", "소장", "원장", "연구원", "기자"]

def extract_guest_name(title):
    """Extract guest name from title. Returns (name, role) or None"""
    # Specific patterns first
    specific = [
        (r'거스\s*쿤\s*작가', '거스 쿤', '작가'),
        (r'IT의\s*신\s*이형수\s*대표', None, None),  # This IS the host
        (r'이효석\s*HS아카데미\s*대표', None, None),  # This IS the host
    ]
    for pat, name, role in specific:
        if re.search(pat, title):
            if name is None:
                return None  # It's the host, not a guest
            return name
    
    # Generic: "이름 직함" pattern
    # But exclude host names
    patterns = [
        # Korean name + role
        r'([가-힣]{2,4})\s+(작가|대표|교수|박사|애널리스트|전문가|위원|본부장|센터장|팀장|이사|실장|소장|원장|연구위원|기자|저자|총괄)',
        # "직함 이름" in some formats - less common
    ]
    
    for p in patterns:
        matches = re.findall(p, title)
        for name, role in matches:
            # Skip if it's the channel host
            if name in ['이효석', '코린이']:
                continue
            return f"{name} {role}" if role not in ['대표'] else name
    
    return None

# Find all guest-keyword videos with signals pointing to host
print("\n=== 전수 조사 ===")
issues = []

for v in videos:
    title = v.get('title') or ''
    ch_id = v['channel_id']
    host_sp_id = ch_host_map.get(ch_id)
    
    if not host_sp_id:
        continue  # Skip channels without clear host
    
    # Check if title has guest keywords
    has_kw = any(kw in title for kw in GUEST_KW)
    if not has_kw:
        continue
    
    # Extract guest name
    guest_name = extract_guest_name(title)
    if not guest_name:
        continue  # Could be host's own title mention
    
    # Find signals for this video pointing to host
    vid_sigs = [s for s in signals if s['video_id'] == v['id'] and s['speaker_id'] == host_sp_id]
    
    if vid_sigs:
        host_name = sp_map[host_sp_id]
        ch_name = ch_map[ch_id]['channel_name']
        print(f"\n⚠️  [{ch_name}] {title}")
        print(f"   게스트: {guest_name} | 호스트({host_name})에 잘못 연결된 시그널: {len(vid_sigs)}건")
        for s in vid_sigs:
            print(f"   - {s['stock']} ({s['ticker']}) {s['signal']} [sig={s['id'][:8]}]")
            issues.append({
                'signal_id': s['id'],
                'video_id': v['id'],
                'title': title,
                'channel_id': ch_id,
                'host_speaker_id': host_sp_id,
                'host_name': host_name,
                'guest_name': guest_name,
                'stock': s['stock'],
                'ticker': s['ticker'],
                'signal': s['signal'],
            })

print(f"\n\n총 문제 시그널: {len(issues)}건")

if not issues:
    print("수정할 건 없음!")
else:
    # Execute fixes
    from collections import defaultdict
    guest_groups = defaultdict(list)
    for i in issues:
        guest_groups[i['guest_name']].append(i)
    
    created = {}
    updated = []
    
    for gname, sigs in guest_groups.items():
        # Find or create speaker
        existing = sp_by_name.get(gname) or created.get(gname)
        if not existing:
            r = requests.post(f'{U}/speakers', headers=WH, json={'name': gname, 'aliases': [gname]})
            r.raise_for_status()
            new_sp = r.json()[0] if isinstance(r.json(), list) else r.json()
            created[gname] = new_sp
            existing = new_sp
            print(f"\n🆕 스피커 생성: {gname} (id={existing['id']})")
        
        for sig in sigs:
            r = requests.patch(
                f"{U}/influencer_signals?id=eq.{sig['signal_id']}",
                headers=WH,
                json={'speaker_id': existing['id']}
            )
            r.raise_for_status()
            updated.append(sig)
            print(f"🔄 sig#{sig['signal_id'][:8]}: {sig['host_name']} → {gname} ({sig['stock']})")
    
    print(f"\n✅ 완료!")
    print(f"  새 스피커 생성: {len(created)}명 - {list(created.keys())}")
    print(f"  시그널 수정: {len(updated)}건")
    
    # Save report
    report = {
        'issues_found': len(issues),
        'fixes_applied': len(updated),
        'new_speakers': {k: v['id'] for k, v in created.items()},
        'updates': [{'signal_id': u['signal_id'], 'old': u['host_name'], 'new': u['guest_name'], 'stock': u['stock'], 'title': u['title']} for u in updated],
    }
    with open('guest_speaker_audit_result.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("결과 저장: guest_speaker_audit_result.json")
