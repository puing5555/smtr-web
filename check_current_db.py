import sqlite3
import os
import json

os.chdir('invest-engine')

try:
    conn = sqlite3.connect('investment.db')
    cursor = conn.cursor()
    
    print('=== DATABASE STATUS ===')
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f'Tables: {[t[0] for t in tables]}')
    
    # Check for signals/influencer data
    if any('signal' in t[0].lower() or 'influencer' in t[0].lower() for t in tables):
        for table_name in [t[0] for t in tables]:
            if 'signal' in table_name.lower() or 'influencer' in table_name.lower():
                try:
                    count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                    print(f'{table_name}: {count} records')
                    
                    if count > 0 and count <= 50:  # Show sample if reasonable size
                        print(f'\n=== {table_name.upper()} SAMPLE ===')
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                        columns = [desc[0] for desc in cursor.description]
                        print(f'Columns: {columns}')
                        
                        for row in cursor.fetchall():
                            print(f'  {dict(zip(columns, row))}')
                except Exception as e:
                    print(f'{table_name}: Error - {e}')
    else:
        print('No signal/influencer tables found')
        
        # Check all tables for any data
        print('\n=== ALL TABLES ===')
        for table_name in [t[0] for t in tables]:
            try:
                count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                print(f'{table_name}: {count} records')
            except:
                print(f'{table_name}: Error')

    conn.close()
    
except Exception as e:
    print(f'Database error: {e}')

# Check if there are any JSON files with signal data
print('\n=== SIGNAL FILES IN WORKSPACE ===')
os.chdir('..')
import glob

signal_files = glob.glob('**/*signal*.json', recursive=True) + glob.glob('**/*corinpapa*.json', recursive=True)
for f in signal_files[:10]:  # Limit to first 10
    try:
        size = os.path.getsize(f)
        print(f'  {f}: {size} bytes')
        if size < 50000:  # If small, peek at content
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if isinstance(data, list):
                    print(f'    Array with {len(data)} items')
                    if data and isinstance(data[0], dict):
                        print(f'    Sample keys: {list(data[0].keys())[:5]}')
    except Exception as e:
        print(f'  {f}: Error - {e}')