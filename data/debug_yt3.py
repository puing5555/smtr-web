import urllib.request, re, json
url = 'https://www.youtube.com/@3protv'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Cookie': 'CONSENT=YES+1'
})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')

# Try different pattern for ytInitialData
m = re.search(r'ytInitialData\s*=\s*(\{.+?\});\s*</script>', html, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    print(f"Keys: {list(data.keys())}")
    # Search recursively for videoCount or videosCount
    text = json.dumps(data)
    for pat in ['videoCount', 'videosCount', 'subscriber']:
        idx = text.find(pat)
        if idx >= 0:
            print(f"\n{pat} found at {idx}:")
            print(text[max(0,idx-20):idx+100])
else:
    print("Pattern not matched")
    # Try to find ytInitialData differently
    starts = [m.start() for m in re.finditer('ytInitialData', html)]
    print(f"ytInitialData positions: {starts}")
