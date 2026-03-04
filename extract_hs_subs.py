import subprocess, sys, time, random, os, json

# Read filtered list
with open('hs_academy_stock_filtered.tsv', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Total to extract: {len(lines)}")

os.makedirs('subs_hs', exist_ok=True)

# Load progress
progress_file = 'hs_sub_progress.json'
if os.path.exists(progress_file):
    with open(progress_file, 'r') as f:
        progress = json.load(f)
else:
    progress = {'done': [], 'failed': [], 'no_sub': []}

done_set = set(progress['done'])
print(f"Already done: {len(done_set)}")

batch_size = 20
total = len(lines)
count = len(done_set)

for i, line in enumerate(lines):
    parts = line.split('\t')
    vid_id = parts[0]
    title = parts[1] if len(parts) > 1 else ''
    
    if vid_id in done_set:
        continue
    
    # Check if subtitle already exists
    vtt_path = f"subs_hs/{vid_id}.ko.vtt"
    if os.path.exists(vtt_path):
        progress['done'].append(vid_id)
        done_set.add(vid_id)
        count += 1
        continue
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--skip-download", 
             "--write-auto-sub", "--sub-lang", "ko", "--sub-format", "vtt",
             "-o", f"subs_hs/{vid_id}", f"https://www.youtube.com/watch?v={vid_id}"],
            capture_output=True, text=True, encoding='utf-8', timeout=30
        )
        
        if os.path.exists(vtt_path):
            progress['done'].append(vid_id)
            done_set.add(vid_id)
            count += 1
        elif 'no subtitles' in result.stderr.lower() or 'no automatic captions' in result.stderr.lower():
            progress['no_sub'].append(vid_id)
            count += 1
            print(f"  [{count}/{total}] {vid_id} - NO SUBTITLE")
        else:
            progress['failed'].append(vid_id)
            count += 1
            print(f"  [{count}/{total}] {vid_id} - FAILED: {result.stderr[:100]}")
    except subprocess.TimeoutExpired:
        progress['failed'].append(vid_id)
        count += 1
        print(f"  [{count}/{total}] {vid_id} - TIMEOUT")
    except Exception as e:
        progress['failed'].append(vid_id)
        count += 1
        print(f"  [{count}/{total}] {vid_id} - ERROR: {e}")
    
    # Progress report every 50
    if count % 50 == 0:
        print(f"\n=== PROGRESS: {count}/{total} | OK: {len(progress['done'])} | NoSub: {len(progress['no_sub'])} | Failed: {len(progress['failed'])} ===\n")
        with open(progress_file, 'w') as f:
            json.dump(progress, f)
    
    # Rate limit: 3 sec delay + random jitter
    delay = 3 + random.uniform(0, 1)
    time.sleep(delay)
    
    # Batch pause: 5 min rest every 20
    if count % batch_size == 0 and count > 0:
        # Save progress
        with open(progress_file, 'w') as f:
            json.dump(progress, f)
        # Only pause on batch boundaries (not too aggressive)
        # 20 videos * 3 sec = ~1 min per batch, take 10 sec break
        print(f"  [Batch {count//batch_size} done, short pause...]")
        time.sleep(10)

# Final save
with open(progress_file, 'w') as f:
    json.dump(progress, f)

print(f"\n=== DONE ===")
print(f"Total: {total}")
print(f"OK: {len(progress['done'])}")
print(f"No subtitle: {len(progress['no_sub'])}")
print(f"Failed: {len(progress['failed'])}")
