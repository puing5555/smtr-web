# PROJECT_STATUS.md

_Last updated: 2026-02-22 00:51 (GMT+7)_

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

#### 트랙 3: 알림/데이터 수집
- 네이버/미국/코인 뉴스 크롤러 완성
- GPT-4o-mini 한글 번역
- 텔레그램 알림 시스템 (현재 봇 kicked 상태)
- 자동 수집 스케줄러 (APScheduler)

### 🔄 진행중
- 코린이 아빠 검증 배치 결과 대기중 (batch_6999165cf3608190b256076bd3cea0a9)

### ⏳ TODO
- 텔레그램 봇 그룹 재등록
- 인플루언서 추가 등록
- Supabase 로그인 시스템
- Next.js 통합 (현재 HTML 프로토타입)
- UI/UX 개선

### 프로필 요구사항
- **투자성향**: 디폴트 필수 (가치투자자, 모멘텀, 단타, 스윙, 배당, 인덱스, 비트코이너 등)
- **뱃지**: 선택적, 뱃지상 형태 (등록 인플루언서, 비트코이너 등), 획득 방식 미정

### 주요 파일
- `invest-engine/main.py` — 백엔드 메인
- `invest-engine/src/models.py` — DB 모델
- `invest-engine/src/collectors/` — 뉴스 크롤러들
- `invest-sns/test-timeline.html` — 프론트 프로토타입
- `C:\Users\Mario\.openclaw\workspace\guru_tracker_prototype_v24_with_corinpapa.html` — guru_tracker 최신

### 현재 터널 URL (2026-02-21)
- 프론트: https://interpretation-falling-falling-facilitate.trycloudflare.com
- 백엔드: https://permits-lamb-poem-hear.trycloudflare.com
