"""
이효석아카데미 396개 자막 → 시그널 분석
OpenClaw sessions_spawn 대신 직접 Anthropic API 사용 (배치 효율)
"""
import os, json, time, sys, glob, re, random

# Get API key from environment (set by OpenClaw)
api_key = os.environ.get('ANTHROPIC_API_KEY', '')

# Flush stdout for progress visibility
import functools
print = functools.partial(print, flush=True)

if not api_key:
    print("NO_API_KEY: Will output task list for sub-agent processing")
    
# Load prompt
with open('invest-sns/prompts/pipeline_v10.md', 'r', encoding='utf-8') as f:
    prompt = f.read()

# Load filtered video list with stock info
video_stocks = {}
with open('hs_academy_stock_filtered.tsv', 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 2:
            video_stocks[parts[0]] = {'title': parts[1], 'stocks': parts[3] if len(parts) > 3 else ''}

# Get all subtitle files
vtt_files = sorted(glob.glob('subs_hs/*.ko.vtt'))
print(f"Total VTT files: {len(vtt_files)}")

# Load progress
progress_file = 'hs_analysis_progress.json'
if os.path.exists(progress_file):
    with open(progress_file, 'r', encoding='utf-8') as f:
        progress = json.load(f)
else:
    progress = {'done': {}, 'failed': [], 'skipped': [], 'total_signals': 0}

done_set = set(progress['done'].keys())
print(f"Already analyzed: {len(done_set)}")

# Results file
results_file = 'hs_analysis_results.jsonl'

def read_vtt(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Strip VTT tags, timestamps, keep just text
    lines = content.split('\n')
    text_lines = []
    seen = set()
    for line in lines:
        line = line.strip()
        if not line or line == 'WEBVTT' or line.startswith('Kind:') or line.startswith('Language:'):
            continue
        if re.match(r'\d{2}:\d{2}:\d{2}\.\d+ -->', line):
            continue
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', line)
        if clean and clean not in seen:
            seen.add(clean)
            text_lines.append(clean)
    return '\n'.join(text_lines)

def truncate_subtitle(text, max_chars=30000):
    """Truncate subtitle to fit in context window"""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[자막이 너무 길어 일부 생략됨]"

def analyze_with_anthropic(vid_id, title, subtitle_text):
    """Call Anthropic API directly"""
    import urllib.request
    
    user_msg = f"""다음 YouTube 영상의 자막을 분석하여 투자 시그널을 추출해주세요.

영상 제목: {title}
채널: 이효석아카데미

=== 자막 시작 ===
{truncate_subtitle(subtitle_text)}
=== 자막 끝 ===

위 자막에서 투자 시그널을 추출해주세요. 종목에 대한 구체적 언급이 없으면 {{"signals": []}}을 반환하세요."""

    body = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "system": prompt,
        "messages": [{"role": "user", "content": user_msg}]
    }).encode('utf-8')
    
    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=body,
        headers={
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
    )
    
    resp = urllib.request.urlopen(req, timeout=120)
    result = json.loads(resp.read().decode('utf-8'))
    return result['content'][0]['text']

# If no API key, generate task batches for sub-agent
if not api_key:
    # Create batch files with video info for sub-agent processing
    batch = []
    batch_num = 0
    for vtt_file in vtt_files:
        vid_id = os.path.basename(vtt_file).replace('.ko.vtt', '')
        if vid_id in done_set:
            continue
        info = video_stocks.get(vid_id, {'title': vid_id, 'stocks': ''})
        subtitle = read_vtt(vtt_file)
        if len(subtitle) < 100:
            progress['skipped'].append(vid_id)
            continue
        batch.append({
            'vid_id': vid_id,
            'title': info['title'],
            'stocks': info['stocks'],
            'subtitle_length': len(subtitle)
        })
    
    print(f"Videos to analyze: {len(batch)}")
    print(f"Skipped (too short): {len(progress['skipped'])}")
    
    # Save batch info
    with open('hs_analysis_batch.json', 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False)
    
    sys.exit(0)

# Process with API
delay = 1.0  # Start with 1 second delay
min_delay = 0.5
max_delay = 30.0
consecutive_success = 0
count = len(done_set)
total = len(vtt_files)

for vtt_file in vtt_files:
    vid_id = os.path.basename(vtt_file).replace('.ko.vtt', '')
    
    if vid_id in done_set:
        continue
    
    info = video_stocks.get(vid_id, {'title': vid_id, 'stocks': ''})
    subtitle = read_vtt(vtt_file)
    
    if len(subtitle) < 100:
        progress['skipped'].append(vid_id)
        count += 1
        continue
    
    try:
        response_text = analyze_with_anthropic(vid_id, info['title'], subtitle)
        
        # Parse JSON from response
        json_match = re.search(r'\{[\s\S]*"signals"[\s\S]*\}', response_text)
        if json_match:
            result = json.loads(json_match.group())
            signals = result.get('signals', [])
        else:
            signals = []
        
        progress['done'][vid_id] = len(signals)
        progress['total_signals'] += len(signals)
        done_set.add(vid_id)
        count += 1
        
        # Append to results
        with open(results_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'vid_id': vid_id,
                'title': info['title'],
                'signals': signals
            }, ensure_ascii=False) + '\n')
        
        # Adaptive delay
        consecutive_success += 1
        if consecutive_success >= 5:
            delay = max(min_delay, delay * 0.8)
            consecutive_success = 0
        
        if count % 10 == 0:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False)
        
        if count % 50 == 0:
            print(f"\n=== PROGRESS: {count}/{total} | Signals: {progress['total_signals']} | Delay: {delay:.1f}s ===\n")
    
    except Exception as e:
        err = str(e)
        if '429' in err or 'rate' in err.lower():
            consecutive_success = 0
            delay = min(max_delay, delay * 2)
            print(f"  [{count}/{total}] RATE LIMITED, delay→{delay:.1f}s")
            time.sleep(delay * 2)
            # Retry
            progress['failed'].append(vid_id)
        else:
            progress['failed'].append(vid_id)
            count += 1
            print(f"  [{count}/{total}] {vid_id} ERROR: {err[:100]}")
    
    time.sleep(delay + random.uniform(0, 0.5))

# Final save
with open(progress_file, 'w', encoding='utf-8') as f:
    json.dump(progress, f, ensure_ascii=False)

print(f"\n=== DONE ===")
print(f"Analyzed: {len(progress['done'])}")
print(f"Total signals: {progress['total_signals']}")
print(f"Skipped: {len(progress['skipped'])}")
print(f"Failed: {len(progress['failed'])}")
