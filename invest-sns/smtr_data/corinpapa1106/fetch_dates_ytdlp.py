#!/usr/bin/env python3
import json, subprocess, os

with open('_deduped_signals_8types.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

video_ids = sorted(set(s['video_id'] for s in signals))
print(f"Need dates for {len(video_ids)} videos")

cache_path = '_video_dates.json'
dates = {}
if os.path.exists(cache_path):
    with open(cache_path, 'r', encoding='utf-8') as f:
        dates = json.load(f)
    # Remove empty entries
    dates = {k: v for k, v in dates.items() if v}

todo = [vid for vid in video_ids if vid not in dates]
print(f"Cached: {len(dates)}, Todo: {len(todo)}")

for i, vid in enumerate(todo):
    try:
        result = subprocess.run(
            ['python', '-m', 'yt_dlp', '--print', 'upload_date', 
             f'https://www.youtube.com/watch?v={vid}', '--no-download'],
            capture_output=True, text=True, timeout=15
        )
        date_str = result.stdout.strip()
        if date_str and len(date_str) == 8 and date_str.isdigit():
            formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            dates[vid] = formatted
            print(f"  [{i+1}/{len(todo)}] {vid}: {formatted}")
        else:
            print(f"  [{i+1}/{len(todo)}] {vid}: no date")
    except Exception as e:
        print(f"  [{i+1}/{len(todo)}] {vid}: error {e}")
    
    if (i+1) % 10 == 0:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(dates, f, indent=2)

with open(cache_path, 'w', encoding='utf-8') as f:
    json.dump(dates, f, indent=2)

found = sum(1 for vid in video_ids if dates.get(vid))
print(f"\nDone. Found: {found}/{len(video_ids)}")
