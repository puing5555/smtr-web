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

# Check header for channel info
header = data.get('header', {})
print("Header keys:", list(header.keys()))

# Dig into header
for k, v in header.items():
    if isinstance(v, dict):
        print(f"\n{k} keys:", list(v.keys()))
        # Look for video/subscriber info
        vtext = json.dumps(v)
        for term in ['video', 'subscriber', 'Count']:
            idx = vtext.find(term)
            if idx >= 0:
                print(f"  '{term}' at {idx}: {vtext[max(0,idx-30):idx+80]}")
