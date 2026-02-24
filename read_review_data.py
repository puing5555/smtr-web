import json
import sys

# Read review results backup
try:
    with open(r'C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_review_results_backup.json', 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    print(f"Backup data loaded: {len(backup_data)} items")
    print(f"First item structure: {list(backup_data[0].keys()) if backup_data else 'Empty'}")
except Exception as e:
    print(f"Error reading backup: {e}")
    backup_data = {}

# Read Opus review results
try:
    with open(r'C:\Users\Mario\work\invest-sns\_opus_review_results.json', 'r', encoding='utf-8') as f:
        opus_data = json.load(f)
    print(f"Opus data loaded: {len(opus_data)} items")
    print(f"First opus item structure: {list(opus_data[0].keys()) if opus_data else 'Empty'}")
except Exception as e:
    print(f"Error reading opus: {e}")
    opus_data = {}

# Count review statuses in backup
if backup_data:
    approved = [item for item in backup_data if item.get('review_status') == 'approved']
    rejected = [item for item in backup_data if item.get('review_status') == 'rejected']
    pending = [item for item in backup_data if item.get('review_status') == 'pending']
    
    print(f"\nReview status counts:")
    print(f"  Approved: {len(approved)}")
    print(f"  Rejected: {len(rejected)}")
    print(f"  Pending: {len(pending)}")
    
    # Show a sample item
    if backup_data:
        print(f"\nSample backup item:")
        sample = backup_data[0]
        for key, value in sample.items():
            print(f"  {key}: {value}")

if opus_data:
    print(f"\nSample opus item:")
    sample = opus_data[0]
    for key, value in sample.items():
        print(f"  {key}: {value}")