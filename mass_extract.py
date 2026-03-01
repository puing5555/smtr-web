"""Mass subtitle extraction for all DB videos missing subtitles"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import httpx, json, os, time, random
from youtube_transcript_api import YouTubeTranscriptApi

BASE = "https://arypzhotxflimroprmdk.supabase.co/rest/v1/"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
SUBS_DIR = r"C:\Users\Mario\work\subs"

# Get all videos from DB
r = httpx.get(BASE + "influencer_videos?select=id,video_id,title,has_subtitle,channel_id,influencer_channels(channel_name)&order=created_at.desc", headers=H)
videos = r.json()
print(f"Total videos in DB: {len(videos)}")

# Check which ones already have subs
existing_subs = set()
for f in os.listdir(SUBS_DIR):
    if f.endswith('.json') and '_' in f:
        vid_part = f.split('_', 1)[1].replace('.json', '')
        existing_subs.add(vid_part)

# Also check for txt files
for f in os.listdir(SUBS_DIR):
    if f.endswith('_fulltext.txt'):
        vid_part = f.split('_', 1)[1].replace('_fulltext.txt', '')
        existing_subs.add(vid_part)

ytt = YouTubeTranscriptApi()
success = 0
fail = 0
skip = 0
results = []

for v in videos:
    vid = v['video_id']
    channel = v.get('influencer_channels', {}).get('channel_name', 'unknown') if v.get('influencer_channels') else 'unknown'
    title = (v.get('title') or '')[:50]
    
    if vid in existing_subs:
        skip += 1
        continue
    
    # Determine prefix
    prefix_map = {
        '삼프로TV': 'sampro',
        '코린이 아빠': 'korini',
        '이효석아카데미': 'hyoseok',
        '슈카월드': 'syuka',
        '부읽남TV': 'booread',
        '달란트투자': 'dalant',
    }
    prefix = prefix_map.get(channel, 'other')
    
    out_json = os.path.join(SUBS_DIR, f"{prefix}_{vid}.json")
    out_txt = os.path.join(SUBS_DIR, f"{prefix}_{vid}_fulltext.txt")
    
    if os.path.exists(out_json):
        skip += 1
        existing_subs.add(vid)
        continue
    
    print(f"[{success+fail+1}] {vid} ({channel}) {title}... ", end='', flush=True)
    
    try:
        result = ytt.fetch(vid, languages=['ko', 'en'])
        snippets = [{"text": s.text, "start": s.start, "duration": s.duration} for s in result.snippets]
        
        # Save JSON
        with open(out_json, 'w', encoding='utf-8') as f:
            json.dump({"video_id": vid, "subtitles": snippets}, f, ensure_ascii=False, indent=2)
        
        # Save fulltext
        lines = []
        for s in snippets:
            m = int(s['start'] // 60)
            sec = int(s['start'] % 60)
            lines.append(f"[{m:02d}:{sec:02d}] {s['text']}")
        with open(out_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"OK ({len(snippets)} snippets)")
        success += 1
        results.append({"video_id": vid, "channel": channel, "snippets": len(snippets), "prefix": prefix})
        
        # Update DB has_subtitle
        httpx.patch(BASE + f"influencer_videos?video_id=eq.{vid}", 
                    json={"has_subtitle": True}, headers={**H, "Prefer": "return=representation"})
        
        time.sleep(random.uniform(1.0, 2.0))
        
    except Exception as e:
        err = str(e)[:80]
        print(f"FAIL: {err}")
        fail += 1
        if '429' in str(e) or 'IpBlocked' in str(e):
            print("  Rate limited! Waiting 30s...")
            time.sleep(30)

print(f"\n=== RESULTS ===")
print(f"Success: {success}, Failed: {fail}, Skipped (existing): {skip}")
print(f"New subtitles extracted:")
for r in results:
    print(f"  {r['video_id']} ({r['channel']}): {r['snippets']} snippets")

# Save results for pipeline
with open(os.path.join(SUBS_DIR, 'mass_extract_results.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
