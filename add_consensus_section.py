import json
from collections import defaultdict

# 컨센서스 결과 로드
with open('consensus_results.json', 'r', encoding='utf-8') as f:
    consensus_results = json.load(f)

# 각 종목별 상세 데이터 로드
def load_detailed_signals(filename):
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'value' in data:
                return data['value']
            return data if isinstance(data, list) else []
    except:
        return []

samsung_signals = load_detailed_signals('samsung_signals.json')
tesla_signals = load_detailed_signals('tesla_signals.json')
nvidia_signals = load_detailed_signals('nvidia_signals.json')

# 최근 3개월 시그널 필터링
THREE_MONTHS_AGO = "2025-12-05"

def filter_recent(signals):
    return [s for s in signals if s.get('created_at', '')[:10] >= THREE_MONTHS_AGO]

samsung_recent = filter_recent(samsung_signals)
tesla_recent = filter_recent(tesla_signals)
nvidia_recent = filter_recent(nvidia_signals)

# 유튜버별 테이블 생성
def create_youtuber_table(signals, stock_name):
    speaker_data = defaultdict(list)
    
    for signal in signals:
        speaker_id = signal['speaker_id']
        speaker_data[speaker_id].append({
            'signal': signal['signal'],
            'date': signal.get('created_at', '')[:10],
            'quote': signal.get('key_quote', ''),
            'confidence': signal.get('confidence', 'unknown')
        })
    
    # 테이블 생성
    table_lines = []
    table_lines.append("| 유튜버 ID | 시그널 | 날짜 | 신뢰도 | 핵심 발언 |")
    table_lines.append("|----------|---------|------|---------|-----------|")
    
    for speaker_id, speaker_signals in speaker_data.items():
        # 각 유튜버의 최신 시그널만 표시
        latest_signal = sorted(speaker_signals, key=lambda x: x['date'])[-1]
        quote_short = latest_signal['quote'][:60] + "..." if len(latest_signal['quote']) > 60 else latest_signal['quote']
        speaker_short = speaker_id[:12] + "..."
        
        table_lines.append(f"| {speaker_short} | {latest_signal['signal']} | {latest_signal['date']} | {latest_signal['confidence']} | {quote_short} |")
    
    return "\n".join(table_lines)

# 컨센서스 섹션 생성
consensus_section = """
## 📊 유튜버 컨센서스 테스트

**분석 기간:** 2025-12-05 이후 (최근 3개월)  
**분석 종목:** 삼성전자, 테슬라, 엔비디아

### 종목별 컨센서스 현황

| 종목 | 총 시그널 | 참여 유튜버 | 매수 | 긍정 | 중립 | 경계 | 매도 | 컨센서스 |
|------|-----------|-------------|------|------|------|------|------|----------|
"""

# 각 종목별 데이터 추가
for result in consensus_results:
    stock = result['stock_name']
    ticker = result['ticker']
    total = result['total_signals']
    speakers = result['unique_speakers']
    distribution = result['signal_distribution']
    consensus = result['consensus_strength']
    
    buy = distribution.get('매수', 0)
    positive = distribution.get('긍정', 0)
    neutral = distribution.get('중립', 0)
    concern = distribution.get('경계', 0)
    sell = distribution.get('매도', 0)
    
    consensus_section += f"| **{stock}** ({ticker}) | {total}개 | {speakers}명 | {buy} | {positive} | {neutral} | {concern} | {sell} | {consensus} |\n"

# 종목별 상세 테이블 추가
consensus_section += f"""

### 삼성전자(005930) 상세 의견

{create_youtuber_table(samsung_recent, "삼성전자")}

**컨센서스 분석:** 19명 유튜버 중 60%가 긍정적 시각. 매수 의견은 10개로 제한적이지만 전반적으로 긍정적 톤이 우세.

### 테슬라(TSLA) 상세 의견

{create_youtuber_table(tesla_recent, "테슬라")}

**컨센서스 분석:** 16명 유튜버 중 60%가 긍정적. 매수 의견 27개로 상대적으로 적극적 추천이 많음.

### 엔비디아(NVDA) 상세 의견

{create_youtuber_table(nvidia_recent, "엔비디아")}

**컨센서스 분석:** 19명 유튜버 중 61%가 긍정적. 매수 의견 19개로 적극적 투자 의견 존재.

### 🎯 컨센서스 테스트 결론

#### 의미 있는 컨센서스 형성도
- **삼성전자:** 약한 컨센서스 (19명 중 긍정 60%) - 의견 수렴 양호
- **테슬라:** 약한 컨센서스 (16명 중 긍정 60%) - 매수 의견 비교적 많음  
- **엔비디아:** 약한 컨센서스 (19명 중 긍정 61%) - 가장 긍정적 컨센서스

#### 투자 의사결정 활용도
- 모든 종목에서 **60% 이상 긍정적 컨센서스** 형성
- 명확한 매도 의견은 소수 (5-11개)
- 유튜버들 간 **의견 분산은 낮은 편**으로 어느 정도 방향성 일치

#### 한계점
- "중립" 의견이 많아 적극적 추천보다는 관망세 우세
- 유튜버별 영향력/신뢰도 차이 미반영
- 시점별 의견 변화 추적 필요
"""

# 기존 파일 읽기
with open('data/research/signal_accuracy_test.md', 'r', encoding='utf-8') as f:
    existing_content = f.read()

# 새로운 섹션 추가
updated_content = existing_content + consensus_section

# 파일 업데이트
with open('data/research/signal_accuracy_test.md', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("✅ 유튜버 컨센서스 테스트 섹션이 signal_accuracy_test.md에 추가되었습니다.")
print("\n=== 컨센서스 요약 ===")
for result in consensus_results:
    print(f"{result['stock_name']}: {result['consensus_strength']} ({result['unique_speakers']}명 참여)")