import json
import random
from collections import defaultdict, Counter
from datetime import datetime

# 매수 시그널 데이터 로드
with open('buy_signals.json', 'r', encoding='utf-8-sig') as f:
    buy_signals = json.load(f)

print(f"총 매수 시그널: {len(buy_signals)}개")

# speaker_id별 분포 확인
speaker_groups = defaultdict(list)
for signal in buy_signals:
    speaker_groups[signal['speaker_id']].append(signal)

print("\n=== 유튜버별 매수 시그널 분포 ===")
for speaker_id, signals in speaker_groups.items():
    print(f"Speaker {speaker_id}: {len(signals)}개")
    # 첫 번째 시그널의 key_quote로 유튜버 스타일 추정
    if signals:
        print(f"  예시: {signals[0]['stock']} - {signals[0]['key_quote'][:50]}...")

# 종목별 분포
stock_counter = Counter([s['stock'] for s in buy_signals])
print(f"\n=== 종목 다양성 ===")
print(f"총 종목 수: {len(stock_counter)}개")
print("상위 10개 종목:")
for stock, count in stock_counter.most_common(10):
    print(f"  {stock}: {count}개")

# 날짜별 분포
date_counter = Counter([s['created_at'][:10] for s in buy_signals])
print(f"\n=== 날짜 분포 ===")
print(f"총 날짜 수: {len(date_counter)}개")
for date, count in sorted(date_counter.items()):
    print(f"  {date}: {count}개")