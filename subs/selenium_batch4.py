"""Selenium v4 - 9개 영상 자막 추출"""
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
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def get_caption_url(driver, vid):
    url = f'https://www.youtube.com/watch?v={vid}'
    driver.get(url)
    time.sleep(5)
    
    page_source = driver.page_source
    
    # Check for 429
    if 'Too Many Requests' in page_source or '429' in driver.title:
        return 'RATE_LIMITED'
    
    caption_match = re.search(r'"captionTracks":\s*(\[.*?\])', page_source)
    if not caption_match:
        return None
    
    tracks = json.loads(caption_match.group(1).replace('\\u0026', '&'))
    ko_track = next((t for t in tracks if t.get('languageCode') == 'ko'), None)
    track = ko_track or (tracks[0] if tracks else None)
    if not track:
        return None
    
    return track.get('baseUrl', ''), track.get('languageCode', '?')

def fetch_via_navigate(driver, caption_url):
    full_url = caption_url + ('&' if '?' in caption_url else '?') + 'fmt=json3'
    driver.get(full_url)
    time.sleep(3)
    
    from selenium.webdriver.common.by import By
    body = driver.find_element(By.TAG_NAME, 'body').text
    
    if not body or len(body) < 50:
        try:
            body = driver.find_element(By.TAG_NAME, 'pre').text
        except:
            pass
    
    if not body or len(body) < 50:
        body = driver.page_source
        match = re.search(r'<pre[^>]*>(.*?)</pre>', body, re.DOTALL)
        if match:
            body = match.group(1)
    
    if not body or len(body) < 50:
        return None
    
    data = json.loads(body)
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
    return segments if segments else None

def save_fulltext(prefix, vid, segments):
    fulltext = '\n'.join(s['text'] for s in segments)
    path = f'{SUBS_DIR}/{prefix}_{vid}_fulltext.txt'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(fulltext)
    return path

def main():
    print("=== Selenium v4: 9개 영상 자막 추출 ===")
    driver = setup_driver()
    print("WebDriver ready\n")
    
    results = []
    batch_count = 0
    
    for i, (prefix, vid) in enumerate(VIDEOS):
        out_path = f'{SUBS_DIR}/{prefix}_{vid}.json'
        
        # Skip if already exists with good data
        if os.path.exists(out_path):
            try:
                d = json.load(open(out_path, 'r', encoding='utf-8'))
                segs = d.get('segments', d.get('subtitles', []))
                if segs and len(segs) > 10:
                    print(f"SKIP {vid} ({prefix}): {len(segs)} segs exist")
                    results.append((vid, prefix, len(segs), 'skipped'))
                    continue
            except:
                pass
        
        print(f"[{i+1}/9] EXTRACT {vid} ({prefix}):")
        batch_count += 1
        
        try:
            info = get_caption_url(driver, vid)
            
            if info == 'RATE_LIMITED':
                print("  429 RATE LIMITED - waiting 1 hour...")
                time.sleep(3600)
                info = get_caption_url(driver, vid)
                if info == 'RATE_LIMITED' or not info:
                    print("  Still rate limited after retry")
                    results.append((vid, prefix, 0, 'rate-limited'))
                    continue
            
            if not info:
                print("  No caption URL found")
                results.append((vid, prefix, 0, 'no-url'))
                time.sleep(3)
                continue
            
            caption_url, lang = info
            print(f"  Caption URL found (lang={lang})")
            
            segments = fetch_via_navigate(driver, caption_url)
            if segments:
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'video_id': vid,
                        'channel': prefix,
                        'subtitles': segments
                    }, f, ensure_ascii=False, indent=2)
                save_fulltext(prefix, vid, segments)
                print(f"  OK: {len(segments)} segments")
                results.append((vid, prefix, len(segments), 'ok'))
            else:
                print(f"  FAIL: fetch returned nothing")
                results.append((vid, prefix, 0, 'fail'))
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append((vid, prefix, 0, 'error'))
        
        # Delay: 3분 랜덤 after every 3rd video
        if batch_count % 3 == 0 and i < len(VIDEOS) - 1:
            delay = random.randint(150, 210)
            print(f"\n  --- Batch pause: {delay}s ---\n")
            time.sleep(delay)
        elif i < len(VIDEOS) - 1:
            delay = random.randint(5, 15)
            time.sleep(delay)
    
    driver.quit()
    
    print("\n=== 결과 ===")
    ok = sum(1 for _,_,_,s in results if s in ('ok', 'skipped'))
    print(f"성공: {ok}/{len(results)}")
    for vid, prefix, count, status in results:
        emoji = '✅' if status in ('ok','skipped') else '❌'
        print(f"  {emoji} {prefix}/{vid}: {status} ({count} segs)")
    
    # Save results
    with open(f'{SUBS_DIR}/batch4_results.json', 'w', encoding='utf-8') as f:
        json.dump([{'vid': v, 'prefix': p, 'count': c, 'status': s} for v,p,c,s in results], f, indent=2)

if __name__ == '__main__':
    main()
