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
- **DB:** Supabase (31개 시그널 - 삼프로TV 20 + 코린이아빠 11)
- **프롬프트:** prompts/pipeline_v9.md
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

### 현재 작업 (2026-02-28)
1. 자막 추출된 거 V9 분석 → Supabase INSERT → 사이트 반영
2. 프롬프트 고도화 (V9.1)

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

## 📝 교훈 & 규칙
- 1영상 1종목 1시그널
- 타임스탬프 필수
- Claude Sonnet 추출 → 사람 검증 (별도 검증 단계 없음)
- 중복제거된 데이터만 사용
- 파일명에 반드시 버전 번호
- 기능 하나 완성할 때마다 git commit
