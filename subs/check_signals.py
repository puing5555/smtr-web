import httpx, json

base = 'https://arypzhotxflimroprmdk.supabase.co/rest/v1'
headers = {
    'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
}

r = httpx.get(base + '/influencer_signals?select=id,stock,signal,speaker_id,video_id,created_at,influencer_videos(title,published_at,video_id,influencer_channels(channel_name)),speakers(name)&order=created_at.desc&limit=40', headers=headers)
data = r.json()
print(f'Total signals: {len(data)}')

for i, s in enumerate(data):
    speaker = s.get('speakers') or {}
    video = s.get('influencer_videos') or {}
    channel = (video.get('influencer_channels') or {})
    sp_name = speaker.get('name', 'NULL') if speaker else 'NULL'
    ch_name = channel.get('channel_name', 'NULL') if channel else 'NULL'
    pub = (video.get('published_at') or 'NULL')[:10]
    created = s['created_at'][:16]
    print(f"{i+1}. {s['stock']:12s} | {s['signal']:4s} | {sp_name:8s} | {ch_name:10s} | pub:{pub} | created:{created}")
