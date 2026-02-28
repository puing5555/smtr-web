# 애널리스트 시스템 현황 및 개선 방안

## 현재 상태
- **더미 데이터**: 5명의 가상 애널리스트 (김선우, 이미래, 박테크, 최파이낸스, 정에너지)
- **증권사**: 한국투자증권, 미래에셋증권, NH투자증권, 대신증권, 키움증권
- **데이터**: 완전히 하드코딩된 가상 리포트와 수익률

## 실제 증권사 리포트 수집 방법

### 1. 공식 API (제한적)
- **한국투자증권**: KIS Developers API (개인 투자자용, 제한적)
- **미래에셋증권**: Open API (계좌 연동 중심, 리포트 제한적)
- **키움증권**: Open API (HTS 연동 중심)
- **문제점**: 대부분 계좌 연동용이며, 애널리스트 리포트는 제공하지 않음

### 2. 웹 스크래핑 방법
**A. 증권사 웹사이트**
- 한국투자증권: https://securities.koreainvestment.com/main/research/research/RsrchList.jsp
- 미래에셋증권: https://securities.miraeasset.com/bbs/board/message/list.do?categoryId=1547
- NH투자증권: https://www.nhqv.com/research
- 키움증권: https://www1.kiwoom.com/h/customer/research/research_01_01
- **문제점**: 대부분 로그인 필요, 회원제 서비스

**B. 금융 포털 사이트**
- **네이버 금융**: https://finance.naver.com/ (일부 리포트 요약 제공)
- **다음 금융**: https://finance.daum.net/
- **한국경제**: https://www.hankyung.com/finance
- **이데일리**: https://www.edaily.co.kr/news/stock
- **장점**: 로그인 없이 접근 가능, 요약 정보 제공

**C. 전문 데이터 제공업체**
- **FnGuide**: https://www.fnguide.com/ (유료)
- **WiseReport**: https://www.wisereport.co.kr/ (유료)
- **에프앤가이드**: 전문 기관투자자용 (고비용)

### 3. 뉴스 기반 수집
**A. 경제 뉴스 사이트**
- 한국경제, 매일경제, 이데일리, 연합인포맥스
- 애널리스트 리포트 관련 기사에서 정보 추출

**B. 증권 전문 뉴스**
- 서울경제 증권 섹션
- 아시아경제 증권 뉴스
- **패턴**: "[증권사] [애널리스트] [종목] 목표가 [금액] 제시"

## 추천 구현 방안

### Phase 1: 뉴스 기반 수집 (단기)
```python
# 예시: 네이버 뉴스에서 애널리스트 리포트 검색
import requests
from bs4 import BeautifulSoup

def collect_analyst_news():
    url = "https://search.naver.com/search.naver"
    params = {
        'where': 'news',
        'query': '애널리스트 리포트 목표가',
        'sm': 'tab_jum'
    }
    # 뉴스 제목과 내용에서 정보 추출
    # 정규표현식으로 "[증권사] [종목] 목표가 [금액]" 패턴 추출
```

### Phase 2: 증권사 웹사이트 스크래핑 (중기)
- Selenium으로 로그인 후 리포트 페이지 접근
- 각 증권사별 구조 분석 및 파서 개발
- 법적/윤리적 검토 필요 (robots.txt, 이용약관 확인)

### Phase 3: 전문 데이터 구매 (장기)
- FnGuide, WiseReport 등 유료 서비스 구독
- API 연동으로 실시간 데이터 수집
- 비용: 월 50-200만원 수준

## 즉시 적용 가능한 개선안

### 1. 더미 데이터 현실화
```typescript
// 실제 증권사 이름과 최근 리포트 스타일로 업데이트
const analysts: Analyst[] = [
  {
    id: 'analyst-001',
    name: '김현중', // 실제 존재하는 스타일의 이름
    company: '삼성증권',
    sector: '반도체/IT',
    lastUpdate: '2026-02-28',
    recentReports: [
      {
        stock: '삼성전자',
        targetPrice: 85000,
        opinion: 'BUY',
        publishedAt: '2026-02-25',
        summary: '3분기 실적 호조, HBM 매출 확대 전망'
      }
    ]
  }
]
```

### 2. 수동 업데이트 시스템
- 주요 경제 뉴스 모니터링
- 주 1-2회 수동으로 실제 리포트 정보 업데이트
- 크라우드소싱: 사용자가 리포트 정보 제보 가능

### 3. 뉴스 RSS 연동
```javascript
// RSS 피드에서 애널리스트 리포트 관련 뉴스 자동 수집
const RSS_SOURCES = [
  'https://rss.hankyung.com/news/economy.xml',
  'https://rss.edaily.co.kr/stock.xml'
]
```

## 결론
1. **단기**: 더미 데이터 현실화 + 수동 업데이트
2. **중기**: 뉴스 기반 자동 수집 시스템
3. **장기**: 전문 데이터 구매 또는 증권사 파트너십

현재로서는 **Phase 1 + 수동 업데이트**가 가장 현실적이고 법적으로 안전한 방법입니다.