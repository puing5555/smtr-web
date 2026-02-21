import sqlite3

conn = sqlite3.connect('invest_engine.db')
c = conn.cursor()

# List tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", [r[0] for r in c.fetchall()])

# Find CNTN entries
for table in ['signals', 'guru_signals', 'influencer_signals']:
    try:
        c.execute(f"SELECT * FROM {table} WHERE ticker='CNTN' OR symbol='CNTN'")
        rows = c.fetchall()
        if rows:
            print(f"\n{table} with CNTN: {len(rows)} rows")
            for r in rows:
                print(r)
    except Exception as e:
        try:
            c.execute(f"SELECT * FROM {table} WHERE ticker='CNTN'")
            rows = c.fetchall()
            if rows:
                print(f"\n{table} with CNTN: {len(rows)} rows")
                for r in rows:
                    print(r)
        except:
            pass

# Check all tables for CNTN
for table_row in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
    tbl = table_row[0]
    try:
        cols = [r[1] for r in c.execute(f"PRAGMA table_info({tbl})").fetchall()]
        for col in cols:
            try:
                rows = c.execute(f"SELECT * FROM {tbl} WHERE {col} LIKE '%CNTN%'").fetchall()
                if rows:
                    print(f"\nFound CNTN in {tbl}.{col}: {len(rows)} rows")
                    for r in rows[:3]:
                        print(r)
            except:
                pass
    except:
        pass

conn.close()
