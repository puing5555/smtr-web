import sys
sys.stdout.reconfigure(encoding='utf-8')
html = open(r'C:\Users\Mario\work\invest-sns\signal-review-v3.html', 'r', encoding='utf-8').read()
print(f'Size: {len(html)} bytes')
print(f'Cards: {html.count("signal-card")}')
print(f'undefined: {html.count("undefined")}')
print(f'NaN count: {html.count("NaN")}')
print(f'YouTube links: {html.count("youtube.com/watch")}')
