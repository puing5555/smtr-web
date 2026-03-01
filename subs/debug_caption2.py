"""Debug: use execute_script fetch instead of driver.get for caption URL"""
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
    track = next((t for t in tracks if t.get('languageCode') == 'ko'), tracks[0])
    caption_url = track.get('baseUrl', '')
    full_url = caption_url + '&fmt=json3'
    
    print("Using execute_script fetch...")
    # Use JS fetch from within the YouTube page context
    result = driver.execute_script(f"""
        const resp = await fetch("{full_url}");
        const text = await resp.text();
        return text;
    """)
    
    print(f"Result length: {len(result)}")
    print(f"First 300: {result[:300]}")
    
    if result and len(result) > 50:
        data = json.loads(result)
        events = data.get('events', [])
        segments = []
        for evt in events:
            segs = evt.get('segs', [])
            text = ''.join(s.get('utf8', '') for s in segs).strip()
            if text and text != '\n':
                segments.append({
                    'start': evt.get('tStartMs', 0) / 1000.0,
                    'duration': evt.get('dDurationMs', 0) / 1000.0,
                    'text': text
                })
        print(f"Segments: {len(segments)}")
        if segments:
            print(f"First: {segments[0]}")
            print(f"Last: {segments[-1]}")
else:
    print("No captionTracks")

driver.quit()
