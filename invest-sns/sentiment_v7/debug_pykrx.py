import sys

f = open(r'C:\Users\Mario\AppData\Roaming\Python\Python314\site-packages\pykrx\stock\stock_api.py', 'r', encoding='utf-8')
content = f.read()
f.close()

# 함수 찾기
idx = content.find('def __get_market_trading_value_and_volume_by_investor')
print(content[idx:idx+1500])

print('\n\n===INVESTOR LINE 850===')
lines = content.split('\n')
for i, line in enumerate(lines[845:870], start=846):
    print(f'{i}: {line}')
