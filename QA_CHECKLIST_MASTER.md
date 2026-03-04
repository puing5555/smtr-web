# QA 체크리스트 마스터 (QA_CHECKLIST_MASTER.md)

> invest-sns 프로젝트 QA 검증의 단일 진실 소스 (Single Source of Truth)
> 최종 업데이트: 2026-03-04
> 기반 문서: QA_PROMPT_MASTER_DOC.md Part 1 + Part 5

---

## 통과 기준

| 통과율 | 판정 | 조치 |
|--------|------|------|
| 95% ↑ | ✅ 통과 | INSERT 진행 |
| 80~95% | ⚠️ 부분수정 | 이슈 항목만 수정 후 재검증 |
| 80% ↓ | 🚫 전체재작업 | 파이프라인부터 재실행 |

---

## 🔴 A섹션: 시그널 데이터 품질 (INSERT 전 필수 게이트)

> **이 섹션은 Supabase INSERT 전 반드시 전량 통과해야 함.**
> Part 5 "QA 상시 검증 작업"의 신규 INSERT 전 필수 검증 항목 포함.

### A1. 비종목 필터링
- [ ] 암호화폐 ticker 없음 (BTC, ETH, XRP, SOL, DOGE, ADA 등)
- [ ] 원자재 ticker 없음 (GLD, SLV, WTI, 금, 은, 구리, 천연가스)
- [ ] 통화 ticker 없음 (달러, 엔, 유로, DXY)
- **위반 시:** 전량 제거

### A2. 비상장기업 필터링
- [ ] 모든 ticker가 실제 상장 종목 (Yahoo Finance 조회 가능)
- [ ] 비상장기업 없음 (스페이스X, 오픈AI, 웨이모, 야놀자, 화웨이 등)
- [ ] 자회사는 상장 모회사로 대체 (삼성파운드리→005930, 삼성디스플레이→005930)
- **위반 시:** 제거 또는 상장 ticker로 대체

### A3. key_quote 품질
- [ ] 길이: 20자 이상 200자 이하
- [ ] 한글 문장 구조 (조사, 어미 포함)
- [ ] 자동자막 오류 패턴 없음 (한글+영어 랜덤 혼합, 의미 없는 단어 나열)
- [ ] 종목명이 key_quote에 포함됨
- **위반 시:** 심각→삭제, 경미→summary 기반 재작성

### A4. signal_date (날짜)
- [ ] signal_date = 영상 업로드 날짜 (오늘 날짜 금지)
- [ ] 미래 날짜 없음
- [ ] 모든 시그널이 동일 날짜가 아님 (배치 INSERT 버그 의심)
- **위반 시:** 영상 업로드 날짜로 수정

### A5. timestamp (타임스탬프)
- [ ] "00:00" 비율 10% 미만
- [ ] 같은 영상의 모든 시그널이 동일 timestamp가 아님
- **위반 시:** subs/ 원본 자막에서 key_quote 기반 재매칭

### A6. 중복 체크
- [ ] (video_id + stock_name) 조합 중복 없음
- [ ] (video_id + ticker) 조합 중복 없음
- [ ] key_quote 내용 유사 중복 없음
- **위반 시:** 중복 제거 (최신 또는 높은 confidence 유지)

### A7. signal_type 유효성
- [ ] 허용값만 사용: `STRONG_BUY`, `BUY`, `POSITIVE`, `HOLD`, `NEUTRAL`, `CONCERN`, `SELL`, `STRONG_SELL`
- [ ] 빈값 없음
- [ ] 위 8종 외 타입 없음 (PRICE_TARGET, MARKET_VIEW 등 금지)
- **위반 시:** 규칙에 맞게 수정

### A8. confidence 범위
- [ ] 모든 값이 0~1 사이
- [ ] 모든 시그널이 동일 confidence가 아님 (의심)
- [ ] 0.5 미만은 시그널 제외
- **위반 시:** 범위 밖 수정, 0.5 미만 제거

---

## 🟡 B섹션: 프론트엔드/사이트 검증

### B1. 종목 페이지 생성
- [ ] DB의 모든 ticker에 대해 /stock/{ticker} 페이지 존재
- [ ] 빌드 로그에서 생성된 stock 페이지 수 확인
- **위반 시:** 누락 종목 페이지 재빌드

### B2. 인플루언서 페이지
- [ ] DB speakers 테이블의 모든 speaker에 대해 /profile/influencer/{slug} 존재
- [ ] SPEAKER_SLUGS 매핑 누락 없음
- **위반 시:** 매핑 추가 + 재빌드

### B3. 모달 UI 일관성
- [ ] 모달에서 마크다운이 텍스트로 노출되지 않음
- [ ] AiDetailRenderer 컴포넌트가 모든 모달에 적용됨
- **위반 시:** 컴포넌트 통일

### B4. 가격 데이터
- [ ] stockPrices.json에 모든 종목 포함
- [ ] 가격 스키마 일관성 (current_price/last_updated 통일)
- [ ] 가격이 0이거나 비정상 값 없음
- **위반 시:** Yahoo Finance 재수집 + 스키마 통일

### B5. HTTP 상태
- [ ] 메인, explore, my-stocks 페이지 200 OK
- [ ] 모든 종목/인플루언서 페이지 200 OK (404 없음)
- **위반 시:** 404 페이지 재빌드

---

## 🟢 C섹션: 애널리스트 리포트 검증

### C1. 애널리스트 이름
- [ ] analyst_name이 한글 2~4글자 이름
- [ ] "-", 빈값, 1글자, 5글자 이상, 의미없는 단어 없음
- **위반 시:** PDF 원본에서 재추출 또는 증권사 기반 추정

### C2. AI 요약 포맷
- [ ] ai_detail에 ## 헤더 5개 섹션 존재 (투자포인트/실적전망/밸류에이션/리스크/결론)
- [ ] 마크다운 렌더링 정상
- [ ] **볼드**, 【괄호】 등 비표준 포맷 없음
- **위반 시:** 텍스트 치환으로 정규화

---

## 검증 결과 리포트 포맷

```
═══════════════════════════════════════
  QA 검증 결과 리포트
  실행일시: {datetime}
═══════════════════════════════════════

📊 총 시그널 수: {total}

🔴 A섹션: 시그널 데이터 품질
  A1 비종목 필터링:    {pass}/{total} ✅/❌
  A2 비상장기업:       {pass}/{total} ✅/❌
  A3 key_quote 품질:   {pass}/{total} ✅/❌
  A4 signal_date:      {pass}/{total} ✅/❌
  A5 timestamp:        {pass}/{total} ✅/❌
  A6 중복 체크:        {pass}/{total} ✅/❌
  A7 signal_type:      {pass}/{total} ✅/❌
  A8 confidence:       {pass}/{total} ✅/❌

  A섹션 통과율: {rate}%

🟡 B섹션: 프론트엔드 (별도 검증)
🟢 C섹션: 애널리스트 (별도 검증)

═══════════════════════════════════════
  최종 판정: ✅통과 / ⚠️부분수정 / 🚫재작업
═══════════════════════════════════════

❌ 오류 목록:
  🔴 [A1] signal_id={id}: ticker=BTC → 암호화폐 제거 필요
  🟡 [A3] signal_id={id}: key_quote 15자 → 20자 미만
  ...
```
