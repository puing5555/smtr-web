import json, re

with open(r'invest-sns\smtr_data\corinpapa1106\_review_results_backup.json', 'rb') as f:
    raw = f.read()

text = raw[2:].decode('utf-16-le')
text = re.sub(r'[\x00-\x1f]', ' ', text)
# Debug around char 2522
print("Around 2522:", repr(text[2510:2540]))
d = json.loads(text)

print(f"Count: {len(d)}")
approved = sum(1 for v in d.values() if v.get('status') == 'approved')
rejected = sum(1 for v in d.values() if v.get('status') == 'rejected')
pending = sum(1 for v in d.values() if v.get('status') == 'pending')
print(f"Approved: {approved}, Rejected: {rejected}, Pending: {pending}")

for k, v in d.items():
    if v.get('status') == 'rejected':
        reason = v.get('reason', '-')
        print(f"  REJECTED: {k} => {reason}")
