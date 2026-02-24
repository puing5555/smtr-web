import json
import sys

# Try different encodings for backup file
encodings = ['utf-8', 'utf-16', 'cp949', 'latin1']
backup_data = []

for encoding in encodings:
    try:
        with open(r'C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_review_results_backup.json', 'r', encoding=encoding) as f:
            backup_data = json.load(f)
        print(f"Successfully read backup with {encoding} encoding: {len(backup_data)} items")
        break
    except Exception as e:
        print(f"Failed with {encoding}: {e}")

# Read Opus review results
try:
    with open(r'C:\Users\Mario\work\invest-sns\_opus_review_results.json', 'r', encoding='utf-8') as f:
        opus_data = json.load(f)
    print(f"Opus data loaded: {len(opus_data)} items")
except Exception as e:
    print(f"Error reading opus: {e}")
    opus_data = []

# Count review statuses in backup
if backup_data:
    approved = [item for item in backup_data if item.get('review_status') == 'approved']
    rejected = [item for item in backup_data if item.get('review_status') == 'rejected']
    pending = [item for item in backup_data if item.get('review_status') == 'pending']
    
    print(f"\nReview status counts:")
    print(f"  Approved: {len(approved)}")
    print(f"  Rejected: {len(rejected)}")
    print(f"  Pending: {len(pending)}")
    
    # Show sample keys
    if backup_data:
        print(f"\nSample backup item keys: {list(backup_data[0].keys())}")

if opus_data:
    print(f"\nSample opus item keys: {list(opus_data[0].keys())}")
    
    # Count opus review statuses
    opus_approved = [item for item in opus_data if item.get('opus_review_status') == 'approved']
    opus_rejected = [item for item in opus_data if item.get('opus_review_status') == 'rejected']
    opus_pending = [item for item in opus_data if not item.get('opus_review_status') or item.get('opus_review_status') == 'pending']
    
    print(f"\nOpus review status counts:")
    print(f"  Approved: {len(opus_approved)}")
    print(f"  Rejected: {len(opus_rejected)}")
    print(f"  Pending: {len(opus_pending)}")