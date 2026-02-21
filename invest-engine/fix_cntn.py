import json, os

base = r"C:\Users\Mario\.openclaw\workspace\smtr_data\corinpapa1106"
files_to_fix = [
    "_extracted_signals.json",
    "_extracted_signals_full.json", 
    "_extracted_signals_partial.json",
    "_simple_extracted_signals.json",
    "_temp_signals.json",
]

for fname in files_to_fix:
    fpath = os.path.join(base, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        raw = f.read()
    
    count = raw.count('"CNTN"')
    if count > 0:
        print(f"{fname}: {count} occurrences of CNTN -> replacing with CC")
        raw = raw.replace('"CNTN"', '"CC"')
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(raw)
    else:
        print(f"{fname}: no CNTN found")

# Also fix DB
import sqlite3
conn = sqlite3.connect(r"C:\Users\Mario\work\invest-engine\invest_engine.db")
c = conn.cursor()

# Check influencer_signals
c.execute("PRAGMA table_info(influencer_signals)")
cols = [r[1] for r in c.fetchall()]
print(f"\ninfluencer_signals columns: {cols}")

for col in cols:
    try:
        c.execute(f"SELECT COUNT(*) FROM influencer_signals WHERE {col} LIKE '%CNTN%'")
        cnt = c.fetchone()[0]
        if cnt > 0:
            print(f"  {col}: {cnt} rows with CNTN")
            c.execute(f"UPDATE influencer_signals SET {col} = REPLACE({col}, 'CNTN', 'CC') WHERE {col} LIKE '%CNTN%'")
            print(f"  Updated {c.rowcount} rows")
    except:
        pass

conn.commit()
conn.close()

# Fix other workspace files
other = [
    r"C:\Users\Mario\.openclaw\workspace\_title_filter_results_complete.json",
    r"C:\Users\Mario\.openclaw\workspace\_title_filter_sample.json",
]
for fpath in other:
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        raw = f.read()
    count = raw.count('"CNTN"')
    if count > 0:
        print(f"\n{os.path.basename(fpath)}: {count} -> CC")
        raw = raw.replace('"CNTN"', '"CC"')
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(raw)

# Also check _all_videos.json and _videos.json
for fname in ["_all_videos.json", "_videos.json"]:
    fpath = os.path.join(base, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        raw = f.read()
    count = raw.count('CNTN')
    if count > 0:
        print(f"\n{fname}: {count} CNTN refs (in video titles, not replacing)")

print("\nDone!")
