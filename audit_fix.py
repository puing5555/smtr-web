import requests, json

SK = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
H = {'apikey': SK, 'Authorization': f'Bearer {SK}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}
RH = {'apikey': SK, 'Authorization': f'Bearer {SK}'}
U = 'https://arypzhotxflimroprmdk.supabase.co/rest/v1'

speakers = requests.get(f'{U}/speakers?select=id,name', headers=RH).json()
sp_by_name = {s['name']: s['id'] for s in speakers}

# 이효석 speaker id
efseok_id = sp_by_name['이효석']
kangjs_id = sp_by_name['강정수']  # Already exists!

print("기존 강정수 id:", kangjs_id)
print("새로 만든 강정수 박사 id:", sp_by_name.get('강정수 박사'))

# Fix 1: "테슬라 전문가" → revert to 이효석 (compilation video, not a single guest)
print("\n1. 테슬라 전문가 → 이효석으로 되돌림 (모아보기 영상)")
sigs = requests.get(f'{U}/influencer_signals?select=id&speaker_id=eq.{sp_by_name["테슬라 전문가"]}', headers=RH).json()
for s in sigs:
    requests.patch(f'{U}/influencer_signals?id=eq.{s["id"]}', headers=H, json={'speaker_id': efseok_id}).raise_for_status()
    print(f"  reverted sig {s['id'][:8]}")
# Delete the bad speaker
requests.delete(f'{U}/speakers?id=eq.{sp_by_name["테슬라 전문가"]}', headers=H).raise_for_status()
print("  deleted speaker 테슬라 전문가")

# Fix 2: "자산운용 팀장" → rename to "김효식" (title: 김효식 삼성액티브자산운용 팀장)
print("\n2. 자산운용 팀장 → 김효식으로 이름 변경")
r = requests.patch(f'{U}/speakers?id=eq.{sp_by_name["자산운용 팀장"]}', headers=H, 
    json={'name': '김효식', 'aliases': ['김효식', '김효식 팀장']})
r.raise_for_status()
print(f"  renamed to 김효식: {r.json()}")

# Fix 3: "스탠포드 박사" → revert to 이효석 (title is vague, can't identify specific person)
print("\n3. 스탠포드 박사 → 이효석으로 되돌림 (구체적 게스트명 불명)")
sigs = requests.get(f'{U}/influencer_signals?select=id&speaker_id=eq.{sp_by_name["스탠포드 박사"]}', headers=RH).json()
for s in sigs:
    requests.patch(f'{U}/influencer_signals?id=eq.{s["id"]}', headers=H, json={'speaker_id': efseok_id}).raise_for_status()
    print(f"  reverted sig {s['id'][:8]}")
requests.delete(f'{U}/speakers?id=eq.{sp_by_name["스탠포드 박사"]}', headers=H).raise_for_status()
print("  deleted speaker 스탠포드 박사")

# Fix 4: "강정수 박사" → use existing "강정수" speaker
print("\n4. 강정수 박사 시그널 → 기존 강정수로 이동")
sigs = requests.get(f'{U}/influencer_signals?select=id&speaker_id=eq.{sp_by_name["강정수 박사"]}', headers=RH).json()
for s in sigs:
    requests.patch(f'{U}/influencer_signals?id=eq.{s["id"]}', headers=H, json={'speaker_id': kangjs_id}).raise_for_status()
    print(f"  moved sig {s['id'][:8]} to 강정수")
requests.delete(f'{U}/speakers?id=eq.{sp_by_name["강정수 박사"]}', headers=H).raise_for_status()
print("  deleted speaker 강정수 박사")

# Also check: the "거스 쿤 작가 1부" video - does it also have misassigned signals?
print("\n5. 거스 쿤 1부 확인")
videos = requests.get(f'{U}/influencer_videos?select=id,title&title=like.*거스*', headers=RH).json()
guskun_id = sp_by_name.get('거스 쿤')
for v in videos:
    print(f"  영상: {v['title']}")
    sigs = requests.get(f'{U}/influencer_signals?select=id,speaker_id,stock,signal&video_id=eq.{v["id"]}', headers=RH).json()
    for s in sigs:
        sp_name = next((sp['name'] for sp in speakers if sp['id'] == s['speaker_id']), '?')
        status = "✅" if s['speaker_id'] == guskun_id else f"⚠️ ({sp_name})"
        print(f"    {status} {s['stock']} {s['signal']} [speaker={sp_name}]")
        if s['speaker_id'] == efseok_id and guskun_id:
            # Fix it
            requests.patch(f'{U}/influencer_signals?id=eq.{s["id"]}', headers=H, json={'speaker_id': guskun_id}).raise_for_status()
            print(f"    🔄 fixed: 이효석 → 거스 쿤")

print("\n✅ 모든 수정 완료!")
print("\n최종 결과:")
print("  - 거스 쿤: 스피커 생성 + 시그널 수정 ✅")
print("  - 김효식: 스피커 생성(이름수정) + 시그널 5건 수정 ✅")
print("  - 강정수: 기존 스피커로 시그널 1건 이동 ✅")
print("  - 테슬라 전문가/스탠포드 박사: 되돌림 (모아보기/불명확)")
