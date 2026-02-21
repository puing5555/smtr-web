"""Fetch upload dates using YouTube page HTML parsing with flush"""
import json, sys, re, time
sys.stdout.reconfigure(encoding='utf-8')
from urllib.request import urlopen, Request

with open('_all_videos.json', 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"Fetching dates for {len(videos)} videos...", flush=True)
updated = 0

for i, v in enumerate(videos):
    vid = v.get('id', '')
    if v.get('date'):
        updated += 1
        continue
    
    try:
        url = f"https://www.youtube.com/watch?v={vid}"
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        raw = urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
        
        # Try uploadDate in JSON-LD or microdata
        m = re.search(r'"uploadDate"\s*:\s*"(\d{4}-\d{2}-\d{2})', raw)
        if not m:
            m = re.search(r'"publishDate"\s*:\s*"(\d{4}-\d{2}-\d{2})', raw)
        if not m:
            m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', raw)
        
        if m:
            v['date'] = m.group(1)
            updated += 1
            print(f"  [{i+1}/{len(videos)}] {vid} -> {v['date']}", flush=True)
        else:
            print(f"  [{i+1}/{len(videos)}] {vid} -> NOT FOUND", flush=True)
        
        time.sleep(1)
    except Exception as e:
        print(f"  [{i+1}/{len(videos)}] {vid} -> ERROR: {e}", flush=True)
        time.sleep(2)

with open('_all_videos.json', 'w', encoding='utf-8') as f:
    json.dump(videos, f, ensure_ascii=False, indent=2)

print(f"\nTotal with dates: {updated}/{len(videos)}", flush=True)
