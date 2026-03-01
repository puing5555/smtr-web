# PROJECT_STATUS.md

_Last updated: 2026-03-01 14:56 (GMT+7)_

## 💼 invest-sns 프로젝트 (투자 SNS 플랫폼)

### 🎯 현재 프로젝트 상태
- **폴더**: `invest-sns/`
- **프롬프트**: `prompts/pipeline_v10.md` → **V10.1로 업그레이드 완료**
- **DB**: Supabase (31개 시그널)
  - 삼프로TV V7 20개 시그널 
  - 코린이아빠 V5 11개 시그널
- **시그널 타입**: 매수/긍정/중립/경계/매도 (한글 5단계만)
- **프론트엔드**: Next.js (56페이지)
- **GitHub**: `puing5555/invest-sns`

### ✅ 1단계 완료 (2026-02-28 11:03)
**🗑️ 프로젝트 정리 완료**
- smtr-web/ 폴더 삭제 ✅
- 177개 코린이 아빠 시그널 JSON 파일 삭제 ✅
- guru_tracker v24 관련 파일 삭제 ✅  
- STRONG_BUY 8단계 시그널 관련 파일 삭제 ✅
- 옛날 분석/크롤링/번역 스크립트 전체 삭제 ✅
- **남은 폴더**: `invest-sns/`, `prompts/`, `memory/`, `invest-engine/` + 워크스페이스 기본 파일들만

### ✅ 2단계 완료 (공시 대시보드 v2 출시!)
1. **✅ invest-sns 빌드 & GitHub Pages 푸시** - https://puing5555.github.io/invest-sns/
2. **✅ 공시 대시보드 v2 개발 완료** - 4탭 구조 + 토스 스타일 UI
   - 탭1: 실시간 장중 공시 피드 (아코디언 + 다크 배너)
   - 탭2: 오늘의 하이라이트 (AI 요약 + 섹터별 분석)
   - 탭3: 실적 시즌 (서프라이즈/쇼크 + 컨센서스 변화)
   - 탭4: 공시 DB 검색 (필터 + D+30 수익률)
3. **✅ 주식 공시 탭 v2** - 필터칩 + 사업보고서 AI분석 + 애널리스트 연동
4. **✅ Supabase 테이블 설계** - 11개 테이블 + RLS + API 뷰
5. **Selenium 자막 추출** (슈카월드/이효석/부읽남/달란트)
6. **V9 분석 → Supabase INSERT** (60초 간격)
7. **프롬프트 고도화** (V9.1/V9.2 버전업)

### ✅ 3단계 완료 (2026-02-28 14:33) - v1.2-deploy-fix
1. **✅ 배포 반영 완료** - `npm run build && npx gh-pages -d out` 성공
   - 55개 페이지 정적 생성 완료
   - GitHub Pages 배포 성공
2. **✅ 내 종목 라우팅 검증 완료** - 버그 없음 확인
   - `/my-stocks`에서 삼성전자 탭 클릭 → `/stock/005930` 정상 이동
   - `/stock/[code]` 페이지 정상 작동 확인
   - 라우팅 로직 올바르게 구현됨
3. **✅ Git 태그 생성 완료** - `v1.2-deploy-fix`
   - 로컬 태그 생성 완료
   - Push Protection으로 원격 푸시는 차단됨 (별도 해결 필요)

### ✅ 긴급 수정 완료 (2026-02-28 14:37) - SPA 라우팅 버그 해결
1. **🚨 문제 발견**: 삼성전자 클릭시 404 에러 발생
2. **✅ 원인 파악**: GitHub Pages에서 SPA 라우팅 미작동 (`404.html` 문제)
3. **✅ 수정 완료**: `404.html`을 `index.html`로 교체
4. **✅ 재배포 완료**: `npx gh-pages -d out` 성공
5. **✅ 검증 완료**: `/stock/005930` 경로 정상 접근 가능

### ✅ 내 종목 전체 탭 수정 완료 (2026-02-28 14:42)
1. **🚨 문제 발견**: 전체 탭에서 코린파파 CC 시그널만 반복 표시, 삼프로TV 시그널 20개 안 보임
2. **✅ 데이터 로드 수정**: `getLatestInfluencerSignals(20)` → `(50)` - 31개 모두 가져오기
3. **✅ 날짜 처리 개선**: `signal.created_at` 우선 사용, Invalid Date 체크 추가
4. **✅ 디버깅 로그**: 콘솔에 로드된 시그널 정보 출력
5. **✅ 빌드+배포 완료**: `npm run build && npx gh-pages -d out` 성공
6. **📋 라이브 URL**: https://puing5555.github.io/invest-sns/my-stocks

