import json
import re
from collections import defaultdict

# 선택된 시그널 데이터 로드
with open('selected_signals.json', 'r', encoding='utf-8') as f:
    signals = json.load(f)

print(f"검증할 시그널 수: {len(signals)}개")

# 진짜 매수 판단 키워드
real_buy_keywords = ["사라", "매수", "비중 확대", "저가 매수", "적극 매수", "강력 매수"]
positive_mention_keywords = ["좋은 회사", "관심", "지켜볼 만한", "유망한", "괜찮은", "흥미로운"]

def classify_signal(key_quote, video_title=""):
    """시그널을 진짜 매수 vs 단순 긍정으로 분류"""
    text = (key_quote + " " + video_title).lower()
    
    # 진짜 매수 키워드 체크
    for keyword in real_buy_keywords:
        if keyword in text:
            return "진짜 매수", keyword
    
    # 단순 긍정 키워드 체크
    for keyword in positive_mention_keywords:
        if keyword in text:
            return "단순 긍정", keyword
    
    # 기타 매수 관련 표현 체크
    buy_patterns = [
        r"(추천|권유).*드립니다",
        r"사시.*권합니다",
        r"투자.*하세요",
        r"매수.*타이밍",
        r"지금.*사야",
        r"꼭.*사세요"
    ]
    
    for pattern in buy_patterns:
        if re.search(pattern, text):
            return "진짜 매수", f"패턴: {pattern}"
    
    # 애매한 경우는 수동 검토 필요
    return "검토 필요", "키워드 없음"

# 검증 실행
results = []
speaker_accuracy = defaultdict(lambda: {"total": 0, "real_buy": 0})

print("\n=== 시그널 검증 결과 ===")
print("ID | 종목 | 분류 | 근거 | 핵심 발언")
print("-" * 100)

for i, signal in enumerate(signals):
    classification, reason = classify_signal(signal['key_quote'], signal.get('video_title', ''))
    
    result = {
        "id": signal['id'],
        "speaker_id": signal['speaker_id'],
        "stock": signal['stock'],
        "ticker": signal['ticker'],
        "key_quote": signal['key_quote'],
        "classification": classification,
        "reason": reason,
        "confidence": signal['confidence'],
        "timestamp": signal['timestamp']
    }
    results.append(result)
    
    # 유튜버별 통계
    speaker_accuracy[signal['speaker_id']]["total"] += 1
    if classification == "진짜 매수":
        speaker_accuracy[signal['speaker_id']]["real_buy"] += 1
    
    # 출력 (처음 20개만)
    if i < 20:
        quote_short = signal['key_quote'][:50] + "..." if len(signal['key_quote']) > 50 else signal['key_quote']
        print(f"{i+1:2d} | {signal['stock']:8s} | {classification:8s} | {reason:15s} | {quote_short}")

# 통계 계산
total_signals = len(results)
real_buy_count = len([r for r in results if r['classification'] == '진짜 매수'])
positive_mention_count = len([r for r in results if r['classification'] == '단순 긍정'])
need_review_count = len([r for r in results if r['classification'] == '검토 필요'])

print(f"\n=== 전체 정확도 통계 ===")
print(f"총 시그널: {total_signals}개")
print(f"진짜 매수: {real_buy_count}개 ({real_buy_count/total_signals*100:.1f}%)")
print(f"단순 긍정: {positive_mention_count}개 ({positive_mention_count/total_signals*100:.1f}%)")
print(f"검토 필요: {need_review_count}개 ({need_review_count/total_signals*100:.1f}%)")

print(f"\n=== 유튜버별 정확도 ===")
for speaker_id, stats in speaker_accuracy.items():
    if stats["total"] > 0:
        accuracy = stats["real_buy"] / stats["total"] * 100
        print(f"Speaker {speaker_id[:8]}...: {stats['real_buy']}/{stats['total']} ({accuracy:.1f}%)")

# 결과 저장
with open('signal_verification.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n검증 결과를 signal_verification.json에 저장했습니다.")

# 진짜 매수만 필터링해서 저장
real_buy_signals = [r for r in results if r['classification'] == '진짜 매수']
with open('real_buy_signals.json', 'w', encoding='utf-8') as f:
    json.dump(real_buy_signals, f, ensure_ascii=False, indent=2)

print(f"진짜 매수 {len(real_buy_signals)}개를 real_buy_signals.json에 저장했습니다.")