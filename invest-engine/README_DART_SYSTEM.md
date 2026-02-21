# DART 공시 필터링 + AI 요약 + 텔레그램 알림 시스템

## 개요
한국 증권시장의 DART(전자공시시스템) 공시를 자동으로 수집하고, AI로 분석하여 중요한 내용만 텔레그램으로 알림을 보내는 시스템입니다.

## 주요 기능

### 1. 3단계 공시 필터링 시스템
- **A등급 (정기공시)**: 사업보고서, 반기보고서, 분기보고서
  - AI로 매출/영업익/순이익 핵심 수치 추출 및 전년 대비 비교
- **B등급 (중요 비정기공시)**: 자기주식, 증자, 임원변경, 합병 등 투자에 영향을 주는 공시
  - AI로 핵심 내용 요약 및 투자 영향 분석  
- **C등급 (기타)**: DB에만 저장, 알림 발송하지 않음

### 2. AI 분석 (OpenAI GPT-4o-mini)
- A등급: 재무제표 핵심 수치 자동 추출
- B등급: 공시 내용 요약 및 투자 포인트 분석
- 한국어 최적화된 프롬프트 엔지니어링

### 3. 텔레그램 알림 포맷
#### A등급 (실적 공시)
```
📊 [실적] 삼성전자 사업보고서 (2024)

매출: 1,234억원 (전년 1,100억원, +12.2%)
영업익: 156억원 (전년 120억원, +30.0%)
순이익: 98억원 (전년 85억원, +15.3%)

⚡ 전반적으로 양호한 실적 개선을 보였습니다.
🔗 DART 상세보기
```

#### B등급 (중요 공시)
```
🔔 [자기주식] 현대차
자기주식 취득을 통한 주주가치 제고 방안을 발표했습니다.
총 1,000억원 규모로 6개월간 진행될 예정입니다.

💡 투자 포인트: 긍정적 - 주가 상승 요인으로 작용할 것으로 예상
🔗 DART 상세보기
```

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (.env)
```env
# DART API 키 (https://opendart.fss.or.kr/)
DART_API_KEY=your_dart_api_key

# 텔레그램 봇
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# OpenAI API (필수)
OPENAI_API_KEY=your_openai_api_key
```

### 3. OpenAI API 키 설정
- https://platform.openai.com/ 에서 API 키 발급
- .env 파일의 OPENAI_API_KEY에 설정
- API 키가 없으면 목업 모드로 동작 (테스트용)

## 사용법

### 전체 파이프라인 테스트
```bash
cd C:\Users\Mario\work\invest-engine
python test_pipeline.py --mode all
```

### 특정 기능만 테스트
```bash
python test_pipeline.py --mode specific
```

### 실제 알림 발송 테스트 (주의!)
```bash
python test_pipeline.py --mode live
```

### 개별 모듈 테스트
```bash
# 공시 필터링 테스트
python -m src.analyzers.filing_filter

# AI 분석 테스트  
python -m src.analyzers.ai_summarizer

# DART 수집기 테스트
python -m src.collectors.dart
```

### 실제 파이프라인 실행
```python
from src.pipeline import run_daily_pipeline
import asyncio

# 매일 실행할 파이프라인
stats = asyncio.run(run_daily_pipeline())
print(f"처리 결과: {stats}")
```

## 파일 구조
```
src/
├── analyzers/
│   ├── filing_filter.py     # 공시 3단계 필터링
│   └── ai_summarizer.py     # OpenAI 기반 AI 분석
├── alerts/
│   └── telegram_bot.py      # 텔레그램 알림 (업데이트됨)
├── collectors/
│   └── dart.py             # DART API 수집기
├── db/
│   └── models.py           # DB 모델 (컬럼 추가됨)
└── pipeline.py             # 메인 파이프라인

test_pipeline.py            # 종합 테스트 스크립트
```

## 주요 특징

### 1. 한국 시장 특화
- DART API 직접 연동
- 한국어 공시 내용 AI 분석 최적화
- KST 시간대 기준 동작

### 2. 비용 효율적
- OpenAI GPT-4o-mini 사용 (저렴한 모델)
- 중요 공시만 선별 분석
- 토큰 사용량 최적화

### 3. 확장 가능
- 다양한 알림 채널 지원 가능
- 사용자별 관심 종목 필터링 추가 가능
- 실시간 스케줄링 지원

### 4. 안정성
- 에러 핸들링 및 로깅
- DB에 모든 데이터 저장
- API 장애시 목업 모드 동작

## 스케줄링 예시

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.pipeline import run_daily_pipeline

scheduler = AsyncIOScheduler()

# 매일 오전 9시에 실행
scheduler.add_job(
    run_daily_pipeline,
    'cron', 
    hour=9, 
    minute=0,
    timezone='Asia/Seoul'
)

scheduler.start()
```

## 문제 해결

### OpenAI API 키가 없는 경우
- 시스템이 자동으로 목업 모드로 전환됩니다
- 실제 분석 대신 테스트용 데이터를 사용합니다
- 기능 테스트는 가능하지만 실제 AI 분석은 불가합니다

### DART API 제한
- 하루 10,000회 호출 제한
- 분당 100회 호출 제한
- 필요시 호출 간격 조정

### 텔레그램 발송 실패
- 봇 토큰과 채팅 ID 확인
- 봇이 해당 채팅방에 참여되어 있는지 확인
- 메시지 길이 제한 (4096자) 주의

## 개발자 정보
- 개발 언어: Python 3.8+
- 주요 라이브러리: FastAPI, SQLAlchemy, OpenAI, python-telegram-bot
- 데이터베이스: SQLite (기본) / PostgreSQL 지원
- 인코딩: UTF-8 (Windows 환경 고려)

## 라이선스
MIT License