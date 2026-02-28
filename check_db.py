import sqlite3
import os

os.chdir('invest-engine')

conn = sqlite3.connect('investment.db')
cursor = conn.cursor()

print('=== DB TABLES ===')
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for table in tables:
    print(f'  {table[0]}')

print('\n=== INFLUENCER SIGNALS TABLE ===')
try:
    # Check if influencer_signals table exists and has data
    cursor.execute("SELECT COUNT(*) FROM influencer_signals")
    count = cursor.fetchone()[0]
    print(f'Total signals: {count}')
    
    if count > 0:
        print('\n=== SIGNAL TYPES ===')
        cursor.execute("SELECT signal_type, COUNT(*) FROM influencer_signals GROUP BY signal_type ORDER BY COUNT(*) DESC")
        for signal_type, cnt in cursor.fetchall():
            print(f'  {signal_type}: {cnt}')
            
        print('\n=== RECENT SIGNALS ===')
        cursor.execute("SELECT video_id, asset, signal_type, speaker, created_at FROM influencer_signals ORDER BY created_at DESC LIMIT 10")
        for row in cursor.fetchall():
            print(f'  {row[0][:10]} | {row[1][:15]} | {row[2]} | {row[3][:10]} | {row[4]}')
            
        print('\n=== CHECK V9 COMPLIANCE ===')
        # V9 only allows these 8 signal types
        valid_signals = ['STRONG_BUY', 'BUY', 'POSITIVE', 'HOLD', 'NEUTRAL', 'CONCERN', 'SELL', 'STRONG_SELL']
        
        cursor.execute("SELECT DISTINCT signal_type FROM influencer_signals")
        all_signals = [row[0] for row in cursor.fetchall()]
        
        invalid_signals = [s for s in all_signals if s not in valid_signals]
        if invalid_signals:
            print(f'❌ INVALID SIGNAL TYPES: {invalid_signals}')
            for inv_sig in invalid_signals:
                cursor.execute("SELECT COUNT(*) FROM influencer_signals WHERE signal_type=?", (inv_sig,))
                cnt = cursor.fetchone()[0]
                print(f'  {inv_sig}: {cnt} records')
        else:
            print('✅ All signal types are V9 compliant')
            
except Exception as e:
    print(f'Error accessing influencer_signals: {e}')

print('\n=== OTHER TABLES ===')
for table in tables:
    table_name = table[0]
    if table_name != 'influencer_signals':
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f'  {table_name}: {count} records')
        except Exception as e:
            print(f'  {table_name}: Error - {e}')

conn.close()