# AGENTS.md - Workspace Rules

## 컨텍스트 관리 (필수)
- 파일은 head -100으로 필요한 부분만 읽어라
- 한번에 파일 3개 이상 동시에 열지 마라
- 컨텍스트 150K 넘으면 새 세션 시작 + MEMORY.md에 상태 저장

## Every Session
1. Read `SOUL.md`, `USER.md`, `memory/YYYY-MM-DD.md` (today+yesterday)
2. Main session only: `MEMORY.md`
3. Read `PROJECT_STATUS.md`

## After Every Task
Update `PROJECT_STATUS.md` with latest state.

## 백업 규칙
- 기능 하나 완성 → `git commit` (한글 메시지)
- 큰 기능 전후 → `git tag v1.x-기능명`
- 커밋 없이 다음 작업 넘어가지 마라

## Memory
- Daily: `memory/YYYY-MM-DD.md` — raw logs
- Long-term: `MEMORY.md` — curated (main session only, security)
- "Mental notes" X → 파일에 기록

## Safety
- Private data 유출 금지
- 외부 발신(이메일/트윗) → 먼저 물어봐
- `trash` > `rm`

## 핵심 운영 규칙
- **확인 후 보고**: 링크/파일 보내기 전 직접 확인. 죽은 링크 금지
- **파일명 버전**: v1, v2... 같은 파일명 2번 금지
- **서브에이전트**: 결과물 직접 확인 후 보고
- **1영상 1종목 1시그널**, 타임스탬프 필수
- **파이프라인**: Claude Sonnet 추출 → 사람 검증 (별도 검증 단계 없음)
- **시그널 한글 5단계**: 매수/긍정/중립/부정/매도
- **중복제거된 데이터만 사용**
- 터널 링크 3번 이상 보내지 마라

## 그룹 채팅
- 질문/가치 있는 정보만 응답. 잡담엔 HEARTBEAT_OK
- 리액션은 메시지당 최대 1개

## Heartbeat
- HEARTBEAT.md 따라 실행 (git 백업 + watchdog)
- 심야(23~08시) → HEARTBEAT_OK (긴급 제외)
