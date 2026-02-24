# 시그널 리뷰 시스템 v4 사용법 (원본 데이터 기반)

## 📋 개요

signal-review-v4는 원본 데이터(`_deduped_signals_8types_dated.json` 177개)를 기준으로 한 완전한 시그널 검증 및 본사이트 동기화 시스템입니다.

## 🚀 주요 기능

### 1. 원본 데이터 기반 변환
- **원본**: `smtr_data/corinpapa1106/_deduped_signals_8types_dated.json` (177개)
- **변환**: TypeScript `CorinpapaSignal` 인터페이스 호환 형식
- **필드 매핑**: asset→stockName, signal_type→signalType, video_id→youtubeLink 등
- **키 변환**: 원본 `video_id_asset` → 변환 `watch?v=video_id_stockName`

### 2. 시그널 검증 리뷰
- Claude Sonnet 추출 시그널 173개 검토 (거부된 4개 제외)
- Opus 검증 결과 확인 (115개 승인)
- 승인/거부/수정 체크박스
- 필터링: 종목별, 시그널타입별, 리뷰상태별
- 영상 날짜 표시, 최신순 정렬

### 3. 본사이트 동기화
- 리뷰 결과를 SMTR 웹사이트에 자동 반영
- 거부된 시그널 삭제 또는 수정
- TypeScript 파일 자동 생성
- 백업 시스템

## 🔧 사용법

### 단계 0: 원본 데이터 동기화 (최초 1회)
```bash
cd C:\Users\Mario\work\invest-sns
node sync_to_site_v2.js
```
- 원본 177개 → 변환된 173개 시그널 (거부된 4개 제외)
- `_matched_reviews_converted.json` 생성
- `corinpapa-signals.ts` 업데이트

### 단계 1: 데이터 임베딩
```bash
node embed_v4.js
```
- 출력: `signal-review-v4-embedded.html` (468KB)
- 173개 시그널 + 변환된 리뷰 상태 + Opus 검증 결과 임베딩

### 단계 2: 리뷰 작업
1. 브라우저에서 `signal-review-v4-embedded.html` 열기
2. 각 시그널 검토:
   - ✅ **승인**: 체크박스 선택
   - ❌ **거부**: 체크박스 선택 → 삭제/수정 선택
   - 🔄 **수정**: 거부 → 수정 선택 → 시그널 타입 변경
3. 필터 활용: 종목명, 시그널타입, 검색어 등
4. 리뷰 완료 후 **"본사이트 동기화"** 버튼 클릭
   - 다운로드: `review-state-YYYY-MM-DD.json`

### 단계 3: 사이트 동기화
```bash
node sync_to_site.js
```

**동작 과정:**
1. 현재 `corinpapa-signals.ts` 로드 (175개)
2. `_matched_reviews.json` + 최신 `review-state-*.json` 병합
3. 리뷰 상태별 처리:
   - `approved`: 시그널 유지
   - `rejected + delete`: 시그널 삭제
   - `rejected + modify`: 시그널 타입 수정
4. 백업 생성: `corinpapa-signals-backup-YYYY-MM-DD.ts`
5. 새 `corinpapa-signals.ts` 저장

### 단계 4: 사이트 빌드
```bash
cd ../smtr-web
npm run build
```

## 📊 예시 결과

**원본 데이터 변환:**
```
📊 원본 데이터 변환 결과:
- 원본 시그널: 177개
- 승인된 시그널: 173개
- 거부된 시그널: 4개
- 최종 시그널: 173개
```

**리뷰 후 동기화:**
```
📊 동기화 결과:
- 승인된 시그널: 171개
- 수정된 시그널: 1개  (캔톤 BUY → HOLD)
- 삭제된 시그널: 1개  (XRP 시그널)
- 거부된 시그널: 0개
- 최종 시그널: 172개
```

## 🔍 파일 구조

```
invest-sns/
├── signal-review-v4.html              # 템플릿
├── signal-review-v4-embedded.html     # 임베딩된 리뷰 페이지 (468KB)
├── embed_v4.js                        # 데이터 임베딩 스크립트
├── sync_to_site.js                    # 본사이트 동기화 스크립트
├── sync_to_site_v2.js                 # 원본 데이터 변환 스크립트 (최초 1회)
├── _matched_reviews.json              # 기본 리뷰 상태
├── _matched_reviews_converted.json    # 변환된 리뷰 상태 (키 형식 변경)
├── _opus_review_results.json          # Opus 검증 결과
├── review-state-*.json                # 브라우저 다운로드 리뷰 상태
├── smtr_data/corinpapa1106/
│   └── _deduped_signals_8types_dated.json  # 원본 데이터 (177개)
└── src/data/
    ├── corinpapa-signals.ts           # 시그널 데이터 (동기화 대상)
    └── corinpapa-signals-backup-*.ts  # 백업 파일
```

## ⚙️ 주요 기능 상세

### 시그널 타입 8가지
- `STRONG_BUY` (적극매수)
- `BUY` (매수)
- `POSITIVE` (긍정)
- `HOLD` (보유)
- `NEUTRAL` (중립)
- `CONCERN` (우려)
- `SELL` (매도)
- `STRONG_SELL` (적극매도)

### 리뷰 액션
- **승인**: 시그널 유지
- **거부 → 삭제**: 시그널 완전 제거
- **거부 → 수정**: 시그널 타입만 변경

### 통계 대시보드
- 총 시그널
- Opus 수정 제안
- 승인됨
- 거부됨
- 검토대기

## 🛡️ 안전장치

1. **백업 시스템**: 동기화 전 자동 백업
2. **로컬스토리지**: 브라우저에 리뷰 상태 저장
3. **디버깅 로그**: 각 시그널 처리 과정 출력
4. **다단계 확인**: 템플릿 → 임베딩 → 리뷰 → 동기화

## 🚨 주의사항

1. **데이터 임베딩 필수**: 리뷰 전에 반드시 `embed_v4.js` 실행
2. **키 형식**: 시그널 키는 `watch?v=VIDEO_ID_STOCK_NAME` 형태
3. **백업 확인**: 동기화 전에 백업 파일 생성 확인
4. **빌드 테스트**: 동기화 후 반드시 `npm run build` 테스트

## 📈 성과

- ✅ **원본 데이터 완전 동기화**: 177개 원본 → 173개 변환 (정확한 필드 매핑)
- ✅ **완전 자동화된 동기화 시스템**: 리뷰 → 변환 → 빌드 → 배포
- ✅ **리뷰 사이트 ↔ 본사이트 실시간 반영**: 삭제/수정 즉시 반영
- ✅ **백업 및 안전장치 완비**: 자동 백업, 다단계 검증
- ✅ **직관적인 UI/UX**: 원본 데이터 기반 정확한 표시

## 🚨 주요 해결사항

1. **원본 데이터 불일치 문제 해결**: 168개 vs 177개 → 177개 원본 기준 통일
2. **종목명 불일치 해결**: 필드 매핑으로 정확한 변환
3. **키 형식 불일치 해결**: 원본 키 → 변환 키 자동 매핑
4. **완전한 동기화**: 리뷰 결과가 본사이트에 100% 반영

---

**개발**: 2026-02-24
**버전**: v4.1 (원본 데이터 기반)
**상태**: 운영 완료 ✅