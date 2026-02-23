# invest-sns PROJECT STATUS

## 현재 작업: 인플루언서 상세 페이지 SMTR 스타일 업그레이드

### 작업 진행 상황
- [x] 프로젝트 구조 분석 완료
- [x] 현재 인플루언서 상세 페이지 확인
- [x] SMTR 참고 디자인 (guru_tracker_v24.html) 분석
- [x] Zustand store 구조 확인
- [x] Supabase 설정 확인
- [x] 프로필 헤더 업그레이드 (SMTR 스타일 적용)
- [x] 발언 이력 테이블 개선 (깔끔한 테이블 스타일)
- [x] 종목별 필터 탭 추가 (종목명 + 건수 표시)
- [x] 더미 데이터 확장 (SMTR 형식)
- [x] 디자인 적용 (라이트 테마)
- [ ] 레이더 차트 구현 (optional, 추후 추가)
- [ ] Supabase 실제 연동

### 현재 파일 상태
- `src/app/(main)/influencers/[id]/page.tsx` - 기본 구조 있음
- `src/stores/influencers.ts` - 더미 데이터로 작동
- `src/lib/supabase.ts` - 클라이언트 설정 완료
- `.env.local` - 플레이스홀더 값 (실제 연동 필요)

### SMTR 참고 요소
1. **프로필 헤더**: 아바타, 이름, 채널명, 국가, 평균 수익률, 총 발언 수, 주력 종목
2. **레이더 차트**: 6축 (적중률, 다양성, 수익률, 리스크 관리, 활동성, 일관성)
3. **발언 이력 테이블**: 종목별 필터 탭, 테이블 컬럼들
4. **다크 테마를 라이트 테마로 변환**

### 완료된 작업 (2026-02-23)
1. **Zustand Store 데이터 구조 확장**:
   - Influencer 타입에 SMTR 필드 추가 (channelName, country, avgReturn, topStocks, radarStats)
   - Signal 타입에 분석 정보 추가 (returnRate, analysis, videoDate)
   - 더미 데이터를 SMTR 형식으로 풍부하게 확장

2. **인플루언서 상세 페이지 SMTR 스타일 업그레이드**:
   - 그라데이션 프로필 헤더 (아바타, 이름, 채널명, 국가 표시)
   - 핵심 지표 4개 (평균 수익률, 총 발언 수, 적중률, 활동성)
   - 주력 종목 표시 (#1, #2, #3 형식)
   - 시그널 분포 바 및 범례
   - 종목별 필터 탭 (종목명 + 건수 표시)
   - 개선된 테이블 (6개 컬럼: 종목, 신호, 분석, 날짜, 수익률, 영상)
   - 최신순 정렬 적용
   - 라이트 테마 유지하며 SMTR 스타일 적용

### 다음 단계 (우선순위 순)
1. **실제 동작 확인**: 로컬에서 페이지 테스트
2. **레이더 차트 구현** (optional): 6축 레이더 차트 추가
3. **Supabase 실제 연동**: 환경변수 설정 및 데이터 연동
4. **반응형 디자인 개선**: 모바일 최적화

### 시그널 타입 (변경 금지)
STRONG_BUY, BUY, POSITIVE, HOLD, NEUTRAL, CONCERN, SELL, STRONG_SELL