# 자동 수집 스케줄러 설정 완료 ✅

## 구현 내용

### 1. 새로운 수집기 추가
- **`src/collectors/us_news.py`** - 미국 금융 뉴스 수집 (Yahoo Finance, MarketWatch)
- **`src/collectors/crypto_news.py`** - 암호화폐 뉴스 수집 (CoinDesk, CoinTelegraph, 코인데스크 코리아)

### 2. 자동 수집 스케줄러
- **`src/scheduler.py`** - 새로운 자동 수집 스케줄러
- APScheduler 사용 (이미 requirements.txt에 포함됨)

### 3. 스케줄 설정

#### 🇰🇷 한국 뉴스 (Naver)
- **장중** (09:00-18:00 KST): 매 15분 수집
- **장외 + 주말**: 매 30분 수집

#### 🇺🇸 미국 뉴스
- **미장 시간** (22:30-05:00 KST): 매 30분 수집  
- **미장 외 시간**: 매 1시간 수집

#### ₿ 코인 뉴스
- **24시간**: 매 30분 수집

#### 📋 DART 공시
- **장중** (09:00-18:00 KST): 매 20분 수집
- **장외**: 매 1시간 수집

### 4. main.py 통합
- 최소한의 수정으로 새 스케줄러 통합
- 기존 `job_scheduler`와 병행 운영
- FastAPI startup 이벤트에서 자동 시작

### 5. API 엔드포인트 추가
```
GET  /api/scheduler/status  - 스케줄러 상태 조회
POST /api/scheduler/toggle  - 스케줄러 on/off 토글
```

### 6. 로깅 시스템
- 수집 시작/완료/에러 로깅
- 기존 `logs/` 디렉토리 활용
- 이모지를 통한 직관적 로그 메시지

## 사용법

### 서버 시작
```bash
cd C:\Users\Mario\work\invest-engine
python main.py
```

### API 사용
```bash
# 스케줄러 상태 확인
curl http://localhost:8000/api/scheduler/status

# 스케줄러 on/off 토글
curl -X POST http://localhost:8000/api/scheduler/toggle
```

### 테스트
```bash
# 스케줄러 단독 테스트
python test_scheduler.py

# 개별 수집기 테스트
python -m src.collectors.us_news
python -m src.collectors.crypto_news
```

## 로그 예시

```
2026-02-20 15:35:00 | INFO | 🇰🇷 Starting Korean news collection job
2026-02-20 15:35:02 | INFO | ✅ Korean news collection completed: 5 new articles
2026-02-20 15:45:00 | INFO | 📋 Starting DART collection job  
2026-02-20 15:45:03 | INFO | ✅ DART collection completed: 2 new filings
2026-02-20 16:00:00 | INFO | ₿ Starting crypto news collection job
2026-02-20 16:00:04 | INFO | ✅ Crypto news collection completed: 8 new articles
```

## 특징

1. **기존 코드 최소 수정**: main.py에는 스케줄러 시작/종료 코드만 추가
2. **병행 운영**: 기존 `job_scheduler`와 새 `auto_scheduler` 동시 실행
3. **유연한 스케줄링**: 장중/장외 시간에 따른 차별화된 수집 주기
4. **강건성**: 각 수집 작업은 독립적으로 실행되어 하나가 실패해도 다른 작업에 영향 없음
5. **실시간 제어**: API를 통해 스케줄러 상태 조회 및 제어 가능

## 다음 단계

1. 수집된 뉴스 데이터의 AI 분석 및 중요도 평가
2. 주식 종목별 뉴스 필터링 강화
3. 암호화폐 시세 연동
4. 알림 조건 세밀화

---

**설정 완료!** 🎉 이제 invest-engine이 24시간 자동으로 뉴스와 공시를 수집합니다.