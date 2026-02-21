import json
import os

print("테스트 시작")

# 파일 경로 확인
signals_file = r"C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_deduped_signals.json"
partial_file = r"C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_claude_partial_60.json"

print(f"시그널 파일 존재: {os.path.exists(signals_file)}")
print(f"부분 결과 파일 존재: {os.path.exists(partial_file)}")

if os.path.exists(signals_file):
    with open(signals_file, 'r', encoding='utf-8') as f:
        all_signals = json.load(f)
    print(f"전체 시그널 수: {len(all_signals)}")

if os.path.exists(partial_file):
    with open(partial_file, 'r', encoding='utf-8') as f:
        partial_results = json.load(f)
    print(f"부분 검증 수: {len(partial_results)}")

print("테스트 완료")