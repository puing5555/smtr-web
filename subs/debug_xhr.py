"""Debug: see what XHR returns for caption URL"""
import sys, io, json, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

vid = '1NUkBQ9MQf8'
driver.get(f'https://www.youtube.com/watch?v={vid}')
time.sleep(5)

page_source = driver.page_source
caption_match = re.search(r'"captionTracks":\s*(\[.*?\])', page_source)
tracks = json.loads(caption_match.group(1).replace('\\u0026', '&'))
track = next((t for t in tracks if t.get('languageCode') == 'ko'), tracks[0])
caption_url = track['baseUrl'] + '&fmt=json3'

print(f"Caption URL (first 200): {caption_url[:200]}")

# XHR from page context
result = driver.execute_async_script("""
    var callback = arguments[arguments.length - 1];
    var xhr = new XMLHttpRequest();
    xhr.open('GET', arguments[0], true);
    xhr.onload = function() {
        callback({status: xhr.status, length: xhr.responseText.length, first500: xhr.responseText.substring(0, 500)});
    };
    xhr.onerror = function() {
        callback({error: 'XHR_ERROR', status: xhr.status});
    };
    xhr.send();
""", caption_url)

print(f"\nXHR result: {json.dumps(result, indent=2, ensure_ascii=False)[:1000]}")

driver.quit()
