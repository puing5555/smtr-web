import json

# Try utf-8-sig for BOM
try:
    with open(r'C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_review_results_backup.json', 'r', encoding='utf-8-sig') as f:
        backup_data = json.load(f)
    
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
        sample = backup_data[first_key]
        print(f"Keys: {list(sample.keys())}")
        
except Exception as e:
    print(f"Error reading backup: {e}")
    backup_data = {}

# Read Opus data  
try:
    with open(r'C:\Users\Mario\work\invest-sns\_opus_review_results.json', 'r', encoding='utf-8') as f:
        opus_data = json.load(f)
    
    print(f"\nOpus data successfully loaded: {len(opus_data)} items")
    
    # Show sample opus item
    first_key = list(opus_data.keys())[0]
    print(f"Sample opus item: {first_key}")
    sample = opus_data[first_key]
    print(f"Keys: {list(sample.keys())}")
    
except Exception as e:
    print(f"Error reading opus: {e}")
    opus_data = {}

print("\n" + "="*50)
print("Ready to embed into HTML")