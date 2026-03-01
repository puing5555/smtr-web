import sys; sys.stdout.reconfigure(encoding='utf-8')
import httpx, os

BASE = 'https://arypzhotxflimroprmdk.supabase.co/rest/v1/'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}'}

vids = httpx.get(BASE + 'influencer_videos?select=id,video_id,channel_id,title&limit=1000', headers=H).json()
sigs = httpx.get(BASE + 'influencer_signals?select=video_id&limit=1000', headers=H).json()
sig_vid_ids = set(s['video_id'] for s in sigs)

chs = httpx.get(BASE + 'influencer_channels?select=id,channel_name&limit=100', headers=H).json()
ch_map = {c['id']: c['channel_name'] for c in chs}

print('=== Videos WITHOUT signals ===')
count = 0
for v in vids:
    if v['id'] not in sig_vid_ids:
        ch = ch_map.get(v['channel_id'], '?')
        has_sub = any(f.endswith('_fulltext.txt') and v['video_id'] in f 
                     for f in os.listdir('.'))
        sub_size = 0
        if has_sub:
            for f in os.listdir('.'):
                if f.endswith('_fulltext.txt') and v['video_id'] in f:
                    sub_size = os.path.getsize(f)
                    break
        status = f'SUB({sub_size//1024}KB)' if has_sub else 'NO_SUB'
        print(f"  {ch} | {v['video_id']} | {status} | {v['title'][:50]}")
        count += 1

print(f'\nTotal: {count} videos without signals')

# Not in DB at all
db_ytids = set(v['video_id'] for v in vids)
print('\n=== Subtitle files NOT in DB ===')
for f in sorted(os.listdir('.')):
    if f.endswith('_fulltext.txt') and os.path.getsize(f) > 500:
        parts = f.replace('_fulltext.txt', '').split('_', 1)
        if len(parts) == 2 and parts[1] not in db_ytids:
            print(f"  {f}")
