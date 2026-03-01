import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

VIDEOS = [
    {"video_id": "bmXgryWXNrw", "prefix": "hyoseok"},
    {"video_id": "5mvn3PfKf9Y", "prefix": "dalant"},
]
SUBS_DIR = r"C:\Users\Mario\work\subs"

opts = Options()
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
opts.add_argument("--no-first-run")
opts.add_argument("--no-default-browser-check")
opts.add_argument("--autoplay-policy=no-user-gesture-required")
# NOT headless — need real rendering for captions
# opts.add_argument("--headless=new")

print("Starting Chrome...")
driver = webdriver.Chrome(options=opts)
driver.set_window_size(1280, 720)
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
    
    # Get video duration
    duration = driver.execute_script("""
        try { return document.querySelector('#movie_player video').duration; }
        catch(e) { return 0; }
    """)
    print(f"  Duration: {duration}s")
    
    if not duration:
        print("  No video duration, skipping")
        continue
    
    # Enable CC
    driver.execute_script("""
        const btn = document.querySelector('.ytp-subtitles-button');
        if (btn && btn.getAttribute('aria-pressed') !== 'true') btn.click();
    """)
    time.sleep(1)
    
    # Set playback speed to max
    driver.execute_script("""
        document.querySelector('#movie_player video').playbackRate = 16;
    """)
    
    # Play video
    driver.execute_script("""
        document.querySelector('#movie_player video').play();
    """)
    time.sleep(1)
    
    # Collect captions
    captions = []
    seen = set()
    last_time = -1
    start_time = time.time()
    max_wait = duration / 16 + 30  # account for playback speed + buffer
    
    print(f"  Collecting captions (max {max_wait:.0f}s)...")
    
    while time.time() - start_time < max_wait:
        try:
            current_time = driver.execute_script(
                "return document.querySelector('#movie_player video').currentTime"
            )
            
            # Get caption text
            segments = driver.find_elements(By.CSS_SELECTOR, ".ytp-caption-segment")
            for seg in segments:
                text = seg.text.strip()
                if text and text not in seen:
                    seen.add(text)
                    captions.append({
                        "text": text,
                        "start": round(current_time, 1),
                        "duration": 3.0
                    })
            
            # Check if video ended
            if current_time >= duration - 1:
                print(f"  Video ended at {current_time:.1f}s")
                break
            
            if int(current_time) % 60 == 0 and current_time != last_time:
                last_time = int(current_time)
                print(f"  {current_time:.0f}/{duration:.0f}s - {len(captions)} captions")
            
        except Exception as e:
            pass
        
        time.sleep(0.3)
    
    if captions:
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump({"video_id": vid, "subtitles": captions}, f, ensure_ascii=False, indent=2)
        print(f"  OK! {len(captions)} captions saved")
    else:
        print(f"  No captions captured!")

driver.quit()
print("\nDone!")
