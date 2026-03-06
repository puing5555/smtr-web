# HEARTBEAT.md

## Git 자동 백업
- `git status` 체크
- 커밋 안 된 변경사항 있으면 자동 커밋 (`auto-backup: [현재시간]`)

## CTO Watchdog (통합)
- sessions_list로 활성 서브에이전트 확인
- 실행 중인 서브에이전트 진행상황 체크
- 5분 이상 응답 없는 서브에이전트 재시작
- 이상 있으면 그룹(-1003764256213)에 상태 로깅
