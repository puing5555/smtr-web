import sys; sys.stdout.reconfigure(encoding='utf-8')
import httpx, os, json

BASE = 'https://arypzhotxflimroprmdk.supabase.co/rest/v1/'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}'}

def get_all(table, select):
    """Paginate through all rows"""
    rows = []
    offset = 0
    while True:
        r = httpx.get(f"{BASE}{table}?select={select}&limit=1000&offset={offset}", headers=H)
        batch = r.json()
        if isinstance(batch, dict):
            print(f"Error: {batch}")
            break
        rows.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000
    return rows

vids = get_all('influencer_videos', 'id,youtube_id,channel_id,title')
print(f'Total videos in DB: {len(vids)}')
yt_ids = {}
for v in vids:
    yt_ids[v['youtube_id']] = v['id']
    print(f"  {v['youtube_id']} | {v['title'][:50]}")

sigs = get_all('influencer_signals', 'id,video_id')
sig_vids = set(s['video_id'] for s in sigs)
print(f'\nTotal signals: {len(sigs)}, across {len(sig_vids)} videos')

# Videos WITH record but NO signals
print('\n--- Videos in DB WITHOUT signals ---')
for v in vids:
    if v['id'] not in sig_vids:
        print(f"  {v['youtube_id']} | {v['title'][:50]}")

# Subtitle files without DB record
subs_dir = 'C:/Users/Mario/work/subs'
print('\n--- Subtitle files WITHOUT DB video record (>500b) ---')
for f in sorted(os.listdir(subs_dir)):
    if f.endswith('_fulltext.txt') and os.path.getsize(os.path.join(subs_dir, f)) > 500:
        parts = f.replace('_fulltext.txt', '').split('_', 1)
        if len(parts) == 2:
            yt_id = parts[1]
            if yt_id not in yt_ids:
                print(f"  NEW: {f} (yt_id={yt_id})")

channels = get_all('influencer_channels', 'id,channel_name')
speakers = get_all('speakers', 'id,name,channel_id')
print('\n--- Channels ---')
for c in channels:
    print(f"  {c['id'][:8]} | {c['channel_name']}")
print('\n--- Speakers ---')
for s in speakers:
    print(f"  {s['id'][:8]} | {s['name']} | ch={s['channel_id'][:8]}")
