"""Selenium으로 자막 URL 직접 접근 테스트 (브라우저 쿠키 활용)"""
import json, re, time, sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def setup():
    opts = Options()
    # NON-headless to use real browser profile
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--window-size=1920,1080')
    opts.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    svc = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=svc, options=opts)

vid = sys.argv[1] if len(sys.argv) > 1 else '1NUkBQ9MQf8'
print(f'Video: {vid}')

driver = setup()
print('Driver ready')

# Visit YouTube to establish session
driver.get('https://www.youtube.com/')
time.sleep(3)
print(f'Cookies after main: {len(driver.get_cookies())}')

# Visit video page
driver.get(f'https://www.youtube.com/watch?v={vid}')
time.sleep(5)
print(f'Video page loaded')

# Extract captionTracks
src = driver.page_source
match = re.search(r'"captionTracks":\s*(\[.*?\])', src)
if not match:
    print('No captionTracks')
    driver.quit()
    sys.exit(1)

tracks = json.loads(match.group(1).replace('\\u0026', '&'))
print(f'Tracks: {len(tracks)}')
track = next((t for t in tracks if t.get('languageCode') == 'ko'), tracks[0])
caption_url = track['baseUrl'] + '&fmt=json3'
print(f'Lang: {track.get("languageCode")}')

# Navigate to caption URL using the same browser session
time.sleep(2)
driver.get(caption_url)
time.sleep(3)

# Check response
try:
    body = driver.find_element(By.TAG_NAME, 'body').text
    if len(body) < 50:
        body = driver.find_element(By.TAG_NAME, 'pre').text
except:
    body = driver.page_source

if 'Sorry' in body[:200] or len(body) < 100:
    print(f'BLOCKED: {body[:200]}')
else:
    try:
        data = json.loads(body)
        events = data.get('events', [])
        segs = []
        for evt in events:
            ss = evt.get('segs', [])
            text = ''.join(s.get('utf8', '') for s in ss).strip()
            if text and text != '\n':
                segs.append({'start': evt.get('tStartMs', 0)/1000, 'text': text})
        print(f'SUCCESS: {len(segs)} segments')
        if segs:
            print(f'First: {segs[0]["text"][:100]}')
    except json.JSONDecodeError:
        print(f'Not JSON: {body[:300]}')

driver.quit()
