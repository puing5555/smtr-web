"""
Browser-based subtitle extraction script.
Reads subtitle URLs from browser_subs_urls.json and fetches them.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import os
import requests
import re

SUBS_DIR = r"C:\Users\Mario\work\subs"

with open(r"C:\Users\Mario\work\browser_subs_urls.json", 'r') as f:
    data = json.load(f)

for item in data:
    vid = item['video_id']
    prefix = item['prefix']
    url = item['url']
    out_file = os.path.join(SUBS_DIR, f"{prefix}_{vid}.json")
    
    if os.path.exists(out_file):
        print(f"[SKIP] {vid}")
        continue
    
    # Fetch the timed text as json3
    try:
        resp = requests.get(url + "&fmt=json3", timeout=15)
        resp.raise_for_status()
        j3 = resp.json()
        
        snippets = []
        for event in j3.get('events', []):
            if 'segs' not in event:
                continue
            text = ''.join(seg.get('utf8', '') for seg in event['segs']).strip()
            if not text:
                continue
            start = event.get('tStartMs', 0) / 1000.0
            dur = event.get('dDurationMs', 0) / 1000.0
            snippets.append({"text": text, "start": start, "duration": dur})
        
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump({"video_id": vid, "subtitles": snippets}, f, ensure_ascii=False, indent=2)
        
        print(f"OK {vid}: {len(snippets)} snippets")
    except Exception as e:
        print(f"FAIL {vid}: {e}")
