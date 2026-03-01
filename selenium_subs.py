import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

VIDEOS = [
    {"video_id": "bmXgryWXNrw", "prefix": "hyoseok"},
    {"video_id": "5mvn3PfKf9Y", "prefix": "dalant"},
]
SUBS_DIR = r"C:\Users\Mario\work\subs"

opts = Options()
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
# Fresh profile (no existing Chrome conflict)
opts.add_argument("--no-first-run")
opts.add_argument("--no-default-browser-check")
opts.add_argument("--headless=new")

print("Starting Chrome...")
driver = webdriver.Chrome(options=opts)
print("Chrome started")

for item in VIDEOS:
    vid = item['video_id']
    prefix = item['prefix']
    out_file = os.path.join(SUBS_DIR, f"{prefix}_{vid}.json")
    
    if os.path.exists(out_file):
        print(f"[SKIP] {vid}")
        continue
    
    print(f"\n[{vid}] Loading video page...")
    driver.get(f"https://www.youtube.com/watch?v={vid}")
    time.sleep(5)
    
    # Extract caption track URL from player response
    try:
        tracks_json = driver.execute_script("""
            try {
                const player = document.querySelector('#movie_player');
                const pd = player.getPlayerResponse();
                const tracks = pd.captions?.playerCaptionsTracklistRenderer?.captionTracks || [];
                return JSON.stringify(tracks.map(t => ({lang: t.languageCode, url: t.baseUrl})));
            } catch(e) {
                return 'ERROR: ' + e.message;
            }
        """)
        print(f"  Tracks: {tracks_json[:200]}")
        
        if tracks_json.startswith('ERROR'):
            print(f"  {tracks_json}")
            continue
        
        tracks = json.loads(tracks_json)
        if not tracks:
            print("  No caption tracks found")
            continue
        
        # Pick Korean or first available
        track = next((t for t in tracks if t['lang'] == 'ko'), tracks[0])
        sub_url = track['url'] + '&fmt=json3'
        
        print(f"  Fetching subtitles via browser...")
        # Navigate to the subtitle URL directly in the browser
        driver.get(sub_url)
        time.sleep(3)
        
        # Get the page text (should be JSON)
        body_text = driver.find_element("tag name", "body").text
        
        # Sometimes it's wrapped in <pre>
        try:
            pre = driver.find_element("tag name", "pre")
            body_text = pre.text
        except:
            pass
        
        try:
            data = json.loads(body_text)
        except:
            # Try getting page source
            src = driver.page_source
            # Extract JSON from source
            import re
            m = re.search(r'<pre[^>]*>(.*?)</pre>', src, re.DOTALL)
            if m:
                data = json.loads(m.group(1))
            else:
                # Try body innerText via JS
                raw = driver.execute_script("return document.body.innerText")
                data = json.loads(raw)
        
        snippets = []
        for event in data.get('events', []):
            if 'segs' not in event:
                continue
            text = ''.join(seg.get('utf8', '') for seg in event['segs']).strip()
            if not text:
                continue
            start = (event.get('tStartMs', 0)) / 1000.0
            dur = (event.get('dDurationMs', 0)) / 1000.0
            snippets.append({"text": text, "start": start, "duration": dur})
        
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump({"video_id": vid, "subtitles": snippets}, f, ensure_ascii=False, indent=2)
        
        print(f"  OK! {len(snippets)} snippets saved")
        
    except Exception as e:
        print(f"  FAILED: {e}")

driver.quit()
print("\nDone!")
