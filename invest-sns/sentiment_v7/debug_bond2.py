from sentiment_v7 import get_junk_bond_series_daily, get_junk_bond_series_monthly
import pandas as pd

# daily 시도
print('=== ECOS 일별 정크본드 (2024-01-01~2026-03-07) ===')
s = get_junk_bond_series_daily('2024-01-01', '2026-03-07')
print(f'길이: {len(s)}')
if not s.empty:
    print(s.tail(5))

# monthly 시도
print('\n=== ECOS 월별 정크본드 (202401~202603) ===')
s2 = get_junk_bond_series_monthly('202401', '202603')
print(f'길이: {len(s2)}')
if not s2.empty:
    print(s2)
