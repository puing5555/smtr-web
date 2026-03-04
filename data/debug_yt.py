import urllib.request, re
url = 'https://www.youtube.com/@3protv'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9'
})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')

# Search for video-related JSON
for pattern in ['video[Cc]ount', 'videosCount', 'videoCount']:
    for m in re.finditer(f'.{{0,20}}{pattern}.{{0,100}}', html):
        print(m.group(0)[:150])
        print("---")

print("\n\nSubscriber patterns:")
for m in re.finditer(r'.{0,20}subscriber.{0,100}', html, re.IGNORECASE):
    print(m.group(0)[:150])
    print("---")
