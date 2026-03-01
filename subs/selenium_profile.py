"""Selenium with Chrome user profile to bypass IP block"""
import sys, io, json, os, time, re, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

SUBS_DIR = 'C:/Users/Mario/work/subs'

VIDEOS = [
    ('booread', '1NUkBQ9MQf8'),
    ('booread', 'IjDhjDgC4Ao'),
    ('booread', '1iuRuDfMLUE'),
    ('booread', 'f519DUfXkzQ'),
    ('booread', 'jXME1wXZDRU'),
    ('dalrant', 'DCpdPagMLbQ'),
    ('hyoseok', 'IjYr0FrINis'),
    ('hyoseok', 'Rdw1judfd5E'),
    ('hyoseok', 'Y-7UUKocmC0'),
]

def setup_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    
    options = Options()
    # Use a copy of user's Chrome profile for cookies
    user_data = os.path.expanduser('~') + '/AppData/Local/Google/Chrome/User Data'
    if os.path.exists(user_data):
        # Copy to temp to avoid lock issues
        temp_profile = 'C:/Users/Mario/work/subs/chrome_profile'
        options.add_argument(f'--user-data-dir={temp_profile}')
        print(f"Using temp profile dir")
    
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def extract_subtitles(driver, vid):
    """Extract subtitles using page_source ytInitialPlayerResponse"""
    url = f'https://www.youtube.com/watch?v={vid}'
    driver.get(url)
    time.sleep(5)
    
    page_source = driver.page_source
    
    # Check for blocks
    if 'Too Many Requests' in page_source:
        return 'RATE_LIMITED', None
    
    # Try to get captions from ytInitialPlayerResponse
    caption_match = re.search(r'"captionTracks":\s*(\[.*?\])', page_source)
    if not caption_match:
        return 'NO_CAPTIONS', None
    
    tracks = json.loads(caption_match.group(1).replace('\\u0026', '&'))
    ko_track = next((t for t in tracks if t.get('languageCode') == 'ko'), None)
    track = ko_track or (tracks[0] if tracks else None)
    if not track:
        return 'NO_TRACK', None
    
    caption_url = track.get('baseUrl', '')
    lang = track.get('languageCode', '?')
    print(f"  Caption lang={lang}, ", end='', flush=True)
    
    # Use XMLHttpRequest from within the page to avoid CORS/blocking
    full_url = caption_url + '&fmt=json3'
    
    # Try XMLHttpRequest
    result = driver.execute_async_script("""
        var callback = arguments[arguments.length - 1];
        var xhr = new XMLHttpRequest();
        xhr.open('GET', arguments[0], true);
        xhr.onload = function() {
            callback(xhr.responseText);
        };
        xhr.onerror = function() {
            callback('XHR_ERROR');
        };
        xhr.send();
    """, full_url)
    
    if not result or result == 'XHR_ERROR' or len(result) < 50 or 'Sorry' in result[:200]:
        # Fallback: try fetch
        result = driver.execute_async_script("""
            var callback = arguments[arguments.length - 1];
            fetch(arguments[0])
                .then(r => r.text())
                .then(t => callback(t))
                .catch(e => callback('FETCH_ERROR: ' + e));
        """, full_url)
    
    if not result or len(result) < 50 or 'Sorry' in result[:200] or 'ERROR' in str(result)[:20]:
        # Last resort: navigate
        driver.get(full_url)
        time.sleep(3)
        from selenium.webdriver.common.by import By
        result = driver.find_element(By.TAG_NAME, 'body').text
    
    if not result or len(result) < 50:
        return 'FETCH_FAIL', None
    
    try:
        data = json.loads(result)
    except:
        return 'JSON_FAIL', None
    
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
    
    return 'OK' if segments else 'EMPTY', segments

def main():
    print("=== Selenium Profile: 9개 영상 자막 추출 ===")
    driver = setup_driver()
    print("WebDriver ready\n")
    
    results = []
    
    for i, (prefix, vid) in enumerate(VIDEOS):
        out_path = f'{SUBS_DIR}/{prefix}_{vid}.json'
        ft_path = f'{SUBS_DIR}/{prefix}_{vid}_fulltext.txt'
        
        if os.path.exists(out_path):
            try:
                d = json.load(open(out_path, 'r', encoding='utf-8'))
                segs = d.get('segments', d.get('subtitles', []))
                if segs and len(segs) > 10:
                    print(f"SKIP {vid} ({prefix}): {len(segs)} segs")
                    results.append((vid, prefix, len(segs), 'skipped'))
                    continue
            except:
                pass
        
        print(f"[{i+1}/9] {vid} ({prefix}): ", end='', flush=True)
        
        status, segments = extract_subtitles(driver, vid)
        
        if status == 'RATE_LIMITED':
            print("429 - waiting 1 hour")
            time.sleep(3600)
            status, segments = extract_subtitles(driver, vid)
        
        if status == 'OK' and segments:
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'video_id': vid, 'channel': prefix, 'subtitles': segments}, f, ensure_ascii=False, indent=2)
            fulltext = '\n'.join(s['text'] for s in segments)
            with open(ft_path, 'w', encoding='utf-8') as f:
                f.write(fulltext)
            print(f"OK {len(segments)} segs")
            results.append((vid, prefix, len(segments), 'ok'))
        else:
            print(f"FAIL: {status}")
            results.append((vid, prefix, 0, status.lower()))
        
        if i < len(VIDEOS) - 1:
            if (i + 1) % 3 == 0:
                delay = random.randint(150, 210)
                print(f"  --- Batch pause: {delay}s ---")
            else:
                delay = random.randint(8, 20)
            time.sleep(delay)
    
    driver.quit()
    
    print(f"\n=== 결과 ===")
    ok = sum(1 for _,_,_,s in results if s in ('ok', 'skipped'))
    print(f"성공: {ok}/{len(results)}")
    for vid, prefix, count, status in results:
        emoji = '✅' if status in ('ok','skipped') else '❌'
        print(f"  {emoji} {prefix}/{vid}: {status} ({count} segs)")
    
    with open(f'{SUBS_DIR}/batch4_results.json', 'w', encoding='utf-8') as f:
        json.dump([{'vid': v, 'prefix': p, 'count': c, 'status': s} for v,p,c,s in results], f, indent=2)

if __name__ == '__main__':
    main()
