"""
Compress subtitle files by removing duplicates, timestamps noise, and merging lines.
Output: one condensed file per video with key content preserved.
"""
import os, re

SUBS_DIR = 'C:/Users/Mario/work/subs'
OUT_DIR = 'C:/Users/Mario/work/subs_compact'
os.makedirs(OUT_DIR, exist_ok=True)

for fname in os.listdir(SUBS_DIR):
    if not fname.endswith('.txt'):
        continue
    
    vid = fname.replace('.txt', '')
    lines = []
    with open(f'{SUBS_DIR}/{fname}', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Extract timestamp and text
            m = re.match(r'\[(\d{2}:\d{2})\]\s*(.*)', line)
            if m:
                ts, text = m.group(1), m.group(2)
                # Clean up >> markers
                text = re.sub(r'&gt;&gt;\s*', '', text).strip()
                text = re.sub(r'&gt;\s*', '', text).strip()
                if text and len(text) > 1:
                    lines.append((ts, text))
    
    # Merge consecutive lines into paragraphs (every 30 seconds)
    if not lines:
        continue
    
    paragraphs = []
    current_ts = lines[0][0]
    current_texts = []
    
    for ts, text in lines:
        # Parse timestamp
        mins, secs = map(int, ts.split(':'))
        total_secs = mins * 60 + secs
        
        c_mins, c_secs = map(int, current_ts.split(':'))
        c_total = c_mins * 60 + c_secs
        
        if total_secs - c_total > 60 and current_texts:
            # New paragraph
            merged = ' '.join(current_texts)
            paragraphs.append(f'[{current_ts}] {merged}')
            current_ts = ts
            current_texts = [text]
        else:
            current_texts.append(text)
    
    if current_texts:
        merged = ' '.join(current_texts)
        paragraphs.append(f'[{current_ts}] {merged}')
    
    with open(f'{OUT_DIR}/{vid}.txt', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(paragraphs))
    
    orig_size = os.path.getsize(f'{SUBS_DIR}/{fname}')
    new_size = os.path.getsize(f'{OUT_DIR}/{vid}.txt')
    ratio = new_size / orig_size * 100
    print(f'{vid}: {orig_size//1024}KB -> {new_size//1024}KB ({ratio:.0f}%) | {len(paragraphs)} paragraphs')
