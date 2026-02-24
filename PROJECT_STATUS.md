# PROJECT_STATUS.md

_Last updated: 2026-02-23 17:13 (GMT+7)_

## 🏗️ SMTR 프로젝트 (투자자의 세컨드 브레인)

### 서비스 구조
- **invest-engine** (백엔드): FastAPI, SQLite, port 8000
- **invest-sns** (프론트): HTML 프로토타입, port 3001
- **외부 접속**: Cloudflare 터널 (재시작마다 URL 변경)
- **텔레그램 그룹**: 인플루언서주식ai (id: -1003764256213)

### 탭 구조 (5개 - 최종 확정)
1. 🏠 **대시보드** (홈) - 프로필 아이콘(👤) 오른쪽 상단, 포트폴리오/최신글/뉴스/시그널/알림
2. 💬 **SNS** — 투자 피드 (기존 SNS탭 컨텐츠)
3. 📰 **뉴스/공시** — 뉴스 & 공시 피드 (기존 뉴스탭)
4. 📊 **인플루언서** — **v24 guru_tracker 페이지 통째로**
   - v24 디자인 그대로 유지 (색상, 폰트, 카드 스타일)
   - v24 데이터 전부 포함 (SIGNALS_DATA, INFLUENCERS, STOCK_TICKERS 등)
   - v24 서브탭: 차트, 발언, 인플루언서, 종목 그대로
   - 차트(LightweightCharts), 검색, 마커 툴팁, 채팅 버블 모든 기능
5. 📝 **노트** — 투자 노트 (기존 노트탭)

### ✅ 완료

#### 트랙 1: 데이터 공장
- 인플루언서 4명 등록: 박두환, 이효석, 세상학개론, 코린이 아빠
- 코린이 아빠 배치 → v24 프로토타입 (42개 시그널)
- 검증 파이프라인 4단계 설계 + 구현
- 코린이 아빠 28개 비디오 검증 배치 제출 (batch_6999165cf3608190b256076bd3cea0a9, 결과 대기중)
- **🔥 Opus 4 검증 파이프라인 구현 완료** (2026-02-22):
  - review-server.py → port 8901 (Claude Haiku 기반 자동 재검증)
  - 거부(rejected) 시그널 자동 Claude 재분석 (비동기)
  - 자막 전체 재검토 + Sonnet vs 인간 판단 검증
  - 프롬프트 개선 제안 누적 저장
  - 169개 시그널 + 리뷰 데이터 적재 완료
  - Opus 4 분석 UI 표시 (분석중 스피너, 완료시 상세 결과)
- **🚀 리뷰 서버 v5 완성** (2026-02-24):
  - `review-server-v5.py` 신규 생성 (port 8900)
  - v3 HTML UI 스타일 완전 유지 (밝은 테마, 깔끔한 디자인)
  - 헤더에 "🧠 Opus 전체 검토" 버튼 추가
  - 서버 기반 리뷰 데이터 저장 (`_review_results_v5.json`, `_opus_review_results.json`)
  - Opus 검증 기능: Claude Sonnet-3.5로 각 시그널 자막 검증
  - API 엔드포인트: GET /api/signals, /api/reviews, /api/opus-reviews, /api/opus-progress, POST /api/review, /api/opus-review-all
  - 진행률 표시: Opus 검토 진행 상황 프로그레스바
  - 통계 표시: 인간+Opus 승인/거절 수 병행 표시
  - 한국어 UI, 필터링 (시그널타입/검토상태/종목/Opus검토), 최신순 정렬
  - 시그널 데이터: `_deduped_signals_8types_dated.json` 177개 중복제거된 시그널 사용

