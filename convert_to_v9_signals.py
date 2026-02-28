import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

# V9 기준 시그널 타입 매핑
SIGNAL_MAPPING = {
    'STRONG_BUY': '매수',
    'BUY': '매수', 
    'POSITIVE': '긍정',
    'HOLD': '중립',
    'NEUTRAL': '중립',
    'CONCERN': '경계',
    'SELL': '매도',
    'STRONG_SELL': '매도'
}

# 현재 31개 시그널 읽기
with open('3protv_signals_final.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

print(f"V9 시그널 타입 변환 시작: {len(signals)}개")

# 변환 전 타입별 분포
before_counts = {}
for signal in signals:
    signal_type = signal['signal']
    before_counts[signal_type] = before_counts.get(signal_type, 0) + 1

print("\n변환 전 타입별 분포:")
for signal_type, count in sorted(before_counts.items()):
    korean_type = SIGNAL_MAPPING.get(signal_type, signal_type)
    print(f"  {signal_type} ({korean_type}): {count}개")

# V9 기준으로 변환
converted_signals = []
for signal in signals:
    converted_signal = signal.copy()
    old_type = signal['signal']
    new_type = SIGNAL_MAPPING.get(old_type, old_type)
    converted_signal['signal'] = new_type
    converted_signals.append(converted_signal)

# 변환 후 타입별 분포
after_counts = {}
for signal in converted_signals:
    signal_type = signal['signal']
    after_counts[signal_type] = after_counts.get(signal_type, 0) + 1

print("\n변환 후 V9 타입별 분포:")
for signal_type, count in sorted(after_counts.items()):
    print(f"  {signal_type}: {count}개")

# V9 기준 시그널 저장
with open('3protv_signals_v9.json', 'w', encoding='utf-8') as f:
    json.dump(converted_signals, f, ensure_ascii=False, indent=2)

print(f"\nV9 시그널 저장: 3protv_signals_v9.json ({len(converted_signals)}개)")

# 프론트엔드 데이터에도 복사
import shutil
shutil.copy('3protv_signals_v9.json', 'invest-sns/data/signals_v9.json')
print("프론트엔드 데이터 업데이트: invest-sns/data/signals_v9.json")