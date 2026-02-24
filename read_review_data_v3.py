import json

# Read backup file with proper UTF-16 LE encoding
try:
    with open(r'C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_review_results_backup.json', 'r', encoding='utf-16-le') as f:
        backup_content = f.read()
        backup_data = json.loads(backup_content)
    
    print(f"Backup data type: {type(backup_data)}")
    
    if isinstance(backup_data, dict):
        print(f"Backup data keys count: {len(backup_data)}")
        
        # Count statuses
        approved = 0
        rejected = 0
        pending = 0
        
        for key, value in backup_data.items():
            status = value.get('status', 'pending')
            if status == 'approve':
                approved += 1
            elif status == 'reject':
                rejected += 1
            else:
                pending += 1
        
        print(f"Review status counts:")
        print(f"  Approved: {approved}")
        print(f"  Rejected: {rejected}")
        print(f"  Pending: {pending}")
        
        # Show sample
        first_key = list(backup_data.keys())[0]
        print(f"\nSample backup item: {first_key}")
        print(f"Structure: {backup_data[first_key]}")
        
except Exception as e:
    print(f"Error reading backup: {e}")
    backup_data = {}

# Read Opus data
try:
    with open(r'C:\Users\Mario\work\invest-sns\_opus_review_results.json', 'r', encoding='utf-8') as f:
        opus_data = json.load(f)
    
    print(f"\nOpus data type: {type(opus_data)}")
    print(f"Opus data keys count: {len(opus_data)}")
    
    # Count opus review statuses
    opus_approved = 0
    opus_rejected = 0
    opus_pending = 0
    
    for key, value in opus_data.items():
        verdict = value.get('verdict', 'pending')
        if verdict == 'approve':
            opus_approved += 1
        elif verdict == 'reject':
            opus_rejected += 1
        else:
            opus_pending += 1
    
    print(f"\nOpus review status counts:")
    print(f"  Approved: {opus_approved}")
    print(f"  Rejected: {opus_rejected}")
    print(f"  Pending: {opus_pending}")
    
except Exception as e:
    print(f"Error reading opus: {e}")
    opus_data = {}

# Show data structure for embedding
print("\n" + "="*50)
print("Data ready for embedding:")
print(f"Backup: {len(backup_data) if backup_data else 0} items")
print(f"Opus: {len(opus_data) if opus_data else 0} items")