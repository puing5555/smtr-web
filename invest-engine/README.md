# Investment Engine

투자 플랫폼용 알림/데이터 수집 시스템

## 🎯 프로젝트 목적

투자 관련 데이터를 자동 수집하고 텔레그램을 통해 알림을 보내는 백엔드 엔진입니다.  
MVP는 텔레그램 봇으로 동작하며, 향후 SNS 웹앱과 API로 연결됩니다.

## 🛠 기술 스택

- **Backend**: Python 3.8+ (FastAPI)
- **Scheduler**: APScheduler  
- **Database**: SQLite (MVP) → PostgreSQL (확장)
- **Messaging**: python-telegram-bot
- **Data Collection**: DART API, Web Scraping
- **Deployment**: Uvicorn

## 📁 프로젝트 구조

```
invest-engine/
├── src/
│   ├── collectors/          # 데이터 수집
│   │   ├── dart.py         # DART 공시 수집
│   │   ├── price.py        # 주가/급등락 감지
│   │   ├── news.py         # 뉴스 크롤링 (예정)
│   │   ├── influencer.py   # 유튜버 영상 감지 (예정) 
│   │   └── buzz.py         # 쏠림 데이터 (예정)
│   ├── analyzers/          # AI 분석 (예정)
│   │   ├── news_scorer.py  # 뉴스 등급 분류
│   │   └── signal_extract.py # 시그널 추출
│   ├── alerts/             # 알림 발송
│   │   ├── telegram_bot.py # 텔레그램 봇
│   │   └── briefing.py     # 브리핑/요약 생성
│   ├── scheduler/          # 스케줄러
│   │   └── job_scheduler.py # 작업 스케줄링
│   ├── db/                 # 데이터베이스
│   │   ├── models.py       # DB 모델
│   │   └── database.py     # DB 연결
│   ├── config/             # 설정
│   │   └── settings.py     # 앱 설정
│   └── api/                # API 엔드포인트 (예정)
├── main.py                 # FastAPI 메인 앱
├── requirements.txt        # 의존성
├── .env.example           # 환경변수 예시
└── README.md              # 이 파일
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 클론/다운로드 후
cd invest-engine

# 가상환경 생성 (권장)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac  
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 수정 (필수)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
DART_API_KEY=your_dart_api_key_here  # 선택사항
```

### 3. 텔레그램 봇 설정

