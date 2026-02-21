# 🌐 뉴스 번역 기능 가이드

invest-engine에 추가된 영문 뉴스 한국어 번역 기능 사용법입니다.

## ✨ 주요 기능

- **자동 번역**: 미국/암호화폐 뉴스 수집 시 자동으로 한국어 번역
- **배치 처리**: 여러 뉴스를 한 번에 번역하여 API 비용 최소화  
- **GPT-4o-mini 사용**: OpenAI 최신 모델로 고품질 번역
- **웹 UI 지원**: 번역된 뉴스를 웹에서 확인 가능

## 🏗️ 구현 구조

```
src/
├── services/
│   └── translator.py      # 번역 서비스 (새로 추가)
├── collectors/
│   ├── us_news.py         # 미국 뉴스 + 자동번역 통합
│   └── crypto_news.py     # 암호화폐 뉴스 + 자동번역 통합
└── db/
    └── models.py          # News.ai_summary 필드 활용

main.py                    # POST /trigger/translate-news API 추가
test-timeline.html         # 번역된 뉴스 표시 UI (새로 생성)
```

## 🚀 사용법

### 1. 자동 번역 (기본 동작)

뉴스 수집 시 자동으로 번역이 실행됩니다:

```bash
# 미국 뉴스 수집 → 자동 번역
python -c "import asyncio; from src.collectors.us_news import USNewsCollector; asyncio.run(USNewsCollector().collect_all())"

# 암호화폐 뉴스 수집 → 자동 번역  
python -c "import asyncio; from src.collectors.crypto_news import CryptoNewsCollector; asyncio.run(CryptoNewsCollector().collect_and_store_news())"
```

### 2. 수동 번역 API

서버 실행 후 API 호출:

```bash
# 서버 시작
python main.py

# 모든 미번역 뉴스 번역
curl -X POST http://localhost:8000/trigger/translate-news

# 미국 뉴스만 번역
curl -X POST "http://localhost:8000/trigger/translate-news?market=us"

# 암호화폐 뉴스만 번역
curl -X POST "http://localhost:8000/trigger/translate-news?market=crypto"
```

### 3. 웹 UI 확인

브라우저에서 번역된 뉴스 확인:

```
http://localhost:8000/  (서버 실행 후)
file:///C:/Users/Mario/work/invest-engine/test-timeline.html  (직접 열기)
```

**웹 UI 기능:**
- 📰 번역된 제목을 메인으로 표시
- 📝 원문은 작은 글씨로 아래 표시
- 🔄 실시간 새로고침
- 🌐 번역 버튼으로 수동 번역 가능

## 🧪 테스트

번역 기능 테스트:

```bash
python test_translation.py
```

**테스트 결과 예시:**
```
원문: Tesla unveils cheaper Cybertruck model for mass market
번역: 테슬라, 저가형 사이버트럭 공개

원문: Bitcoin breaks $100,000 resistance level amid ETF optimism  
번역: 비트코인, ETF 낙관론 속 10만 달러 저항선 돌파
```

## ⚙️ 설정

### 필수 환경 변수

`.env` 파일에 OpenAI API 키 설정 필요:

```env
OPENAI_API_KEY=sk-proj-your-api-key-here
```

### 번역 옵션

`src/services/translator.py`에서 수정 가능:

- **배치 크기**: `batch_size=15` (한 번에 번역할 뉴스 개수)
- **모델**: `gpt-4o-mini` (비용 최적화)
- **온도**: `temperature=0.3` (일관성 있는 번역)

## 💾 데이터베이스

번역된 내용은 `News` 테이블의 `ai_summary` 필드에 저장:

```sql
-- 번역된 뉴스 조회
SELECT title, ai_summary, market 
FROM news 
WHERE ai_summary IS NOT NULL 
AND market IN ('us', 'crypto')
ORDER BY created_at DESC;
```

## 📊 비용 최적화

- **배치 처리**: 10-20개씩 묶어서 번역
- **중복 방지**: 이미 번역된 뉴스는 스킵
- **gpt-4o-mini**: 저렴한 모델 사용 (gpt-4 대비 1/10 가격)

## 🔧 문제 해결

### OpenAI API 오류
```bash
# .env 파일 확인
cat .env | grep OPENAI_API_KEY

# API 키 테스트
python -c "import openai; print('API Key OK')"
```

### 번역 안됨
```bash
# 미번역 뉴스 확인
python -c "from src.db.database import get_db_session; from src.db.models import News; db = get_db_session(); print(f'미번역: {db.query(News).filter(News.ai_summary.is_(None)).count()}개')"
```

### 인코딩 오류
```bash
# 한글 출력 문제시 (Windows)
chcp 65001
python test_translation.py
```

## 📈 향후 계획

- [ ] 감정 분석 추가
- [ ] 요약 길이 조정 옵션
- [ ] 실시간 번역 스트리밍
- [ ] 다국어 지원 확대

---

**구현 완료일**: 2026-02-20  
**구현자**: OpenClaw AI Assistant  
**테스트 상태**: ✅ 통과