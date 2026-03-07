import requests
import pandas as pd
from datetime import datetime

api_key = 'sample'

# sample 키는 max 10건이므로 월별 데이터를 짧은 구간으로 나눠서 가져오기
# 10건씩 → 10개월씩 요청
all_rows = []
# 2015-01 ~ 2026-03 = 135개월 → 14번 요청
periods = [
    ('201501', '201512'),
    ('201601', '201612'),
    ('201701', '201712'),
    ('201801', '201812'),
    ('201901', '201912'),
    ('202001', '202012'),
    ('202101', '202112'),
    ('202201', '202212'),
    ('202301', '202312'),
    ('202401', '202412'),
    ('202501', '202603'),
]

aa_data = {}
bbb_data = {}

for start, end in periods:
    for item_code, storage in [('7020000', aa_data), ('7030000', bbb_data)]:
        url = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/10/721Y001/M/{start}/{end}/{item_code}'
        r = requests.get(url, timeout=10)
        data = r.json()
        if 'StatisticSearch' in data:
            rows = data['StatisticSearch'].get('row', [])
            for row in rows:
                t = row.get('TIME', '')
                v = row.get('DATA_VALUE', '')
                if t and v:
                    storage[t] = float(v)

print(f'AA- 데이터 개수: {len(aa_data)}')
print(f'BBB- 데이터 개수: {len(bbb_data)}')

aa_s = pd.Series(aa_data, dtype=float)
bbb_s = pd.Series(bbb_data, dtype=float)
aa_s.index = pd.to_datetime(aa_s.index, format='%Y%m')
bbb_s.index = pd.to_datetime(bbb_s.index, format='%Y%m')

combined = pd.concat([aa_s.rename('aa'), bbb_s.rename('bbb')], axis=1).dropna()
spread = combined['bbb'] - combined['aa']

print(f'\n스프레드 데이터 (최신 10개):')
print(spread.tail(10))
print(f'\n평균 스프레드: {spread.mean():.3f}%')
print(f'현재 스프레드: {spread.iloc[-1]:.3f}%')
