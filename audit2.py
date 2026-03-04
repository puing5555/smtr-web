import requests, json

H = {
    'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
}
U = 'https://arypzhotxflimroprmdk.supabase.co/rest/v1'

videos = requests.get(f'{U}/influencer_videos?select=id,channel_id,video_id,title', headers=H).json()

# Search for guest keywords
kws = ['작가', '대표', '교수', '애널리스트', '전문가', '저자', '박사', '위원', '본부장', '거스', '사토시']
print("=== 게스트 키워드 포함 영상 ===")
found = 0
for v in videos:
    t = v.get('title') or ''
    matching = [k for k in kws if k in t]
    if matching:
        found += 1
        print(f"  {v['id'][:8]} | {matching} | {t}")

print(f"\n총 {found}건 / {len(videos)}개 영상")

# Also check: what are the host-assigned signals on 이효석아카데미?
# 이효석 is the host with 460 signals - are any of those actually guest episodes?
signals = requests.get(f'{U}/influencer_signals?select=id,video_id,speaker_id,stock,signal', headers=H).json()
speakers = requests.get(f'{U}/speakers?select=id,name', headers=H).json()
sp_map = {s['id']: s['name'] for s in speakers}
vid_map = {v['id']: v for v in videos}

# 이효석 speaker id
efseok_id = next(s['id'] for s in speakers if s['name'] == '이효석')
print(f"\n=== 이효석(호스트)에게 연결된 시그널의 영상 제목 ===")
efseok_sigs = [s for s in signals if s['speaker_id'] == efseok_id]
seen_vids = set()
for s in efseok_sigs:
    vid = vid_map.get(s['video_id'])
    if vid and vid['id'] not in seen_vids:
        seen_vids.add(vid['id'])
        print(f"  {vid['title']}")
