"""Fix published_at for all videos using YouTube Data API / yt-dlp"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import httpx, json

BASE = "https://arypzhotxflimroprmdk.supabase.co/rest/v1/"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
H = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Get all videos
r = httpx.get(BASE + "influencer_videos?select=id,video_id,title,published_at&order=created_at.desc", headers=H)
videos = r.json()

print(f"Total videos: {len(videos)}")
null_dates = [v for v in videos if not v.get('published_at')]
print(f"Missing published_at: {len(null_dates)}")

for v in videos:
    pub = v.get('published_at')
    pub_str = pub[:10] if pub else 'NULL'
    title = (v.get('title') or '')[:40]
    print(f"  {v['video_id']} | {pub_str} | {title}")

# Fetch dates using yt-dlp (no download, just metadata)
import subprocess
import re

def get_upload_date(youtube_id):
    """Get upload date via yt-dlp --print upload_date"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'yt_dlp', '--print', 'upload_date', '--skip-download',
             f'https://www.youtube.com/watch?v={youtube_id}'],
            capture_output=True, text=True, timeout=30
        )
        date_str = result.stdout.strip()
        if re.match(r'^\d{8}$', date_str):
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T00:00:00Z"
    except:
        pass
    return None

print("\n--- Fetching upload dates ---")
updated = 0
failed = 0

for v in null_dates:
    vid = v['video_id']
    print(f"  {vid}... ", end='', flush=True)
    date = get_upload_date(vid)
    if date:
        # Update DB
        r = httpx.patch(
            BASE + f"influencer_videos?id=eq.{v['id']}",
            json={"published_at": date},
            headers=H
        )
        if r.status_code < 300:
            print(f"OK -> {date[:10]}")
            updated += 1
        else:
            print(f"DB ERROR: {r.text[:100]}")
            failed += 1
    else:
        print("FAILED to get date")
        failed += 1

print(f"\nUpdated: {updated}, Failed: {failed}")
