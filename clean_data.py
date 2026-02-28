import json

# 1. 현재 42개 시그널에서 차영주 시그널 찾기
with open('3protv_signals.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

print(f"현재 총 {len(signals)}개 시그널")

# 차영주 시그널 찾기
chayoungju_signals = [s for s in signals if '차영주' in s['speaker']]
print(f"\n차영주 시그널: {len(chayoungju_signals)}개")
for i, signal in enumerate(chayoungju_signals, 1):
    print(f"{i}. {signal['stock']} | {signal['signal']} | {signal['mention']}")

# 차영주 제외한 시그널들
filtered_signals = [s for s in signals if '차영주' not in s['speaker']]
print(f"\n차영주 제외 후: {len(filtered_signals)}개 시그널")

# 발언자별 시그널 수
speakers = {}
for signal in filtered_signals:
    speaker = signal['speaker']
    speakers[speaker] = speakers.get(speaker, 0) + 1

print(f"\n발언자별 시그널 수:")
for speaker, count in sorted(speakers.items(), key=lambda x: x[1], reverse=True):
    print(f"  {speaker}: {count}개")

# V7 20개 + 코린이아빠 V5 11개 = 31개 확인
target_count = 31
if len(filtered_signals) == target_count:
    print(f"\n✅ 목표 달성: {target_count}개")
else:
    print(f"\n❌ 목표 미달성: {len(filtered_signals)}개 (목표: {target_count}개)")
    diff = len(filtered_signals) - target_count
    if diff > 0:
        print(f"   {diff}개 더 삭제 필요")
    else:
        print(f"   {abs(diff)}개 부족")

# 정리된 시그널을 새 파일로 저장
with open('3protv_signals_cleaned.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_signals, f, ensure_ascii=False, indent=2)

print(f"\n정리된 데이터 저장: 3protv_signals_cleaned.json ({len(filtered_signals)}개)")