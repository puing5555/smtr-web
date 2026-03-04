import os, json
from supabase import create_client

url = "https://arypzhotxflimroprmdk.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
sb = create_client(url, key)

# A-1: 시그널 총 수
r = sb.table("signals").select("id", count="exact").execute()
total = r.count
print(f"A-1: 시그널 총 수 = {total}")

# A-2: 채널 수
r2 = sb.table("channels").select("id", count="exact").execute()
print(f"A-2: 채널 수 = {r2.count}")

# A-5: published_at NULL
r3 = sb.table("signals").select("id").is_("published_at", "null").execute()
null_pub = len(r3.data)
print(f"A-5: published_at NULL = {null_pub} {'✅' if null_pub==0 else '❌'}")

# A-6: 중복 (video_id + ticker)
r4 = sb.table("signals").select("video_id,ticker").execute()
pairs = [(d['video_id'], d['ticker']) for d in r4.data]
dupes = len(pairs) - len(set(pairs))
print(f"A-6: 중복(video_id+ticker) = {dupes} {'✅' if dupes==0 else '❌'}")
if dupes > 0:
    from collections import Counter
    c = Counter(pairs)
    for p, cnt in c.most_common(5):
        if cnt > 1:
            print(f"  중복: {p} x{cnt}")

# A-7: 스피커 검증
r5 = sb.table("signals").select("id,speaker_name,video_title,channel_name").eq("channel_name","이효석아카데미").eq("speaker_name","이효석").limit(10).execute()
print(f"\nA-7: 이효석아카데미 speaker=이효석 샘플 ({len(r5.data)}개):")
guest_names = ["홍춘욱","박세익","김경록","오건영","이선엽","김일구","박종훈","강영현","이지영","한정수","신영재","염승환","석경철","정원호"]
a7_fail = 0
for d in r5.data:
    title = d.get('video_title','')
    found_guests = [g for g in guest_names if g in title]
    status = "❌ 게스트발견:" + ",".join(found_guests) if found_guests else "✅"
    if found_guests: a7_fail += 1
    print(f"  [{status}] {title[:60]}")
print(f"A-7 결과: {'❌ 실패 '+str(a7_fail)+'건' if a7_fail else '✅ PASS'}")

# F-3: 필수 필드 NULL
for field in ["ticker","signal_type","key_quote","timestamp"]:
    r6 = sb.table("signals").select("id").is_(field, "null").execute()
    n = len(r6.data)
    print(f"F-3: {field} NULL = {n} {'✅' if n==0 else '❌'}")

# 상식 검증: 랜덤 5개
import random
r7 = sb.table("signals").select("id,video_title,speaker_name,ticker,signal_type,key_quote,channel_name").execute()
samples = random.sample(r7.data, min(5, len(r7.data)))
print(f"\n🧠 상식 검증 (5개 샘플):")
for s in samples:
    print(f"---")
    print(f"  채널: {s.get('channel_name','?')}")
    print(f"  제목: {s.get('video_title','?')[:80]}")
    print(f"  스피커: {s.get('speaker_name','?')}")
    print(f"  종목: {s.get('ticker','?')}")
    print(f"  시그널: {s.get('signal_type','?')}")
    print(f"  인용: {(s.get('key_quote','?') or '?')[:100]}")
