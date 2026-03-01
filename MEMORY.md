# MEMORY.md - 장기 기억

_Last updated: 2026-02-28 16:14 (GMT+7)_

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
- **프론트엔드:** Next.js (55페이지, GitHub Pages 배포)
- **DB:** Supabase (78개 시그널 - 삼프로TV 20 + 코린이아빠 11 + 부읽남TV 7 + 이효석 9 + 슈카 17 + 달란트 4 + 기타)
- **프롬프트:** prompts/pipeline_v9.md (V9.1 고도화 완료, 규칙 31개)
- **시그널 타입:** 매수/긍정/중립/경계/매도 (한글 5단계만)
- **최신 태그:** v1.3-rollback-fixed

### ⚠️ 절대 금지
- **177개/SMTR/guru_tracker 참조 금지** — 이미 삭제된 레거시 데이터
- STRONG_BUY 8단계 시그널 사용 금지
- GPT-4o-mini 추출 + 별도 검증 파이프라인 사용 금지

### 완료된 작업
- 프로젝트 정리 (smtr-web, guru_tracker, 177개 JSON 삭제)
- 공시 대시보드 v2 출시 (4탭 구조 + 토스 스타일 UI)
- Supabase 테이블 설계 (11개 테이블 + RLS + API 뷰)
- GitHub Pages 배포 완료 (55페이지)
- v1.2-deploy-fix, v1.3-rollback-fixed 태그

### 완료된 추가 작업 (2026-02-28)
- V9.1 고도화 완료 (5회 연속 문제 0개, 규칙 31개: V9 28개 + V9.1 3개)
- 부읽남TV 7시그널 + 이효석 7시그널 추출/INSERT
- 인플루언서 탭: 기간필터→차트연동, SignalDetailModal 모달, 호버 툴팁
- 내 종목 전체탭: limit 50으로 확대, 45개 시그널 전부 표시
- 삼성전자 주가: yfinance 실데이터 확인 (216,500원 = 실제)

### 현재 작업
- ✅ 시그널 99개 (101→99, 바스켓 중복 2건 삭제)
- 서브에이전트 Sonnet 전환 완료 (메인만 Opus)
- 유저 참여 시스템 1단계 100% 완료, 2단계 1→2→3 완료 (AI 자동검토+수정안+승인UI)
- 2단계 4→5 미착수 (AI제안 탭, 프롬프트관리 탭)
- V10.3 프롬프트 완성 (prompts/pipeline_v10.md, 3라운드 자율개선, 7단계 검증)
- 자동화 파이프라인 scripts/ 완성 (6모듈)
- ✅ 종목 페이지 일괄 생성 (5개→28개, Supabase 동적 조회)
- ✅ Edge Function 전환 (corsproxy.io→Supabase Edge Function, API키 입력 불필요)
- ✅ Supabase access token: openclaw-deploy (만료 없음)
- speakers 테이블 "김장년" orphan 레코드 정리 필요

### 완료된 추가 작업 (2026-03-01)
- Selenium 16배속 CC 캡처로 YouTube IP 차단 우회 (마지막 2개 자막 추출)
- 달란트투자 채널/스피커 신규 추가, 4시그널 DB INSERT (총 78개)
- published_at 날짜 수정 (42개 중 38개 업데이트, yt-dlp 사용)
- 프론트엔드 published_at 우선 표시 + 최신순 정렬 + 배포
- 게스트 프로필 이니셜 수정 (호스트만 유튜브 썸네일)
- 코린이아빠 멤버십 영상 11개 + 시그널 11개 삭제 (84→73→74개)
- 리포트 탭 삭제 (애널리스트와 중복)
- 좋아요 하트 중복 버그 수정
- Supabase signal_memos 테이블 + signal_reports AI 컬럼 추가
- 파이프라인 멤버십 제외 규칙 추가

## 🔧 환경 설정
- **OpenClaw 모델:** anthropic/claude-opus-4-6 (2026-02-28 변경)
- **OpenClaw 포트:** 18789
- **채널:** Telegram

## 🧹 세션 자동 정리 (필수)
- 작업 완료 후 불필요한 파일 즉시 삭제 (임시 파일, 로그, 캐시)
- .next/cache/ 폴더는 배포 후 삭제
- 자막 추출 완료 후 원본 자막 파일은 분석 끝나면 삭제, 결과만 DB에 저장
- node_modules 안의 파일 절대 읽지 마라
- out/ 폴더는 배포 후 삭제
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
