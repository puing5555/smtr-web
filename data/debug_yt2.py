import urllib.request, re
url = 'https://www.youtube.com/@3protv'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Cookie': 'CONSENT=YES+1'
})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
print(f"HTML length: {len(html)}")

# Check if ytInitialData exists
if 'ytInitialData' in html:
    print("ytInitialData FOUND")
    m = re.search(r'var ytInitialData = (.+?);</script>', html)
    if m:
        import json
        data = json.loads(m.group(1))
        # Pretty print keys
        print(json.dumps(list(data.keys()), indent=2))
else:
    print("ytInitialData NOT FOUND")
    # Print first 2000 chars to see what we get
    print(html[:2000])
