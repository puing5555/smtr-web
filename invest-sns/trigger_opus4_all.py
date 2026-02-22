"""Trigger Opus 4 analysis for all rejected signals that haven't been analyzed yet"""
import json, sys, time, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

with open('smtr_data/corinpapa1106/_review_results.json', 'r', encoding='utf-8') as f:
    reviews = json.load(f)

with open('smtr_data/corinpapa1106/_opus4_analysis.json', 'r', encoding='utf-8') as f:
    opus = json.load(f)

rejected = {k: v for k, v in reviews.items() if v['status'] == 'rejected'}
pending = [k for k in rejected if k not in opus or opus[k].get('status') != 'complete']

print(f"Total rejected: {len(rejected)}")
print(f"Already analyzed: {len(rejected) - len(pending)}")
print(f"Pending analysis: {len(pending)}")
print()

for i, sig_id in enumerate(pending):
    reason = rejected[sig_id].get('reason', '')
    print(f"[{i+1}/{len(pending)}] Triggering: {sig_id}")
    print(f"  Reason: {reason[:80]}")
    
    data = json.dumps({
        'id': sig_id,
        'status': 'rejected',
        'reason': reason,
        'time': rejected[sig_id].get('time', '')
    }).encode('utf-8')
    
    req = urllib.request.Request(
        'http://localhost:8899/api/review',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read().decode('utf-8'))
        print(f"  -> Triggered OK")
    except Exception as e:
        print(f"  -> Error: {e}")
    
    # Small delay between requests
    time.sleep(1)

print(f"\nAll {len(pending)} analyses triggered! Waiting for completion...")
print("Opus 4 analyzes in background threads. Check back in a few minutes.")
