"""Debug: check what caption URL returns"""
import sys, io, json, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

def setup_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

driver = setup_driver()
vid = '1NUkBQ9MQf8'
url = f'https://www.youtube.com/watch?v={vid}'
print(f"Loading {url}")
driver.get(url)
time.sleep(5)

page_source = driver.page_source
caption_match = re.search(r'"captionTracks":\s*(\[.*?\])', page_source)
if caption_match:
    tracks = json.loads(caption_match.group(1).replace('\\u0026', '&'))
    print(f"Tracks: {json.dumps(tracks, indent=2, ensure_ascii=False)[:1000]}")
    
    ko_track = next((t for t in tracks if t.get('languageCode') == 'ko'), None)
    track = ko_track or tracks[0]
    caption_url = track.get('baseUrl', '')
    print(f"\nCaption URL: {caption_url[:200]}")
    
    full_url = caption_url + '&fmt=json3'
    print(f"\nNavigating to caption URL...")
    driver.get(full_url)
    time.sleep(3)
    
    from selenium.webdriver.common.by import By
    body = driver.find_element(By.TAG_NAME, 'body').text
    print(f"\nBody length: {len(body)}")
    print(f"Body first 500 chars: {body[:500]}")
    
    # Also try page_source
    ps = driver.page_source
    print(f"\nPage source length: {len(ps)}")
    print(f"Page source first 500: {ps[:500]}")
else:
    print("No captionTracks found")
    # Check if there's a consent page or something
    print(f"Title: {driver.title}")
    print(f"Page source first 500: {page_source[:500]}")

driver.quit()
