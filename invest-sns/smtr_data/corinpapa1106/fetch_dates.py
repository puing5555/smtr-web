#!/usr/bin/env python3
"""Fetch video publish dates from YouTube via web scraping"""
import json
import re
import urllib.request
import time
import os

def get_publish_date(video_id):
    """Get publish date from YouTube page"""
    url = f"https://www.youtube.com/watch?v={video_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        # Look for publishDate in JSON-LD or meta
        m = re.search(r'"publishDate"\s*:\s*"(\d{4}-\d{2}-\d{2})"', html)
        if m:
            return m.group(1)
        m = re.search(r'"uploadDate"\s*:\s*"(\d{4}-\d{2}-\d{2})"', html)
        if m:
            return m.group(1)
        m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})"', html)
        if m:
            return m.group(1)
    except Exception as e:
        print(f"  Error {video_id}: {e}")
    return None

# Load signals to get video IDs we care about
with open('_deduped_signals_8types.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

video_ids = list(set(s['video_id'] for s in signals))
print(f"Need dates for {len(video_ids)} videos")

# Load existing dates cache
cache_path = '_video_dates.json'
dates = {}
if os.path.exists(cache_path):
    with open(cache_path, 'r', encoding='utf-8') as f:
        dates = json.load(f)

todo = [vid for vid in video_ids if vid not in dates]
print(f"Already cached: {len(dates)}, Todo: {len(todo)}")

for i, vid in enumerate(todo):
    date = get_publish_date(vid)
    if date:
        dates[vid] = date
        print(f"  [{i+1}/{len(todo)}] {vid}: {date}")
    else:
        dates[vid] = ""
        print(f"  [{i+1}/{len(todo)}] {vid}: not found")
    
    if (i+1) % 10 == 0:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(dates, f, indent=2)
    time.sleep(0.5)

with open(cache_path, 'w', encoding='utf-8') as f:
    json.dump(dates, f, indent=2)

found = sum(1 for d in dates.values() if d)
print(f"\nDone. Found dates: {found}/{len(video_ids)}")