1. [@BotFather](https://t.me/botfather)와 채팅 시작
2. `/newbot` 명령으로 새 봇 생성
3. 봇 토큰을 `.env`의 `TELEGRAM_BOT_TOKEN`에 설정
4. 봇과 채팅 시작 후 채팅 ID 확인하여 `TELEGRAM_CHAT_ID`에 설정

### 4. 실행

```bash
# 개발 서버 실행
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면:
- API: http://localhost:8000
- 문서: http://localhost:8000/docs
- 스케줄러 자동 시작

## 📋 주요 기능

### ✅ 구현 완료 (MVP)

1. **DART 공시 수집**
   - 평일 매시 정각 자동 수집
   - 중요 공시 즉시 텔레그램 알림
   - API: `/trigger/dart-collection`

2. **아침 브리핑**
   - 평일 08:30 자동 전송
   - 어제 주요 공시 요약
   - 급등락 종목 정리
   - API: `/trigger/morning-briefing`

3. **마감 요약**
   - 평일 16:00 자동 전송
   - 오늘 공시/급등락 요약
   - 내일 주목사항 
   - API: `/trigger/market-close-summary`

4. **급등락 감지**
   - 평일 장중 5분마다 체크
   - ±3% 임계값 (설정 가능)
   - 텔레그램 즉시 알림

5. **시스템 모니터링**
   - 매일 자정 상태 체크
   - 건강 상태 리포트
   - API: `/health`, `/status`

### 🔄 진행 예정

1. **뉴스 수집** (`news.py`)
2. **유튜버 영상 감지** (`influencer.py`)  
3. **쏠림 데이터 수집** (`buzz.py`)
4. **AI 분석 기능** (`analyzers/`)
5. **웹앱 API** (`api/`)

## 🔧 설정 옵션

### 환경변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `DATABASE_URL` | DB 연결 문자열 | `sqlite:///./invest_engine.db` |
| `DART_API_KEY` | DART API 키 | - |
| `TELEGRAM_BOT_TOKEN` | 텔레그램 봇 토큰 | - |
| `TELEGRAM_CHAT_ID` | 채팅 ID | - |
| `TIMEZONE` | 시간대 | `Asia/Seoul` |
| `MORNING_BRIEFING_TIME` | 아침 브리핑 시간 | `08:30` |
| `MARKET_CLOSE_TIME` | 마감 요약 시간 | `16:00` |
| `PRICE_ALERT_THRESHOLD` | 급등락 임계값(%) | `3.0` |

### DART API 키 발급

1. [DART 홈페이지](https://opendart.fss.or.kr/) 접속
2. 회원가입 후 로그인  
3. API 키 신청 및 발급
4. `.env` 파일에 키 설정

## 📊 API 엔드포인트

### 기본 정보
- `GET /` - 기본 정보
- `GET /health` - 헬스 체크  
- `GET /status` - 상세 상태

### 수동 실행
- `POST /trigger/morning-briefing` - 아침 브리핑
- `POST /trigger/market-close-summary` - 마감 요약
- `POST /trigger/dart-collection` - DART 수집
- `POST /trigger/test-telegram` - 텔레그램 테스트

### 데이터 조회  
- `GET /data/filings` - 최근 공시 조회
- `GET /data/alerts` - 최근 알림 로그

## 🗄 데이터베이스

### 주요 테이블

- **stocks**: 종목 기본 정보
- **watchlist**: 유저별 관심종목  
- **alerts_log**: 발송된 알림 기록
- **dart_filings**: DART 공시 정보
- **news**: 수집된 뉴스 (예정)
- **price_alerts**: 급등락 기록
- **buzz_data**: 쏠림 데이터 (예정)
- **influencer_videos**: 유튜버 영상 (예정)

## ⏰ 스케줄

| 작업 | 실행 시간 | 설명 |
|------|-----------|------|
| 아침 브리핑 | 평일 08:30 | 어제 공시/급등락 요약 |
| 마감 요약 | 평일 16:00 | 오늘 결과 요약 |
| DART 수집 | 평일 매시 정각 | 새 공시 확인 및 알림 |
| 급등락 감지 | 평일 장중 5분마다 | ±3% 이상 변동 감지 |
| 상태 체크 | 매일 자정 | 시스템 건강 상태 확인 |

## 🔍 로그

로그는 `logs/invest_engine.log`에 저장되며, 일별 로테이션됩니다.

```bash
# 로그 확인
tail -f logs/invest_engine.log

# 에러만 확인  
grep ERROR logs/invest_engine.log
```

## 🧪 테스트

```bash
# 텔레그램 봇 테스트
curl -X POST http://localhost:8000/trigger/test-telegram

# DART 수집 테스트
curl -X POST http://localhost:8000/trigger/dart-collection

# 아침 브리핑 테스트  
curl -X POST http://localhost:8000/trigger/morning-briefing
```

## 🚨 문제해결

### 1. 텔레그램 봇이 작동하지 않는 경우
- 봇 토큰 확인
- 채팅 ID 확인 (봇과 먼저 채팅 시작)
- 네트워크 연결 확인

### 2. DART API 오류  
- API 키 유효성 확인
- 일일 호출 제한 확인  
- DART 서버 상태 확인

### 3. 데이터베이스 오류
- SQLite 파일 권한 확인
- 디스크 공간 확인

## 📈 향후 계획

1. **Phase 2**: 뉴스 수집 및 AI 분석
2. **Phase 3**: 유튜버 시그널 분석  
3. **Phase 4**: 쏠림 지표 개발
4. **Phase 5**: 웹앱 연동 API
5. **Phase 6**: PostgreSQL 마이그레이션

## 📞 지원

문제가 있으면 GitHub Issues로 제보해주세요.

---

**Investment Engine v1.0.0** 🚀  
*현명한 투자를 위한 정보 수집 엔진*