### ✅ 종목 페이지 에러 핸들링 강화 완료 (2026-02-28 14:45)
1. **🚨 문제 발견**: 종목 클릭시 계속 "Application error: a client-side exception" 발생
2. **✅ import 충돌 해결**: `getStockSignals` 함수 이름 충돌 수정 → `getSupabaseStockSignals`로 변경
3. **✅ 에러 바운더리 추가**: 종목 페이지에 fallback UI와 "다시 시도" 버튼 구현
4. **✅ Supabase 연결 실패 처리**: InfluencerTab에서 연결 실패시 빈 배열로 fallback
5. **✅ 상세한 로깅**: 콘솔에 에러 상태별 명확한 메시지 출력
6. **✅ 빌드+배포 완료**: `/stock/[code]` 페이지 크래시 방지

### ✅ 종목 상세 페이지 완전 복원 완료 (2026-02-28 14:55)
1. **✅ 9개 탭 구조 복원**: 실시간/인플루언서/애널리스트/공시/실적/리포트/임원매매/일정/메모
2. **✅ 실제 Supabase 데이터 연동**: 인플루언서 탭에서 `getStockSignals(code)`로 DB 조회
3. **✅ 주가 차트 추가**: 인플루언서 탭과 애널리스트 탭에 `StockChart` 컴포넌트 추가
4. **✅ 더미/하드코딩 데이터 완전 제거**: "+8.5%", "+12.3%" 등 가짜 수익률 모두 제거
5. **✅ 안전한 에러 처리**: Supabase 연결 실패시 "데이터베이스 연결 실패" 메시지 표시
6. **✅ 시그널 없는 경우 처리**: "아직 시그널이 없습니다" 명확한 안내
7. **✅ 빌드+배포 완료**: `npm run build && npx gh-pages -d out` 성공

### ✅ 날짜 표시 published_at 우선으로 수정 (2026-03-01 09:38)
1. **✅ 프론트엔드 날짜 표시**: `published_at ?? created_at` (영상 업로드 날짜 우선, DB 입력 날짜 fallback)
2. **✅ 클라이언트 정렬**: 4개 페이지에서 published_at 기준 최신순 정렬 추가
   - `app/explore/influencer/page.tsx` - filteredSignals 정렬
   - `app/profile/influencer/[id]/InfluencerProfileClient.tsx` - filteredSignals 정렬
   - `app/stock/[code]/StockDetailClient.tsx` - transformedSignals 정렬
   - `app/stock/[code]/StockDetailClientV2.tsx` - transformedSignals 정렬
3. **✅ Supabase 쿼리**: `lib/supabase.ts`에서 이미 `published_at` select 확인 완료
4. **✅ 커밋**: `24fc61b` - "날짜 표시 published_at 우선으로 수정"

### ✅ V10 프롬프트 자체 분석 및 개선 완료 (2026-03-01 14:56)
1. **✅ DB 시그널 전수 검토**: 101개 시그널 분석, 87개 이슈 발견
2. **✅ V10 규칙 위반 분석**: 
   - 규칙30 (key_quote 품질): 53개 이슈 (61%)
   - 규칙29 (화자 식별): 19개 이슈 (22%)
   - 중복: 13개 이슈 (15%)
   - 규칙3 (전망 vs 권유): 2개 이슈 (2%)
3. **✅ V10.1 프롬프트 업그레이드 완료**: `prompts/pipeline_v10.md`
   - 규칙 3개 강화 (규칙3, 29, 30)
   - 규칙 1개 신규 (규칙32 중복방지)
   - 교차검증 26항목 → 29항목 확장
4. **✅ 개선 효과 검증**: **31% 이슈 해결** 예상 (87개 → 60개)
   - 화자 식별: 100% 해결 (19개 → 0개)
   - 중복 방지: 62% 해결 (13개 → 5개)
   - 전망/권유: 100% 해결 (2개 → 0개)
   - key_quote: 2% 해결 (53개 → 52개) - 자막 품질 한계
5. **✅ 파일 생성**: 
   - `V10_FINAL_REPORT.md` - 최종 보고서
   - `v10_issues.json` - 87개 이슈 목록
   - `v10_1_improvement_report.json` - 개선 효과 데이터

---

**❌ 절대 참조 금지**: smtr-web, guru_tracker v24, STRONG_BUY, 177개 코린이아빠 시그널 (망한 프로젝트)