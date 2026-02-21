# 신호 검증 리뷰 시스템

## 개요
인플루언서 시그널의 GPT-4o 검증 결과를 사람이 최종 검토하는 웹 인터페이스입니다.

## 파일 위치
- **HTML 페이지**: `C:\Users\Mario\work\invest-sns\signal-review.html`
- **원본 시그널 데이터**: `C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_extracted_signals.json`
- **GPT 검증 결과**: `C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_verify_batch_test_result.jsonl`

## 접속 방법
1. invest-sns 디렉토리에서 http-server 실행 중 (포트 3001)
2. 브라우저에서 접속: `http://localhost:3001/signal-review.html`
3. 또는 터널 주소: `interpretation-falling-falling-facilitate.trycloudflare.com/signal-review.html`

## 주요 기능

### 📊 통계 대시보드
- 총 시그널 수
- 의심 시그널 수 (GPT가 오류 감지한 것들)
- 검토 완료 수
- 승인된 시그널 수

### 🔍 필터링 시스템
- **전체 보기**: 모든 시그널 표시
- **의심만 보기**: GPT가 오류를 발견한 시그널만
- **검토 대기**: 아직 사람이 검토하지 않은 시그널
- **승인됨/거부됨**: 사람의 최종 판단 완료된 시그널
- **인플루언서별**: 특정 인플루언서의 시그널만

### 📝 시그널 정보 표시
각 시그널 카드에는 다음 정보가 표시됩니다:
1. **원본 시그널**:
   - 인플루언서 이름, 비디오 제목, 날짜
   - 종목명, 신호 방향 (BUY/SELL/CONCERN 등)
   - 원본 인용문
   - 추출 분석 내용

2. **GPT-4o 검증 결과**:
   - 종목 정확성: ✅/❌
   - 신호 정확성: ✅/❌
   - 인용문 정확성: ✅/❌
   - 화자 정확성: ✅/❌
   - 제안된 대안 신호 (있는 경우)
   - 오류 설명

### 👨‍💼 인간 검토 인터페이스
각 시그널에 대해 다음 액션을 취할 수 있습니다:
- **✅ 승인**: GPT 검증이 정확하고 시그널이 유효함
- **❌ 거부**: 시그널에 문제가 있어 사용 불가
- **🔄 수정 필요**: 시그널은 유효하지만 수정이 필요함

검토 시 선택적으로 노트를 추가할 수 있습니다.

### 💾 데이터 관리
- **LocalStorage**: 브라우저에 검토 결과 자동 저장
- **결과 내보내기**: JSON 파일로 검토 결과 다운로드
- **데이터 가져오기**: 이전 검토 결과 JSON 파일 업로드

## 데이터 구조

### 원본 시그널 형식
```json
{
  "video_id": "-brWAKvRaqI",
  "stock": "비트마인",
  "signal": "CONCERN",
  "timestamp": "5:39",
  "quote": "비트마인으로 몰려든 서학 개미들이...",
  "detail": "화자는 비트마인에 대한 집단적 투자 열풍이...",
  "speaker": "코린이 아빠",
  "influencer": "코린이 아빠",
  "upload_date": "2026-02-01"
}
```

### GPT 검증 결과 형식
```json
{
  "signal_index": 0,
  "stock_correct": true,
  "signal_correct": true,
  "suggested_signal": "CONCERN",
  "quote_correct": true,
  "speaker_correct": true,
  "error_type": null,
  "explanation": "검증 설명..."
}
```

### 인간 검토 결과 형식
```json
{
  "status": "approved|rejected|modified",
  "notes": "선택적 노트",
  "timestamp": "2026-02-21T09:30:00.000Z",
  "reviewer": "human"
}
```

## API 엔드포인트 (향후 확장용)
invest-engine (포트 8000)에 다음 API가 추가되었습니다:
- `GET /smtr_data/corinpapa1106/_extracted_signals.json`
- `GET /smtr_data/corinpapa1106/_verify_batch_test_result.jsonl`
- `POST /api/signal-reviews` (검토 결과 저장)
- `GET /api/signal-reviews` (검토 결과 조회)

## 사용 workflow
1. 페이지 로드 → 자동으로 시그널과 검증 데이터 로드
2. "의심만 보기" 필터로 GPT가 문제를 발견한 시그널 위주 검토
3. 각 시그널의 원본 내용과 GPT 분석 검토
4. 승인/거부/수정 버튼으로 최종 판단
5. 필요시 노트 추가
6. 주기적으로 "결과 내보내기"로 백업

## 개발자 노트
- UI/UX는 기본적인 수준으로 구현 (기능 우선)
- 현재는 코린이 아빠 데이터만 지원
- 향후 다른 인플루언서 데이터 추가 시 경로만 수정하면 됨
- 검토 결과는 현재 localStorage 사용, 향후 DB 저장으로 확장 가능