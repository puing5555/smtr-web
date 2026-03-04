import urllib.request, re, json
url = 'https://www.youtube.com/@3protv'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Cookie': 'CONSENT=YES+1'
})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')

m = re.search(r'ytInitialData\s*=\s*(\{.+?\});\s*</script>', html, re.DOTALL)
data = json.loads(m.group(1))
text = json.dumps(data, ensure_ascii=False)

# Search for Korean patterns
for term in ['동영상', '구독자', 'videos', 'subscribers']:
    idx = text.find(term)
    if idx >= 0:
        print(f"'{term}' found:")
        print(text[max(0,idx-50):idx+100])
        print("---")
