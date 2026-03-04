import requests
import json
import re

URL = "https://arypzhotxflimroprmdk.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

READ_HEADERS = {"apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}"}
WRITE_HEADERS = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

def get(table, params=""):
    r = requests.get(f"{URL}/rest/v1/{table}?{params}", headers=READ_HEADERS)
    r.raise_for_status()
    return r.json()

def post(table, data):
    r = requests.post(f"{URL}/rest/v1/{table}", headers=WRITE_HEADERS, json=data)
    r.raise_for_status()
    return r.json()

def patch(table, params, data):
    h = {**WRITE_HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{URL}/rest/v1/{table}?{params}", headers=h, json=data)
    r.raise_for_status()
    return r.json()

# 1. Get all speakers
speakers = get("speakers", "select=id,name,channel_id")
print(f"총 스피커: {len(speakers)}명")
for s in speakers:
    print(f"  {s['id']}: {s['name']} (channel_id={s.get('channel_id')})")

# Map channel_id -> host speaker
host_speakers = {s['channel_id']: s for s in speakers if s.get('channel_id')}
guest_speakers = {s['name']: s for s in speakers if not s.get('channel_id')}
print(f"\n호스트: {len(host_speakers)}명, 게스트: {len(guest_speakers)}명")

# 2. Get all videos
videos = get("influencer_videos", "select=id,channel_id,video_id,title&order=id.asc")
print(f"\n총 영상: {len(videos)}개")

# 3. Find videos with guest keywords in title
GUEST_KEYWORDS = ["작가", "대표", "교수", "애널리스트", "전문가", "저자", "박사", "위원", "본부장", "센터장", "팀장", "이사", "실장", "소장", "원장", "연구원", "기자"]

guest_videos = []
for v in videos:
    title = v.get('title', '') or ''
    for kw in GUEST_KEYWORDS:
        if kw in title:
            guest_videos.append(v)
            break

print(f"\n게스트 키워드 포함 영상: {len(guest_videos)}개")
for v in guest_videos:
    print(f"  [{v['channel_id']}] {v['title']}")

# 4. For each guest video, check if signals have host speaker
print("\n=== 시그널 조사 ===")
issues = []
for v in guest_videos:
    sigs = get("influencer_signals", f"select=id,video_id,speaker_id,stock,ticker,signal&video_id=eq.{v['video_id']}")
    if not sigs:
        continue
    host = host_speakers.get(v['channel_id'])
    if not host:
        continue
    for sig in sigs:
        if sig['speaker_id'] == host['id']:
            issues.append({
                'signal_id': sig['id'],
                'video_id': v['video_id'],
                'title': v['title'],
                'channel_id': v['channel_id'],
                'host_name': host['name'],
                'stock': sig.get('stock'),
                'ticker': sig.get('ticker'),
                'signal': sig.get('signal'),
            })

print(f"\n🔍 호스트로 잘못 연결된 시그널: {len(issues)}건")
for i in issues:
    print(f"  시그널#{i['signal_id']}: [{i['host_name']}→?] {i['title']} | {i['stock']} ({i['ticker']}) {i['signal']}")

# 5. Extract guest names from titles and fix
# Pattern: "이름 직함" like "거스 쿤 작가", "홍춘욱 박사"
def extract_guest_name(title):
    """Try to extract guest name from title"""
    patterns = [
        # "이름 직함 (설명)" - 2-4 char name + title
        r'([가-힣]{2,4})\s*(작가|대표|교수|박사|애널리스트|전문가|위원|본부장|센터장|팀장|이사|실장|소장|원장|연구원|기자)',
        # "외국이름 직함"
        r'([가-힣a-zA-Z\s]{2,10}?)\s*(작가|대표|교수|박사|애널리스트|전문가|위원)',
        # Specific: 거스 쿤 작가
        r'(거스\s*쿤)\s*작가',
    ]
    for p in patterns:
        m = re.search(p, title)
        if m:
            name = m.group(1).strip()
            role = m.group(2).strip()
            return f"{name} {role}"
    return None

print("\n=== 게스트 이름 추출 및 수정 ===")
fixes = []
for issue in issues:
    guest_name = extract_guest_name(issue['title'])
    if guest_name:
        issue['guest_name'] = guest_name
        fixes.append(issue)
        print(f"  ✅ {issue['title']} → 게스트: {guest_name}")
    else:
        print(f"  ❓ 이름 추출 실패: {issue['title']}")

# 6. Create missing guest speakers and update signals
created_speakers = {}
updated_signals = []

for fix in fixes:
    guest_name = fix['guest_name']
    
    # Check if guest speaker already exists
    existing = None
    for s in speakers:
        if s['name'] == guest_name:
            existing = s
            break
    if guest_name in created_speakers:
        existing = created_speakers[guest_name]
    
    if not existing:
        # Create new guest speaker
        result = post("speakers", {"name": guest_name, "channel_id": None})
        new_speaker = result[0] if isinstance(result, list) else result
        created_speakers[guest_name] = new_speaker
        print(f"\n  🆕 게스트 스피커 생성: {guest_name} (id={new_speaker['id']})")
        speakers.append(new_speaker)
        existing = new_speaker
    
    # Update signal speaker_id
    result = patch("influencer_signals", f"id=eq.{fix['signal_id']}", {"speaker_id": existing['id']})
    updated_signals.append({
        'signal_id': fix['signal_id'],
        'old_speaker': fix['host_name'],
        'new_speaker': guest_name,
        'new_speaker_id': existing['id'],
        'stock': fix['stock'],
        'title': fix['title'],
    })
    print(f"  🔄 시그널#{fix['signal_id']}: {fix['host_name']} → {guest_name} ({fix['stock']})")

print(f"\n=== 최종 결과 ===")
print(f"총 조사 영상: {len(guest_videos)}개")
print(f"문제 시그널 발견: {len(issues)}건")
print(f"이름 추출 성공: {len(fixes)}건")
print(f"새 게스트 스피커 생성: {len(created_speakers)}명")
print(f"시그널 수정: {len(updated_signals)}건")

# Save report
report = {
    "issues_found": len(issues),
    "fixes_applied": len(updated_signals),
    "new_speakers": list(created_speakers.keys()),
    "details": updated_signals,
    "unresolved": [i for i in issues if i not in fixes],
}
with open("guest_speaker_audit_result.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print("\n결과 저장: guest_speaker_audit_result.json")
