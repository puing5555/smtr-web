import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

# 정리된 33개 시그널 분석
with open('3protv_signals_cleaned.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

print(f"현재 {len(signals)}개 시그널 (목표: 31개, 추가 삭제 필요: 2개)")

# 1. 중복 확인 (같은 발언자 + 같은 종목)
duplicates = {}
for signal in signals:
    key = f"{signal['speaker']}-{signal['stock']}"
    if key not in duplicates:
        duplicates[key] = []
    duplicates[key].append(signal)

# 중복된 항목 찾기
print("\n=== 중복 분석 ===")
has_duplicates = False
for key, sigs in duplicates.items():
    if len(sigs) > 1:
        print(f"중복: {key}")
        for i, sig in enumerate(sigs, 1):
            print(f"  {i}. {sig['signal']} | {sig['mention']} | {sig.get('ts', 'N/A')}")
        has_duplicates = True

if not has_duplicates:
    print("중복 없음")

# 2. 가장 약한 시그널 찾기 (삭제 후보)
print("\n=== 삭제 후보 분석 ===")

# 논거 타입 시그널들 (결론보다 약함)
nonmemory_signals = [s for s in signals if s['mention'] == '논거']
print(f"논거 타입 시그널: {len(nonmemory_signals)}개")
for sig in nonmemory_signals:
    print(f"  - {sig['speaker']} | {sig['stock']} | {sig['signal']}")

# 낮은 신뢰도 시그널들
weak_signals = [s for s in signals if s['signal'] in ['NEUTRAL', 'HOLD']]
print(f"\n중립/보유 시그널: {len(weak_signals)}개")
for sig in weak_signals:
    print(f"  - {sig['speaker']} | {sig['stock']} | {sig['signal']} | {sig['mention']}")

# 3. 제거 추천
print("\n=== 제거 추천 ===")
removal_candidates = []

# 논거 중에서 NEUTRAL이나 HOLD 선택
for sig in signals:
    if sig['mention'] == '논거' and sig['signal'] in ['NEUTRAL', 'HOLD']:
        removal_candidates.append(sig)

# 또는 가장 적은 시그널을 가진 발언자의 논거 시그널
speaker_counts = {}
for sig in signals:
    speaker_counts[sig['speaker']] = speaker_counts.get(sig['speaker'], 0) + 1

min_count = min(speaker_counts.values())
rare_speakers = [k for k, v in speaker_counts.items() if v == min_count]

print(f"시그널 1개만 있는 발언자: {rare_speakers}")

# 1개만 있는 발언자의 시그널 중 논거 타입
for sig in signals:
    if sig['speaker'] in rare_speakers and sig['mention'] == '논거':
        removal_candidates.append(sig)

print(f"\n제거 후보 {len(removal_candidates)}개:")
for i, sig in enumerate(removal_candidates, 1):
    print(f"{i}. {sig['speaker']} | {sig['stock']} | {sig['signal']} | {sig['mention']}")

# 2개 선택해서 제거
if len(removal_candidates) >= 2:
    to_remove = removal_candidates[:2]
else:
    # 논거 시그널 중 임의 선택
    to_remove = nonmemory_signals[:2]

print(f"\n최종 제거할 2개:")
for i, sig in enumerate(to_remove, 1):
    print(f"{i}. {sig['speaker']} | {sig['stock']} | {sig['signal']} | {sig['mention']}")

# 제거 후 최종 시그널
final_signals = [s for s in signals if s not in to_remove]

print(f"\n제거 후: {len(final_signals)}개 시그널")

# 저장
with open('3protv_signals_final.json', 'w', encoding='utf-8') as f:
    json.dump(final_signals, f, ensure_ascii=False, indent=2)

print("최종 데이터 저장: 3protv_signals_final.json")