"""Try youtube-transcript-api with cookies from Chrome"""
import sys, io, json, os, time, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

from youtube_transcript_api import YouTubeTranscriptApi

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

# Try with cookies from Chrome
try:
    from youtube_transcript_api import CookieJar
    print("CookieJar available")
except ImportError:
    print("No CookieJar")

# Check if cookie-based auth works
# youtube-transcript-api v1.x supports cookies_path
try:
    api = YouTubeTranscriptApi(cookie_path='C:/Users/Mario/work/subs/cookies.txt')
    print("Cookie API created")
except Exception as e:
    print(f"Cookie API failed: {e}")
    # Try without cookies but with proxy
    api = YouTubeTranscriptApi()

# Test one video
vid = '1NUkBQ9MQf8'
try:
    t = api.fetch(vid, languages=['ko'])
    print(f"Success: {len(t.snippets)} snippets")
except Exception as e:
    print(f"Failed: {type(e).__name__}: {str(e)[:200]}")
    
    # Try listing transcripts
    try:
        tl = api.list(vid)
        print(f"Transcript list: {tl}")
    except Exception as e2:
        print(f"List also failed: {type(e2).__name__}")
