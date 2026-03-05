import json
import random
from collections import defaultdict
from datetime import datetime

# 매수 시그널 데이터 로드
with open('buy_signals.json', 'r', encoding='utf-8-sig') as f:
    buy_signals = json.load(f)

print(f"총 매수 시그널: {len(buy_signals)}개")

# speaker_id별 그룹핑
speaker_groups = defaultdict(list)
for signal in buy_signals:
    speaker_groups[signal['speaker_id']].append(signal)

# 각 유튜버에서 최소 5개씩, 최대한 다양하게 선별
selected_signals = []
random.seed(42)  # 재현 가능한 결과를 위해

# 1단계: 각 유튜버별로 최대 8개씩 선별 (총 50개를 위해 조정)
for speaker_id, signals in speaker_groups.items():
    if len(signals) >= 5:
        # 5개 이상인 유튜버는 최대 8개까지
        max_take = min(8, len(signals))
    else:
        # 5개 미만인 유튜버는 모두 가져오기
        max_take = len(signals)
    
    # 종목과 날짜 다양성을 위해 셔플
    random.shuffle(signals)
    selected = signals[:max_take]
    selected_signals.extend(selected)
    
    print(f"Speaker {speaker_id}: {len(signals)}개 중 {len(selected)}개 선택")

print(f"\n1단계 선택 결과: {len(selected_signals)}개")

# 2단계: 50개로 축소하되 다양성 유지
if len(selected_signals) > 50:
    # 종목별 중복도를 고려하여 선별
    stock_count = defaultdict(int)
    final_signals = []
    
    # 우선 종목별로 1개씩 선택
    used_stocks = set()
    remaining_signals = []
    
    for signal in selected_signals:
        if signal['stock'] not in used_stocks and len(final_signals) < 50:
            final_signals.append(signal)
            used_stocks.add(signal['stock'])
        else:
            remaining_signals.append(signal)
    
    # 나머지 슬롯을 채움
    random.shuffle(remaining_signals)
    while len(final_signals) < 50 and remaining_signals:
        final_signals.append(remaining_signals.pop())
    
    selected_signals = final_signals

print(f"최종 선택: {len(selected_signals)}개")

# 선택된 시그널 정보 요약
print("\n=== 최종 선택 요약 ===")
speaker_final_count = defaultdict(int)
stock_final_count = defaultdict(int)

for signal in selected_signals:
    speaker_final_count[signal['speaker_id']] += 1
    stock_final_count[signal['stock']] += 1

print("유튜버별 분포:")
for speaker_id, count in sorted(speaker_final_count.items(), key=lambda x: x[1], reverse=True):
    print(f"  Speaker {speaker_id}: {count}개")

print("\n종목별 분포 (상위 10개):")
for stock, count in sorted(stock_final_count.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {stock}: {count}개")

# 결과 저장
with open('selected_signals.json', 'w', encoding='utf-8') as f:
    json.dump(selected_signals, f, ensure_ascii=False, indent=2)

print(f"\n선택된 50개 시그널을 selected_signals.json에 저장했습니다.")