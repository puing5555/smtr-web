"""Fetch upload dates for videos using web scraping"""
import json, sys, re, time
sys.stdout.reconfigure(encoding='utf-8')
from urllib.request import urlopen, Request

with open('_all_videos.json', 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"Fetching dates for {len(videos)} videos...")
updated = 0

for i, v in enumerate(videos):
    vid = v.get('id', '')
    if v.get('date'):
        continue
    
    try:
        url = f"https://www.youtube.com/watch?v={vid}"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US'})
        html = urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        
        # Try to find uploadDate in JSON-LD
        m = re.search(r'"uploadDate"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
        if m:
            v['date'] = m.group(1)
            updated += 1
            print(f"  [{i+1}/{len(videos)}] {vid} -> {v['date']}")
        else:
            # Try dateText
            m2 = re.search(r'"publishDate"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
            if m2:
                v['date'] = m2.group(1)
                updated += 1
                print(f"  [{i+1}/{len(videos)}] {vid} -> {v['date']}")
            else:
                print(f"  [{i+1}/{len(videos)}] {vid} -> NOT FOUND")
        
        time.sleep(0.5)
    except Exception as e:
        print(f"  [{i+1}/{len(videos)}] {vid} -> ERROR: {e}")
        time.sleep(1)

with open('_all_videos.json', 'w', encoding='utf-8') as f:
    json.dump(videos, f, ensure_ascii=False, indent=2)

print(f"\nUpdated {updated} dates")
