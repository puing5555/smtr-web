"""
Naver Finance News Collector
네이버 증권 뉴스 수집 모듈
"""
import httpx
import asyncio
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

class NaverNewsCollector:
    """네이버 증권 뉴스 수집기"""
    
    def __init__(self):
        self.base_url = "https://finance.naver.com"
        self.main_news_url = "https://finance.naver.com/news/mainnews.naver"
        self.session = None
        self.kst = pytz.timezone('Asia/Seoul')
        
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
    
    async def get_main_news(self) -> List[Dict]:
        """
        네이버 증권 주요 뉴스 수집
        
        Returns:
            뉴스 정보 리스트
        """
        try:
            response = await self.session.get(self.main_news_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            
            # 주요 뉴스 섹션 찾기
            main_news_area = soup.find('div', class_='mainNewsList')
            if not main_news_area:
                logger.warning("Main news area not found")
                return []
            
            # 뉴스 아이템들 찾기
            news_items = main_news_area.find_all('dd')
            
            for item in news_items:
                try:
                    link_elem = item.find('a')
                    if not link_elem:
                        continue
                        
                    title = link_elem.get_text().strip()
                    if not title:
                        continue
                        
                    # URL 정리
                    url = link_elem.get('href')
                    if not url:
                        continue
                        
                    if url.startswith('/'):
                        url = urljoin(self.base_url, url)
                    
                    # 시간 정보 찾기
                    time_elem = item.find('span', class_='wdate')
                    time_str = None
                    published_at = None
                    
                    if time_elem:
                        time_str = time_elem.get_text().strip()
                        published_at = self._parse_time(time_str)
                    
                    # 뉴스 데이터 생성
                    news_data = {
                        'title': title,
                        'url': url,
                        'source': 'naver_finance',
                        'category': 'market_news',
                        'published_at': published_at,
                        'time_str': time_str
                    }
                    
                    news_list.append(news_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse news item: {e}")
                    continue
                    
            logger.info(f"Collected {len(news_list)} main news items")
            return news_list
            
        except Exception as e:
            logger.error(f"Failed to fetch main news: {e}")
            return []
    
    async def get_stock_news(self, stock_code: str, limit: int = 10) -> List[Dict]:
        """
        특정 종목 관련 뉴스 수집
        
        Args:
            stock_code: 종목코드 (e.g., "005930")
            limit: 수집할 뉴스 개수
            
        Returns:
            뉴스 정보 리스트
        """
        try:
            # 종목별 뉴스 URL
            stock_news_url = f"https://finance.naver.com/item/news_news.naver?code={stock_code}"
            
            response = await self.session.get(stock_news_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            
            # 뉴스 테이블 찾기
            news_table = soup.find('table', class_='type5')
            if not news_table:
                logger.warning(f"News table not found for stock {stock_code}")
                return []
            
            # 뉴스 행들 찾기
            news_rows = news_table.find_all('tr')[2:]  # 헤더 제외
            
            for row in news_rows[:limit]:
                try:
                    cells = row.find_all('td')
                    if len(cells) < 3:
                        continue
                        
                    # 제목과 링크
                    title_cell = cells[0]
                    link_elem = title_cell.find('a')
                    if not link_elem:
                        continue
                        
                    title = link_elem.get_text().strip()
                    if not title:
                        continue
                        
                    url = link_elem.get('href')
                    if not url:
                        continue
                        
                    if url.startswith('/'):
                        url = urljoin(self.base_url, url)
                    
                    # 정보제공 (출처)
                    source_cell = cells[1]
                    source = source_cell.get_text().strip() if source_cell else 'Unknown'
                    
                    # 날짜
                    date_cell = cells[2]
                    date_str = date_cell.get_text().strip() if date_cell else None
                    published_at = self._parse_date(date_str)
                    
                    news_data = {
                        'title': title,
                        'url': url,
                        'source': f'naver_finance_{source.lower()}',
                        'category': 'stock_news',
                        'published_at': published_at,
                        'stock_codes': [stock_code],
                        'date_str': date_str
                    }
                    
                    news_list.append(news_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse stock news item: {e}")
                    continue
                    
            logger.info(f"Collected {len(news_list)} stock news items for {stock_code}")
            return news_list
            
        except Exception as e:
            logger.error(f"Failed to fetch stock news for {stock_code}: {e}")
            return []
    
    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """
        시간 문자열을 datetime으로 변환 (오늘 기준)
        
        Args:
            time_str: 시간 문자열 (예: "14:30")
            
        Returns:
            datetime 객체 또는 None
        """
        if not time_str:
            return None
            
        try:
            # "14:30" 형태
            if re.match(r'\d{2}:\d{2}', time_str):
                today = datetime.now(self.kst).date()
                time_obj = datetime.strptime(time_str, '%H:%M').time()
                return datetime.combine(today, time_obj, tzinfo=self.kst)
            
            # "2월20일" 형태
            month_day_match = re.match(r'(\d{1,2})월(\d{1,2})일', time_str)
            if month_day_match:
                month = int(month_day_match.group(1))
                day = int(month_day_match.group(2))
                year = datetime.now(self.kst).year
                return datetime(year, month, day, tzinfo=self.kst)
                
            return None
            
        except Exception as e:
            logger.warning(f"Failed to parse time string '{time_str}': {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        날짜 문자열을 datetime으로 변환
        
        Args:
            date_str: 날짜 문자열 (예: "2024.02.20")
            
        Returns:
            datetime 객체 또는 None
        """
        if not date_str:
            return None
            
        try:
            # "2024.02.20" 형태
            if re.match(r'\d{4}\.\d{2}\.\d{2}', date_str):
                return datetime.strptime(date_str, '%Y.%m.%d').replace(tzinfo=self.kst)
            
            # "02.20" 형태 (올해)
            if re.match(r'\d{2}\.\d{2}', date_str):
                year = datetime.now(self.kst).year
                return datetime.strptime(f"{year}.{date_str}", '%Y.%m.%d').replace(tzinfo=self.kst)
                
            return None
            
        except Exception as e:
            logger.warning(f"Failed to parse date string '{date_str}': {e}")
            return None
    
    def extract_stock_codes_from_title(self, title: str) -> List[str]:
        """
        뉴스 제목에서 종목코드 추출
        
        Args:
            title: 뉴스 제목
            
        Returns:
            추출된 종목코드 리스트
        """
        stock_codes = []
        
        # 일반적인 대기업 종목코드 매칭
        stock_patterns = {
            '삼성전자': '005930',
            'SK하이닉스': '000660',
            'NAVER': '035420',
            '카카오': '035720',
            'LG에너지솔루션': '373220',
            '현대차': '005380',
            '기아': '000270',
            'POSCO홀딩스': '005490',
            '삼성바이오로직스': '207940',
            'LG화학': '051910'
        }
        
        for company_name, stock_code in stock_patterns.items():
            if company_name in title:
                stock_codes.append(stock_code)
        
        # 직접적인 종목코드 패턴 매칭 (6자리 숫자)
        code_matches = re.findall(r'\b(\d{6})\b', title)
        for code in code_matches:
            if code not in stock_codes:
                stock_codes.append(code)
        
        return stock_codes
    
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
        
        # 중요한 키워드들
        important_keywords = [
            '급등', '급락', '상승', '하락', '실적', '배당',
            '증자', '감자', '분할', '합병', '인수',
            '승인', '허가', '계약', '투자',
            '코스피', '코스닥', '시장'
        ]
        
        for keyword in important_keywords:
            if keyword in title:
                score += 0.1
        
        # 종목 관련 뉴스는 중요도 증가
        if news_data.get('stock_codes'):
            score += 0.2
        
        # 카테고리별 가중치
        if news_data.get('category') == 'market_news':
            score += 0.1
        elif news_data.get('category') == 'stock_news':
            score += 0.2
        
        return min(score, 1.0)  # 최대 1.0으로 제한
    
    async def collect_and_store_news(self, collect_stock_news: bool = False) -> int:
        """
        뉴스 수집하여 DB에 저장
        
        Args:
            collect_stock_news: 종목별 뉴스도 수집할지 여부
            
        Returns:
            저장된 뉴스 개수
        """
        all_news = []
        
        # 주요 뉴스 수집
        main_news = await self.get_main_news()
        all_news.extend(main_news)
        
        # 종목별 뉴스 수집 (선택적)
        if collect_stock_news:
            # 주요 종목들에 대해 뉴스 수집
            major_stocks = ['005930', '000660', '035420', '035720']  # 삼성전자, SK하이닉스, 네이버, 카카오
            
            for stock_code in major_stocks:
                try:
                    stock_news = await self.get_stock_news(stock_code, limit=5)
                    all_news.extend(stock_news)
                    # 요청 간 딜레이
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Failed to collect news for stock {stock_code}: {e}")
        
        if not all_news:
            return 0
        
        db = get_db_session()
        new_news_count = 0
        
        try:
            for news_data in all_news:
                # 이미 저장된 뉴스인지 확인
                existing = db.query(News).filter(
                    News.url == news_data['url']
                ).first()
                
                if existing:
                    continue
                
                # 제목에서 종목코드 추출 (stock_codes가 없는 경우)
                if not news_data.get('stock_codes'):
                    news_data['stock_codes'] = self.extract_stock_codes_from_title(
                        news_data['title']
                    )
                
                # 중요도 점수 계산
                importance_score = self.calculate_importance_score(news_data)
                
                # 새 뉴스 저장
                news = News(
                    title=news_data['title'],
                    url=news_data['url'],
                    source=news_data['source'],
                    market='kr',  # 한국 뉴스로 설정
                    published_at=news_data.get('published_at'),
                    stock_codes=news_data.get('stock_codes', []),
                    importance_score=importance_score
                )
                
                db.add(news)
                new_news_count += 1
                
                logger.info(f"New news: {news.title[:50]}...")
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to store news: {e}")
            
        finally:
            db.close()
            
        # 중요도 높은 뉴스는 텔레그램 알림 자동 발송
        if new_news_count > 0:
            try:
                from ..alerts.telegram_alert import telegram_alert
                await telegram_alert.process_high_importance_news(min_importance=0.7)
            except Exception as e:
                logger.error(f"Failed to send telegram alerts for high importance news: {e}")
        
        return new_news_count

# Helper function for manual testing
async def test_naver_news_collector():
    """네이버 뉴스 수집기 테스트"""
    async with NaverNewsCollector() as collector:
        # 주요 뉴스 테스트
        main_news = await collector.get_main_news()
        logger.info(f"Found {len(main_news)} main news items")
        
        for news in main_news[:3]:  # Show first 3
            logger.info(f"- {news['title'][:50]}...")
        
        # 종목별 뉴스 테스트
        stock_news = await collector.get_stock_news('005930', limit=3)
        logger.info(f"Found {len(stock_news)} stock news items for 005930")
        
        for news in stock_news:
            logger.info(f"- {news['title'][:50]}...")

if __name__ == "__main__":
    # Test run
    asyncio.run(test_naver_news_collector())