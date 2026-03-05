# MEMORY.md - 장기 기억

_Last updated: 2026-03-05 06:30 (GMT+7)_

## 👤 유저 정보
- **이름:** Jay Jay (Mario)
- **텔레그램 ID:** 6578282080
- **타임존:** Asia/Bangkok (GMT+7)
- **작업 디렉토리:** C:\Users\Mario\work

## 📌 핵심 프로젝트: 개미는 왜 지는가 (왜지)

### 기본 정보
- **코드 경로:** C:\Users\Mario\work\invest-sns
- **라이브 URL:** https://puing5555.github.io/invest-sns/
- **GitHub:** puing5555/invest-sns
- **프론트엔드:** Next.js (135+ 페이지, GitHub Pages 배포)
- **DB:** Supabase — **804개 시그널** (2026-03-05 확인)
- **Supabase URL:** arypzhotxflimroprmdk.supabase.co (⚠️ 이전 lfymoyaoeq... 사용 금지)
- **프롬프트:** prompts/pipeline_v10.md (V10.10)
- **시그널 타입:** 매수/긍정/중립/경계/매도 (한글 5단계만)
- **시그널 분포:** 매수 491, 매도 168, 중립 87, 경계 48, 긍정 10

### ⚠️ 절대 금지
- **177개/SMTR/guru_tracker 참조 금지** — 이미 삭제된 레거시 데이터
- STRONG_BUY 8단계 시그널 사용 금지
- GPT-4o-mini 추출 + 별도 검증 파이프라인 사용 금지
- **이효석 692개 INSERT 다시 묻지 마라** — 이미 승인+완료됨

### DB 시그널 히스토리
- 155개 → 248개 → 833개 (이효석 692개 INSERT) → **804개** (불량 29개 삭제, 커밋 ecbb4f5)

### 완료된 작업 (~2026-03-03)
- 프로젝트 정리 (smtr-web, guru_tracker, 177개 JSON 삭제)
- 공시 대시보드 v2 출시 (4탭 구조 + 토스 스타일 UI)
- Supabase 테이블 설계 (11개 테이블 + RLS + API 뷰)
- GitHub Pages 배포
- 해외종목 통화표시 (원→$)
- 세상학개론 81개, 달란트투자 4개 시그널 INSERT
- QA 리포트 17항목 점검
- 채널 리서치 1차 50개 + 2차 250개 = 300개 조사, 142개 적합 선별

### 완료된 작업 (2026-03-04)
- **CTO 시스템 v3** — Opus(CTO) + Sonnet(Dev/QA/Patrol) 체계
- **이효석 아카데미 692개** — 원본793→정제692 (QA 98.4%) → **INSERT 완료** → 불량29개 삭제
- **V10.9→V10.10 프롬프트** — A/B 테스트 V10.9 100% 승리, V10.10 적용
- **가격 데이터** — UUID 784개 가비지 제거, 152개 종목 최신가격, 차트 155개
- **수익률 데이터** — signal ID 키로 750개 return_pct 추가
- **공시 스펙 v2** — DART OpenAPI 전환 계획 (disclosure_tech_spec_v2.md)
- **공시 탭 배포** — 시드 20건 + 토스 스타일 UI + SQL
- **올랜도 킴 채널** — 345→189개 영상 필터링, VIDEO_FILTER_RULES.md
- **스피커 slug 매핑** — 70명 전수 커버
- **게스트 스피커 42명** 등록, 242개 시그널 speaker 수정
- **SPA 404 fallback** 추가 (커밋 ab7f929)
- **벤치마킹 리서치** — 16개 해외 사이트 조사 (docs/benchmarking_report.md)
- **채널 우선순위 20개** 선정 (data/channel_priority_top20.md)
  - 1위 김현석 월스트리트나우(95점) ~ 20위 한화투자증권(65점)

### 현재 작업 / 다음 단계
- ai_detail 519건 재생성 (Claude API 스크립트 준비됨, 미실행)
- 공시 DART OpenAPI 연동 (1층 PC cron)
- 채널 확장: 상위 20개 채널 크롤링 시작 필요
- Supabase anon key 변경됨 (.env.local이 최신)

### DB 스키마 (중요)
- 테이블: `influencer_channels`, `influencer_videos`, `influencer_signals`
- videos의 YouTube ID 컬럼: `video_id` (NOT youtube_id)
- 컬럼명: `stock` (NOT stock_name)
- supabase 패키지 깨짐 → REST API 직접 사용

## 🔧 환경 설정
- **OpenClaw 모델:** anthropic/claude-opus-4-6
- **OpenClaw 포트:** 18789
- **채널:** Telegram

## 🧹 세션 자동 정리 (필수)
- 작업 완료 후 불필요한 파일 즉시 삭제
- .next/cache/, out/ 폴더는 배포 후 삭제
- node_modules 안의 파일 절대 읽지 마라
- 워크스페이스에 50MB 이상 파일 생기면 알려줘

## 🚦 자막 추출 레이트리밋 규칙 (필수)
- 요청 간 2-3초 랜덤 딜레이
- 429 뜨면 60초 대기 후 재시도
- 한 번에 20개 이상 연속 추출 금지, 20개 후 5분 휴식

## 📝 교훈 & 규칙
- 1영상 1종목 1시그널
- 타임스탬프 필수
- Claude Sonnet 추출 → 사람 검증 (별도 검증 단계 없음)
- 중복제거된 데이터만 사용
- 파일명에 반드시 버전 번호
- 기능 하나 완성할 때마다 git commit