#### 트랙 2: SNS 웹앱
- 5탭 SPA 완성
- SNS 피드 탭 (스크랩→SNS 자동발행)
- 초세분화 필터 UI (마켓/섹터/공시유형/뉴스카테고리/중요도/기간)
- 종목 검색→태그 멀티셀렉트
- 노트 탭 통합 (메모+스크랩+북마크, 폴더/태그, SNS 연동)
- 인플루언서 시그널 대시보드 통합 (guru_tracker v24)
- **🎉 SMTR 5탭 재구조화 완료** (2026-02-22): 
  - v24 인플루언서 페이지를 독립 탭으로 완전 통합
  - v24 디자인 언어(--bg:#0a0e17) 전체 앱에 적용
  - 프로필을 별도 탭 → 대시보드 우상단 아이콘으로 이동
  - 하단 5탭바, v24 색상 시스템, 모바일 반응형 완료
  - 단일 HTML 파일, v24 JS 데이터/차트/마커 모두 포함
- **🚀 코린이 아빠 검증 시그널 169개 본사이트 통합 완료** (2026-02-22):
  - `_deduped_signals_8types_dated.json` 169개 시그널 → `test-timeline.html` 통합
  - `_review_results.json` 검증 결과 (전부 approved) 확인
  - 인플루언서 메타데이터 stmtCount 29→169 업데이트
  - Python 변환 스크립트 구현 (`integrate_corinpapa_signals.py`)
  - 8가지 시그널 타입 CSS/JS 지원 확인 완료
- **🎯 v24 차트/마커 시스템 본사이트 완전 통합 완료** (2026-02-23):
  - `test-timeline-v25.html` 생성 - v24 모든 차트/마커 기능 통합
  - 마커 CSS (`.marker-tooltip`, `.marker-dot`, `.marker-overlay-container`) 완전 이식
  - 차트 생성 코드 (`createChart`, 캔들스틱 옵션) 통합
  - 마커 dot 시스템 (커스텀 HTML 마커 오버레이) 적용
  - 마커 툴팁 (클릭시 상세 툴팁 - mt-header, mt-avatar, mt-badge, mt-body) 완전 구현
  - 8가지 시그널 타입별 색상 시스템 완벽 적용
  - `showTooltip/closeTooltip` 함수, 검색 기능, 모든 인터랙션 정상 작동
  - v24 데이터 (STOCK_TICKERS, SEARCHABLE_STOCKS, allStatements) 완전 포함
  - 5탭 구조 유지하면서 인플루언서 탭에서 v24 경험 완전 재현
- **🐦 SNS 탭 X(트위터) 스타일 리디자인 완료** (2026-02-23):
  - X 스타일 레이아웃: 좌측 아바타 + 우측 이름/핸들/@/시간 배치
  - 카드 배경 제거, 얇은 border-bottom 구분선으로 깔끔하게
  - X 스타일 액션바: ❤️ 좋아요, 🔄 리트윗, 💬 댓글, 📤 공유 아이콘 + 호버 효과
  - 해시태그 파란색 링크 스타일: #비트코인 #BTC 등
  - "무슨 일이 일어나고 있나요?" 게시 영역 + 둥근 파란 "게시하기" 버튼
  - 시간 표시 X 스타일: "2h", "4h", "6h" 등 짧은 포맷
  - 인플루언서 인증 뱃지: ✓ 파란 체크 (박두환, 세상학개론)
  - X 다크모드 색상: #000000 배경 + #1D9BF0 액센트 + #71767b 보조텍스트
  - 산세리프 폰트 + X 호버 효과 (포스트 호버시 약간 밝아짐)
  - JavaScript 인터랙션: 포스트 작성, 좋아요/리트윗/댓글/공유 기능
- **🎨 SMTR v2 전체 디자인 통합 + 모든 탭 업그레이드 완료** (2026-02-23):
  - **통합 작업**: test-timeline.html(SNS X스타일) + test-timeline-v25.html(v24 차트/마커) → `test-timeline-v2.html`
  - **통일된 디자인 언어**: X 다크모드 #000000 + #1d9bf0 액센트, -apple-system 폰트 스택
  - **🏠 대시보드 탭**: 글래스모피즘 위젯 그리드, 포트폴리오/시그널/마켓 요약, 호버 효과
  - **📰 뉴스/공시 탭**: 뉴스카드 UI, 썸네일+제목+출처+시간, 카테고리 필터 태그
  - **📝 노트 탭**: 노션/Apple Notes 느낌, 사이드바+에디터 레이아웃, 노트 리스트
  - **💬 SNS 탭**: X(트위터) 스타일 완전 유지
  - **👥 인플루언서 탭**: v24 차트/마커/툴팁 시스템 완전 통합
  - **모바일 반응형**: 모든 탭 적응형 레이아웃, 터치 친화적 인터페이스
  - **통일된 하단 탭바**: 부드러운 애니메이션, 일관된 스타일링
- **🏠 SMTR v2 대시보드 개선 + 프로필 패널 구현 완료** (2026-02-23):
  - **대시보드 혁신**: 의미없는 더미 포트폴리오 데이터 (₩125,430,000 등) 완전 제거
  - **유용한 콘텐츠로 대체**:
    1. **🚀 빠른 이동 카드**: 4개 탭으로 바로가는 앱 허브 스타일 큰 카드 (SNS/뉴스/인플루언서/노트)
    2. **🚨 최신 투자 시그널**: 인플루언서 시그널 요약 + "더 많은 시그널 보기" 연결
    3. **📊 실시간 마켓 요약**: BTC/ETH/코스피/나스닥/USD-KRW 5개 마켓 실시간 데이터 (30초 자동 업데이트)
    4. **⏱️ 최근 활동**: 노트 작성, 뉴스 확인, SNS 게시 등 사용자 활동 히스토리
  - **👤 프로필 패널 완전 구현**: 
    - 우상단 👤 아이콘 클릭 → 우측 슬라이드 패널 오픈
    - **사용자 정보**: 프로필 아바타 + 이메일
    - **투자 성향 선택**: 안정형/성장형/공격형/균형형 4개 카드 선택
    - **앱 설정**: 다크모드/푸시알림/소리효과 토글 스위치
    - **기타 옵션**: 도움말, 앱 정보, 로그아웃 버튼
    - **완벽한 X 다크 디자인**: 모던 슬라이드 패널, 오버레이 배경, 부드러운 애니메이션
  - **실시간 마켓 데이터**: 대시보드 탭 활성화 시 자동 시작, 다른 탭 이동 시 중지 (성능 최적화)
  - **파일 출력**: `test-timeline-v2-dashboard-v3.html` (백업: `test-timeline-v2-backup.html`)
- **👥 SMTR v2 인플루언서 탭 서브탭 기능 완성** (2026-02-23):
  - **🎯 3개 준비중 서브탭 완전 구현**:
    1. **💬 발언 탭**: 인플루언서들의 발언 목록 - 날짜/종목/시그널타입/내용 카드 리스트, 시그널타입별 필터링 (전체/적극매수/매수/긍정/우려/매도)
    2. **👥 인플루언서 탭**: 등록된 인플루언서 프로필 카드 - 이름/아바타/총발언수/시그널분포/최근발언, 정확도 표시
    3. **📊 종목 탭**: 종목별 시그널 요약 - 종목명/관련시그널수/최근시그널방향/인플루언서별의견/시그널분포
  - **v24 데이터 구조 완전 이식**: STOCK_TICKERS, INFLUENCERS 객체, parkStatements/hsStatements/corinpapaStatements 배열
  - **8가지 시그널 타입 지원**: STRONG_BUY/BUY/POSITIVE/HOLD/NEUTRAL/CONCERN/SELL/STRONG_SELL + 색상 배지 시스템
  - **X 다크모드 디자인 일관성**: 글래스모피즘 카드, 호버 효과, 모바일 반응형
  - **인터랙티브 기능**: 필터링 버튼, 시그널 배지, 유튜브 링크, 프로필 카드 호버 효과
  - **차트 서브탭 기존 기능 완전 유지**: v24 차트/마커/툴팁 시스템 그대로 보존
- **🚀 SMTR v3 완전체 탄생** (2026-02-23):
  - **v24 guru_tracker를 베이스로 5탭 SPA 완성**: `smtr-v3.html` (8.5MB)
  - **핵심 전략**: v24를 베이스로 하고 나머지 4탭 추가 (기존 방식 대신)
  - **인플루언서 탭**: v24 전체 내용 그대로 보존 (종목뷰/인플루언서/랭킹 서브탭 포함)
  - **v24 CSS/JS 원본 유지**: 차트, 마커, 데이터, 검색, 필터, 툴팁 모든 기능 보존
  - **하단 5탭바**: v24 디자인 언어 (#0a0e17, #f59e0b), 모바일 고정 하단
  - **새로운 4개 탭**:
    - 🏠 대시보드: 빠른이동 카드 + 최신 시그널 + 마켓 요약
    - 💬 SNS: X(트위터) 스타일 피드 (작성/좋아요/리트윗/공유 기능)
    - 📰 뉴스: 뉴스 카드 + 카테고리 필터 (증권/가상화폐/경제/기술/공시)
    - 📝 노트: 노션 스타일 에디터 (사이드바 + 에디터, 검색/저장 기능)
  - **우상단 프로필 아이콘**: 클릭하면 프로필 패널 (설정/프로필/앱정보)

#### 트랙 3: 알림/데이터 수집
- 네이버/미국/코인 뉴스 크롤러 완성
- GPT-4o-mini 한글 번역
- 텔레그램 알림 시스템 (현재 봇 kicked 상태)
- 자동 수집 스케줄러 (APScheduler)

### 🔄 진행중
- 코린이 아빠 검증 배치 결과 대기중 (batch_6999165cf3608190b256076bd3cea0a9)
- **🤖 SMTR 진행상황 자동 보고**: 30분마다 텔레그램 그룹 자동 보고 (크론 작업: 275f92d3-b008-4940-ad05-4f75d93c38b9)

### ⏳ TODO
- 텔레그램 봇 그룹 재등록
- 인플루언서 추가 등록
- Supabase 로그인 시스템
- ~~Next.js 통합 (현재 HTML 프로토타입)~~ ✅ **인플루언서 탭 추가 완료 (2026-02-23)**
- UI/UX 개선

### ✅ 완료 - **🚀 Next.js 인플루언서 탭 추가** (2026-02-23)
- 사이드바에 "인플루언서" 메뉴 추가 (시그널 아래에 배치)
- `/influencers` 라우트 생성 (`src/app/(main)/influencers/page.tsx`)
- 주요 기능 구현:
  - **4개 탭 구조**: 개요/시그널/인플루언서/종목
  - **인플루언서 목록**: 프로필 카드, 검증 뱃지, 시그널 분포 차트
  - **시그널 필터링**: 8가지 시그널 타입별 필터 (STRONG_BUY~STRONG_SELL)
  - **검색 기능**: 인플루언서명, 종목명 통합 검색
  - **통계 대시보드**: 등록 인플루언서/총 시그널/평균 정확도/추적 종목 수
- Zustand 스토어 구조 (`src/stores/influencers.ts`)
- Supabase 연동 준비 (`.env.local`, `src/lib/supabase.ts`)
- 기존 피드 페이지와 일관된 Tailwind + shadcn/ui 디자인
- 더미 데이터로 4명 인플루언서 (박두환, 이효석, 세상학개론, 코린이 아빠)
- 8가지 시그널 타입 색상 배지 시스템
- Next.js 16 + Tailwind v4 호환성 확인 완료

### ✅ 완료 - **🌐 Next.js 앱 GitHub Pages 정적 배포** (2026-02-23)
- **동적 라우트 문제 해결**: `/stocks/[symbol]`, `/influencers/[id]` 동적 라우트에 `generateStaticParams()` 함수 추가
- **서버/클라이언트 컴포넌트 분리**: 각 동적 라우트를 서버 컴포넌트(page.tsx) + 클라이언트 컴포넌트(별도 파일)로 구조 개선
- **정적 빌드 성공**: `npm run build` 성공, `out` 폴더 생성 (171개 파일)
- **배포 완료**: 
  - 빌드 결과물 → `C:\Users\Mario\work\smtr-web` 복사 완료
  - 기존 중요 파일 보존: `guru_tracker_v24.html`, `signal-review-v3.html`, `smtr-v3.html`
  - Git 커밋 및 푸시: https://github.com/puing5555/smtr-web
- **라이브 사이트**: https://puing5555.github.io/smtr-web/ 
- **생성된 정적 페이지**:
  - 홈 및 기본 페이지들: `/`, `/feed`, `/influencers`, `/news`
  - 동적 인플루언서 페이지: `/influencers/corinpapa1106`, `/influencers/1`, `/influencers/2`, `/influencers/3`
  - 동적 종목 페이지: `/stocks/BTC`, `/stocks/ETH`, `/stocks/SOL`, `/stocks/ADA`, `/stocks/DOT`
- **Next.js 16 + GitHub Pages 정적 내보내기 성공**

### ✅ 완료 - **🖼️ 플레이스홀더 아바타 및 차트 이미지 생성** (2026-02-23)
- **아바타 이미지 9개 생성**: UI Avatars API 사용
  - `avatars/me.jpg` - 기본 유저 아바타
  - `avatars/doohwan.jpg` - 박두환 (투자 전문가, 파란색)
  - `avatars/hyoseok.jpg` - 이효석 (반도체 분석가, 초록색)
  - `avatars/korini.jpg` - 코린이 아빠 (친근한 투자자, 주황색)
  - `avatars/whale.jpg` - CryptoWhale (익명 고래, 검정색)
  - `avatars/stock-king.jpg` - 주식왕 (프로 트레이더, 빨간색)
  - `avatars/writer-kim.jpg` - 김작가 (작가/분석가, 보라색)
  - `avatars/realestate.jpg` - 부동산왕 (부동산 전문가, 주황색)
  - `avatars/quant.jpg` - 퀀트투자 (데이터/수학, 청록색)
- **차트 이미지 생성**: 
  - `charts/bitcoin-chart.jpg` - 비트코인 차트 (SVG 기반)
  - 색상: Bitcoin Orange (#f7931a), 검은 배경, 그리드, 가격 라벨 포함
- **PowerShell 다운로드**: `Invoke-WebRequest`로 UI Avatars API에서 직접 다운로드
- **Git 커밋**: "프로필 아바타 및 차트 이미지 추가" (11개 파일 추가)

### ✅ 완료 - **🔧 GitHub Pages basePath 이미지 경로 수정** (2026-02-23)
- **문제점**: GitHub Pages에서 basePath가 "/smtr-web"인데 피드 페이지 이미지 경로가 "/avatars/doohwan.jpg" 등으로 하드코딩돼서 실제로는 "/smtr-web/avatars/doohwan.jpg"로 가야하는데 루트 "/avatars/" 찾고 있었음
- **해결책**: `getImagePath` 헬퍼 함수 구현 - `process.env.NEXT_PUBLIC_BASE_PATH || ''`를 이미지 경로에 prefix로 추가
- **수정 파일**: `src/app/(main)/feed/page.tsx` 
  - 모든 하드코딩된 이미지 경로 (`/avatars/xxx.jpg`, `/charts/xxx.jpg` 등) → `getImagePath()` 함수로 감싸기
  - dummyPosts, suggestedFollows, 컴포넌트 내 fallback 이미지 경로 모두 수정
- **환경변수 설정**: `.env.local`에 `NEXT_PUBLIC_BASE_PATH=/smtr-web` 추가
- **빌드 및 배포**: 
  - `npm run build` 성공
  - `out` 폴더 → `smtr-web` 레포에 복사 (기존 avatars/, charts/, HTML 파일들 보존)
  - git commit "이미지 경로 basePath 수정" + push 완료
- **결과**: GitHub Pages에서 이미지들이 올바른 경로로 로드됨

### 프로필 요구사항
- **투자성향**: 디폴트 필수 (가치투자자, 모멘텀, 단타, 스윙, 배당, 인덱스, 비트코이너 등)
- **뱃지**: 선택적, 뱃지상 형태 (등록 인플루언서, 비트코이너 등), 획득 방식 미정

### 주요 파일
- `invest-engine/main.py` — 백엔드 메인
- `invest-engine/src/models.py` — DB 모델
- `invest-engine/src/collectors/` — 뉴스 크롤러들
- `invest-sns/smtr-v3.html` — **🚀 SMTR v3 완전체 (8.5MB)** - v24 베이스 5탭 SPA
- `invest-sns/test-timeline-v2-dashboard-v3.html` — 인플루언서 서브탭 완성 버전
- `invest-sns/test-timeline-v2.html` — v2 통합 프론트 (SNS+v24차트+전체 탭 업그레이드)
- `invest-sns/test-timeline.html` — SNS X 스타일 버전
- `invest-sns/test-timeline-v25.html` — v24 차트 통합 버전
- `invest-sns/guru_tracker_v24.html` — v24 원본 (8MB, 모든 기능)
- `C:\Users\Mario\.openclaw\workspace\guru_tracker_prototype_v24_with_corinpapa.html` — guru_tracker 최신

### 현재 터널 URL (2026-02-22)
- **Opus 4 리뷰서버**: https://bright-corners-bow.loca.lt (port 8901)
- 프론트: https://interpretation-falling-falling-facilitate.trycloudflare.com  
- 백엔드: https://permits-lamb-poem-hear.trycloudflare.com
