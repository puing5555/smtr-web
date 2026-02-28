import re
for v in ['syuka_4QlLhzLfhzU','syuka_g19QLu5tZlo','syuka_wPKfa2qWh4U',
          'hyoseok_fDZnPoK5lyc','hyoseok_ZXuQCpuVCYc','hyoseok_tSXkj2Omz34']:
    with open(f'C:/Users/Mario/work/subs/{v}_fulltext.txt','r',encoding='utf-8') as f:
        text = f.read()
    kws = ['주식','삼성','SK','코스피','매수','매도','투자','종목','ETF','반도체','테슬라','엔비디아','비트코인','코인','하이닉스','네이버','카카오','LG','현대','기아','셀트리온']
    found = []
    for kw in kws:
        cnt = text.count(kw)
        if cnt > 0:
            found.append(f'{kw}:{cnt}')
    print(f'{v}: {found}')
