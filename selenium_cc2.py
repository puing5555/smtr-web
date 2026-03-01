import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

vid = "5mvn3PfKf9Y"
prefix = "dalant"
SUBS_DIR = r"C:\Users\Mario\work\subs"
out_file = os.path.join(SUBS_DIR, f"{prefix}_{vid}.json")

if os.path.exists(out_file):
    print(f"Already exists!")
    sys.exit(0)

opts = Options()
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
opts.add_argument("--no-first-run")
opts.add_argument("--autoplay-policy=no-user-gesture-required")

print("Starting Chrome...")
driver = webdriver.Chrome(options=opts)
driver.set_window_size(1280, 720)

print(f"Loading {vid}...")
driver.get(f"https://www.youtube.com/watch?v={vid}")
time.sleep(6)

duration = driver.execute_script("return document.querySelector('#movie_player video').duration")
print(f"Duration: {duration}s")

# Enable CC
driver.execute_script("""
    const btn = document.querySelector('.ytp-subtitles-button');
    if (btn && btn.getAttribute('aria-pressed') !== 'true') btn.click();
""")
time.sleep(1)

# Check CC state
cc_state = driver.execute_script("""
    const btn = document.querySelector('.ytp-subtitles-button');
    return btn ? btn.getAttribute('aria-pressed') : 'no button';
""")
print(f"CC state: {cc_state}")

# Set speed and play
driver.execute_script("document.querySelector('#movie_player video').playbackRate = 16;")
actual_speed = driver.execute_script("return document.querySelector('#movie_player video').playbackRate")
print(f"Playback speed: {actual_speed}x")

driver.execute_script("document.querySelector('#movie_player video').play();")
time.sleep(1)

paused = driver.execute_script("return document.querySelector('#movie_player video').paused")
print(f"Paused: {paused}")

captions = []
seen = set()
start_time = time.time()
max_wait = duration / actual_speed + 60
last_report = 0

print(f"Collecting captions (max {max_wait:.0f}s)...")

while time.time() - start_time < max_wait:
    try:
        current_time = driver.execute_script(
            "return document.querySelector('#movie_player video').currentTime"
        )
        
        segments = driver.find_elements(By.CSS_SELECTOR, ".ytp-caption-segment")
        for seg in segments:
            text = seg.text.strip()
            if text and text not in seen and text != "Korean (auto-generated)":
                seen.add(text)
                captions.append({
                    "text": text,
                    "start": round(current_time, 1),
                    "duration": 3.0
                })
        
        # Report every 10 seconds
        elapsed = time.time() - start_time
        if elapsed - last_report >= 10:
            last_report = elapsed
            print(f"  {elapsed:.0f}s elapsed | video {current_time:.0f}/{duration:.0f}s | {len(captions)} captions")
        
        if current_time >= duration - 1:
            print(f"Video ended at {current_time:.1f}s")
            break
        
    except Exception as e:
        print(f"  err: {str(e)[:60]}")
    
    time.sleep(0.2)

if captions:
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump({"video_id": vid, "subtitles": captions}, f, ensure_ascii=False, indent=2)
    print(f"OK! {len(captions)} captions saved")
else:
    print("No captions captured!")

driver.quit()
print("Done!")
