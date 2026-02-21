"""
US Stock News Collector
미국 주식 뉴스 수집 모듈
Yahoo Finance RSS 및 Google Finance 뉴스 수집
"""
import httpx
import asyncio
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
import pytz
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, parse_qs, urlparse
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..db.database import get_db_session
from ..db.models import News

class USNewsCollector:
    """미국 주식 뉴스 수집기"""
    
    def __init__(self):
        self.session = None
        self.est = pytz.timezone('US/Eastern')
        self.utc = pytz.UTC
        
        # Yahoo Finance RSS URLs
        self.yahoo_rss_urls = {
            'market_news': 'https://finance.yahoo.com/news/rssindex',
            'stock_news': 'https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US',
        }
        
        # 주요 미국 종목들
        self.major_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK.B',
            'UNH', 'JNJ', 'XOM', 'V', 'PG', 'JPM', 'HD', 'CVX', 'MA', 'PFE',
            'ABBV', 'BAC', 'KO', 'AVGO', 'PEP', 'TMO', 'COST', 'MRK', 'WMT', 'LLY'
        ]
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout=30.0
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def get_yahoo_market_news(self, limit: int = 20) -> List[Dict]:
        """
        Yahoo Finance 마켓 뉴스 수집 (RSS)
        
        Args:
            limit: 수집할 뉴스 개수
            
        Returns:
            뉴스 정보 리스트
        """
        try:
            response = await self.session.get(self.yahoo_rss_urls['market_news'])
            response.raise_for_status()
            
            # RSS 파싱
            feed = feedparser.parse(response.content)
            news_list = []
            
            if not feed.entries:
                logger.warning("No RSS entries found from Yahoo Finance")
                return []
            
            for entry in feed.entries[:limit]:
                try:
                    # 기본 정보 추출
                    title = entry.title.strip() if hasattr(entry, 'title') else ''
                    if not title:
                        continue
                        
                    url = entry.link if hasattr(entry, 'link') else ''
                    if not url:
                        continue
                    
                    # 발행 시간
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        # RSS의 published_parsed는 GMT 시간
                        dt = datetime(*entry.published_parsed[:6])
                        published_at = self.utc.localize(dt)
                    elif hasattr(entry, 'published'):
                        # 문자열로 된 날짜 파싱 시도
                        published_at = self._parse_date_string(entry.published)
                    
                    # 요약/설명
                    summary = ''
                    if hasattr(entry, 'summary'):
                        # HTML 태그 제거
                        soup = BeautifulSoup(entry.summary, 'html.parser')
                        summary = soup.get_text().strip()
                    
                    # 뉴스 데이터 생성
                    news_data = {
                        'title': title,
                        'url': url,
                        'source': 'yahoo_finance',
                        'category': 'us_market_news',
                        'published_at': published_at,
                        'summary': summary[:500] if summary else None  # 요약문 길이 제한
                    }
                    
                    # 제목에서 종목 추출
                    tickers = self.extract_tickers_from_text(title + ' ' + summary)
                    if tickers:
                        news_data['stock_codes'] = tickers
                    
                    news_list.append(news_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse RSS entry: {e}")
                    continue
                    
            logger.info(f"Collected {len(news_list)} market news from Yahoo Finance RSS")
            return news_list
            
        except Exception as e:
            logger.error(f"Failed to fetch Yahoo Finance RSS: {e}")
            return []
    
    async def get_stock_specific_news(self, ticker: str, limit: int = 10) -> List[Dict]:
        """
        특정 종목 관련 뉴스 수집 (Yahoo Finance RSS)
        
        Args:
            ticker: 종목 심볼 (e.g., "AAPL")
            limit: 수집할 뉴스 개수
            
        Returns:
            뉴스 정보 리스트
        """
        try:
            # 종목별 RSS URL
            rss_url = self.yahoo_rss_urls['stock_news'].format(ticker=ticker)
            
            response = await self.session.get(rss_url)
            response.raise_for_status()
            
            # RSS 파싱
            feed = feedparser.parse(response.content)
            news_list = []
            
            if not feed.entries:
                logger.debug(f"No RSS entries found for ticker {ticker}")
                return []
            
            for entry in feed.entries[:limit]:
                try:
                    title = entry.title.strip() if hasattr(entry, 'title') else ''
                    if not title:
                        continue
                        
                    url = entry.link if hasattr(entry, 'link') else ''
                    if not url:
                        continue
                    
                    # 발행 시간
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        dt = datetime(*entry.published_parsed[:6])
                        published_at = self.utc.localize(dt)
                    
                    # 요약
                    summary = ''
                    if hasattr(entry, 'summary'):
                        soup = BeautifulSoup(entry.summary, 'html.parser')
                        summary = soup.get_text().strip()
                    
                    news_data = {
                        'title': title,
                        'url': url,
                        'source': 'yahoo_finance',
                        'category': 'us_stock_news',
                        'published_at': published_at,
                        'summary': summary[:500] if summary else None,
                        'stock_codes': [ticker]  # 요청된 종목 코드 포함
                    }
                    
                    # 다른 종목도 언급되었는지 확인
                    other_tickers = self.extract_tickers_from_text(title + ' ' + summary)
                    if other_tickers:
                        # 중복 제거하면서 추가
                        all_tickers = list(set([ticker] + other_tickers))
                        news_data['stock_codes'] = all_tickers
                    
                    news_list.append(news_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse stock news entry for {ticker}: {e}")
                    continue
                    
            logger.info(f"Collected {len(news_list)} stock news for {ticker}")
            return news_list
            
        except Exception as e:
            logger.error(f"Failed to fetch stock news for {ticker}: {e}")
            return []
    
    async def get_google_finance_news(self, query: str = "US stocks", limit: int = 10) -> List[Dict]:
        """
        Google Finance 뉴스 스크래핑 (백업용)
        
        Args:
            query: 검색 쿼리
            limit: 수집할 뉴스 개수
            
        Returns:
            뉴스 정보 리스트
        """
        try:
            # Google Finance 뉴스 URL
            url = f"https://www.google.com/finance/quote/{query}:NASDAQ"
            
            response = await self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            
            # Google Finance의 뉴스 섹션 찾기 (구조가 자주 변경됨)
            # 이 부분은 실제 Google Finance 페이지 구조에 따라 조정 필요
            news_articles = soup.find_all('div', class_='yY3Lee')  # 예시 클래스명
            
            for article in news_articles[:limit]:
                try:
                    title_elem = article.find('div', class_='Yfwt5')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text().strip()
                    if not title:
                        continue
                    
                    # URL 추출
                    link_elem = article.find('a')
                    url = link_elem.get('href') if link_elem else ''
                    if url and url.startswith('/url?'):
                        # Google redirect URL 디코딩
                        parsed = urlparse(url)
                        query_params = parse_qs(parsed.query)
                        if 'url' in query_params:
                            url = query_params['url'][0]
                    
                    # 시간 정보
                    time_elem = article.find('div', class_='Adak')
                    time_str = time_elem.get_text().strip() if time_elem else ''
                    published_at = self._parse_relative_time(time_str)
                    
                    news_data = {
                        'title': title,
                        'url': url,
                        'source': 'google_finance',
                        'category': 'us_market_news',
                        'published_at': published_at,
                        'time_str': time_str
                    }
                    
                    # 종목 추출
                    tickers = self.extract_tickers_from_text(title)
                    if tickers:
                        news_data['stock_codes'] = tickers
                    
                    news_list.append(news_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse Google Finance article: {e}")
                    continue
                    
            logger.info(f"Collected {len(news_list)} news from Google Finance")
            return news_list
            
        except Exception as e:
            logger.error(f"Failed to fetch Google Finance news: {e}")
            return []
    
    def extract_tickers_from_text(self, text: str) -> List[str]:
        """
        텍스트에서 미국 주식 티커 추출
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            추출된 티커 리스트
        """
        tickers = []
        text_upper = text.upper()
        
        # 주요 종목 패턴 매칭
        stock_patterns = {
            'APPLE': 'AAPL',
            'MICROSOFT': 'MSFT',
            'GOOGLE': 'GOOGL',
            'ALPHABET': 'GOOGL',
            'AMAZON': 'AMZN',
            'NVIDIA': 'NVDA',
            'TESLA': 'TSLA',
            'META': 'META',
            'FACEBOOK': 'META',
            'BERKSHIRE': 'BRK.B',
            'JOHNSON & JOHNSON': 'JNJ',
            'EXXON': 'XOM',
            'VISA': 'V',
            'PROCTER & GAMBLE': 'PG',
            'JPMORGAN': 'JPM',
            'HOME DEPOT': 'HD',
            'CHEVRON': 'CVX',
            'MASTERCARD': 'MA',
            'PFIZER': 'PFE',
            'COCA-COLA': 'KO',
            'BROADCOM': 'AVGO',
            'PEPSICO': 'PEP',
            'WALMART': 'WMT'
        }
        
        # 회사명으로 티커 추출
        for company_name, ticker in stock_patterns.items():
            if company_name in text_upper:
                tickers.append(ticker)
        
        # 직접적인 티커 심볼 패턴 (대문자 2-5자리)
        ticker_pattern = r'\b([A-Z]{2,5})\b'
        found_tickers = re.findall(ticker_pattern, text_upper)
        
        for ticker in found_tickers:
            # 알려진 주요 종목인지 확인
            if ticker in self.major_tickers and ticker not in tickers:
                tickers.append(ticker)
        
        return list(set(tickers))  # 중복 제거
    
    def calculate_importance_score(self, news_data: Dict) -> float:
        """
        뉴스의 중요도 점수 계산
        
        Args:
            news_data: 뉴스 데이터
            
        Returns:
            중요도 점수 (0.0 ~ 1.0)
        """
        score = 0.5  # 기본 점수
        title = news_data.get('title', '').lower()
        summary = news_data.get('summary') or ''
        summary = summary.lower() if summary else ''
        text = title + ' ' + summary
        
        # 중요한 키워드들 (영문)
        important_keywords = [
            'earnings', 'revenue', 'profit', 'loss', 'dividend',
            'acquisition', 'merger', 'ipo', 'stock split',
            'sec filing', 'fda approval', 'breakthrough',
            'partnership', 'contract', 'deal', 'investment',
            'upgrade', 'downgrade', 'target price',
            'surge', 'plunge', 'rally', 'crash', 'volatility',
            'nasdaq', 'sp500', 's&p 500', 'dow jones'
        ]
        
        for keyword in important_keywords:
            if keyword in text:
                score += 0.1
        
        # 주요 종목 언급 시 중요도 증가
        if news_data.get('stock_codes'):
            num_major_stocks = len([t for t in news_data['stock_codes'] if t in self.major_tickers[:10]])
            score += num_major_stocks * 0.15
        
        # 카테고리별 가중치
        category = news_data.get('category', '')
        if 'earnings' in category.lower():
            score += 0.2
        elif 'stock_news' in category:
            score += 0.15
        elif 'market_news' in category:
            score += 0.1
        
        return min(score, 1.0)  # 최대 1.0으로 제한
    
    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """
        날짜 문자열을 datetime으로 변환
        
        Args:
            date_str: 날짜 문자열
            
        Returns:
            datetime 객체 또는 None
        """
        if not date_str:
            return None
            
        try:
            # 여러 날짜 형식 시도
            date_formats = [
                '%a, %d %b %Y %H:%M:%S %Z',  # RSS 표준
                '%a, %d %b %Y %H:%M:%S %z',  # 타임존 포함
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S%z'
            ]
            
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    if dt.tzinfo is None:
                        dt = self.utc.localize(dt)
                    return dt
                except ValueError:
                    continue
                    
            return None
            
        except Exception as e:
            logger.warning(f"Failed to parse date string '{date_str}': {e}")
            return None
    
    def _parse_relative_time(self, time_str: str) -> Optional[datetime]:
        """
        상대적 시간 문자열을 datetime으로 변환
        
        Args:
            time_str: 시간 문자열 (e.g., "2 hours ago")
            
        Returns:
            datetime 객체 또는 None
        """
        if not time_str:
            return None
            
        try:
            now = datetime.now(self.utc)
            time_str = time_str.lower()
            
            if 'minute' in time_str:
                minutes = re.search(r'(\d+)\s*minute', time_str)
                if minutes:
                    return now - timedelta(minutes=int(minutes.group(1)))
            elif 'hour' in time_str:
                hours = re.search(r'(\d+)\s*hour', time_str)
                if hours:
                    return now - timedelta(hours=int(hours.group(1)))
            elif 'day' in time_str:
                days = re.search(r'(\d+)\s*day', time_str)
                if days:
                    return now - timedelta(days=int(days.group(1)))
                    
            return None
            
        except Exception as e:
            logger.warning(f"Failed to parse relative time '{time_str}': {e}")
            return None
    
    async def collect_and_store_news(
        self, 
        collect_stock_specific: bool = True,
        stock_limit_per_ticker: int = 5,
        market_news_limit: int = 20
    ) -> int:
        """
        미국 뉴스 수집하여 DB에 저장
        
        Args:
            collect_stock_specific: 종목별 뉴스도 수집할지 여부
            stock_limit_per_ticker: 종목당 수집할 뉴스 개수
            market_news_limit: 마켓 뉴스 수집 개수
            
        Returns:
            저장된 뉴스 개수
        """
        all_news = []
        
        # Yahoo Finance 마켓 뉴스 수집
        try:
            market_news = await self.get_yahoo_market_news(limit=market_news_limit)
            all_news.extend(market_news)
            logger.info(f"Collected {len(market_news)} market news items")
        except Exception as e:
            logger.error(f"Failed to collect market news: {e}")
        
        # 주요 종목별 뉴스 수집
        if collect_stock_specific:
            # 주요 종목들 중 일부만 선택 (API 요청 제한 고려)
            selected_tickers = self.major_tickers[:10]  # 상위 10개 종목만
            
            for ticker in selected_tickers:
                try:
                    stock_news = await self.get_stock_specific_news(
                        ticker, 
                        limit=stock_limit_per_ticker
                    )
                    all_news.extend(stock_news)
                    
                    # API 요청 간 딜레이 (Rate limiting 방지)
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Failed to collect news for {ticker}: {e}")
        
        if not all_news:
            logger.warning("No news collected")
            return 0
        
        # DB에 저장
        db = get_db_session()
        new_news_count = 0
        
        try:
            for news_data in all_news:
                # 중복 확인
                existing = db.query(News).filter(
                    News.url == news_data['url']
                ).first()
                
                if existing:
                    continue
                
                # 중요도 점수 계산
                importance_score = self.calculate_importance_score(news_data)
                
                # 새 뉴스 저장
                news = News(
                    title=news_data['title'],
                    url=news_data['url'],
                    source=news_data['source'],
                    market='us',  # 미국 뉴스로 설정
                    published_at=news_data.get('published_at'),
                    stock_codes=news_data.get('stock_codes', []),
                    importance_score=importance_score,
                    content=news_data.get('summary')  # 요약을 content에 저장
                )
                
                db.add(news)
                new_news_count += 1
                
                logger.info(f"New US news: {news.title[:50]}...")
            
            db.commit()
            logger.info(f"Successfully stored {new_news_count} US news items")
            
            # 수집된 뉴스 자동 번역 실행
            if new_news_count > 0:
                try:
                    from ..services.translator import translate_news_batch
                    translated_count = await translate_news_batch(market='us', limit=new_news_count)
                    logger.info(f"Auto-translated {translated_count} US news items")
                except Exception as e:
                    logger.warning(f"Auto-translation failed: {e}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to store US news: {e}")
            
        finally:
            db.close()
            
        return new_news_count

# Helper function for manual testing
async def test_us_news_collector():
    """미국 뉴스 수집기 테스트"""
    async with USNewsCollector() as collector:
        # 마켓 뉴스 테스트
        market_news = await collector.get_yahoo_market_news(limit=5)
        logger.info(f"Found {len(market_news)} market news items")
        
        for news in market_news:
            logger.info(f"- {news['title'][:70]}...")
            if news.get('stock_codes'):
                logger.info(f"  Tickers: {news['stock_codes']}")
        
        # 종목별 뉴스 테스트
        stock_news = await collector.get_stock_specific_news('AAPL', limit=3)
        logger.info(f"Found {len(stock_news)} AAPL news items")
        
        for news in stock_news:
            logger.info(f"- {news['title'][:70]}...")

if __name__ == "__main__":
    # Test run
    asyncio.run(test_us_news_collector())