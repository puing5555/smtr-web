# PROJECT_STATUS.md

_Last updated: 2026-02-28 11:10 (GMT+7)_

## 💼 invest-sns 프로젝트 (투자 SNS 플랫폼)

### 🎯 현재 프로젝트 상태
- **폴더**: `invest-sns/`
- **프롬프트**: `prompts/pipeline_v9.md`
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

---

**❌ 절대 참조 금지**: smtr-web, guru_tracker v24, STRONG_BUY, 177개 코린이아빠 시그널 (망한 프로젝트)