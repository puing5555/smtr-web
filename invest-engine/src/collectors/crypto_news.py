"""
Crypto News Collector
암호화폐 뉴스 수집 모듈 - CoinDesk, CoinTelegraph RSS 기반
"""
import httpx
import asyncio
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
import pytz
import re
from urllib.parse import urljoin
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..db.database import get_db_session
from ..db.models import News

class CryptoNewsCollector:
    """암호화폐 뉴스 수집기"""
    
    def __init__(self):
        self.session = None
        self.kst = pytz.timezone('Asia/Seoul')
        
        # RSS 피드 URLs
        self.rss_feeds = {
            'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'cointelegraph': 'https://cointelegraph.com/rss'
        }
        
        # 주요 암호화폐 심볼 매핑
        self.crypto_symbols = {
            'bitcoin': 'BTC',
            'btc': 'BTC',
            'ethereum': 'ETH',
            'eth': 'ETH',
            'ripple': 'XRP',
            'xrp': 'XRP',
            'solana': 'SOL',
            'sol': 'SOL',
            'cardano': 'ADA',
            'ada': 'ADA',
            'dogecoin': 'DOGE',
            'doge': 'DOGE',
            'polygon': 'MATIC',
            'matic': 'MATIC',
            'chainlink': 'LINK',
            'link': 'LINK',
            'polkadot': 'DOT',
            'dot': 'DOT',
            'avalanche': 'AVAX',
            'avax': 'AVAX',
            'litecoin': 'LTC',
            'ltc': 'LTC',
            'shiba inu': 'SHIB',
            'shib': 'SHIB',
            'tron': 'TRX',
            'trx': 'TRX'
        }
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout=30.0,
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def fetch_coindesk_news(self) -> List[Dict]:
        """
        CoinDesk RSS 피드에서 뉴스 수집
        
        Returns:
            뉴스 정보 리스트
        """
        try:
            logger.info("Fetching CoinDesk RSS...")
            response = await self.session.get(self.rss_feeds['coindesk'])
            response.raise_for_status()
            
            # feedparser로 RSS 파싱
            feed = feedparser.parse(response.text)
            news_list = []
            
            logger.info(f"CoinDesk RSS parsed, found {len(feed.entries)} entries")
            
            for entry in feed.entries[:20]:  # 최근 20개
                try:
                    title = entry.title.strip()
                    url = entry.link
                    description = getattr(entry, 'description', '') or getattr(entry, 'summary', '')
                    
                    # 발행 시간 파싱
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6], tzinfo=pytz.UTC)
                        # KST로 변환
                        published_at = published_at.astimezone(self.kst)
                    
                    # 관련 암호화폐 추출
                    crypto_symbols = self.extract_crypto_symbols(f"{title} {description}")
                    
                    news_data = {
                        'title': title,
                        'url': url,
                        'content': description,
                        'source': 'coindesk',
                        'published_at': published_at,
                        'crypto_symbols': crypto_symbols,
                        'market': 'crypto'
                    }
                    
                    news_list.append(news_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse CoinDesk entry: {e}")
                    continue
                    
            logger.info(f"Collected {len(news_list)} CoinDesk news items")
            return news_list
            
        except Exception as e:
            logger.error(f"Failed to fetch CoinDesk news: {e}")
            return []
    
    async def fetch_cointelegraph_news(self) -> List[Dict]:
        """
        CoinTelegraph RSS 피드에서 뉴스 수집
        
        Returns:
            뉴스 정보 리스트
        """
        try:
            logger.info("Fetching CoinTelegraph RSS...")
            response = await self.session.get(self.rss_feeds['cointelegraph'])
            response.raise_for_status()
            
            # feedparser로 RSS 파싱
            feed = feedparser.parse(response.text)
            news_list = []
            
            logger.info(f"CoinTelegraph RSS parsed, found {len(feed.entries)} entries")
            
            for entry in feed.entries[:20]:  # 최근 20개
                try:
                    title = entry.title.strip()
                    url = entry.link
                    description = getattr(entry, 'description', '') or getattr(entry, 'summary', '')
                    
                    # 발행 시간 파싱
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6], tzinfo=pytz.UTC)
                        # KST로 변환
                        published_at = published_at.astimezone(self.kst)
                    
                    # 관련 암호화폐 추출
                    crypto_symbols = self.extract_crypto_symbols(f"{title} {description}")
                    
                    news_data = {
                        'title': title,
                        'url': url,
                        'content': description,
                        'source': 'cointelegraph',
                        'published_at': published_at,
                        'crypto_symbols': crypto_symbols,
                        'market': 'crypto'
                    }
                    
                    news_list.append(news_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse CoinTelegraph entry: {e}")
                    continue
                    
            logger.info(f"Collected {len(news_list)} CoinTelegraph news items")
            return news_list
            
        except Exception as e:
            logger.error(f"Failed to fetch CoinTelegraph news: {e}")
            return []
    
    def extract_crypto_symbols(self, text: str) -> List[str]:
        """
        텍스트에서 암호화폐 심볼 추출
        
        Args:
            text: 분석할 텍스트 (제목 + 내용)
            
        Returns:
            추출된 암호화폐 심볼 리스트
        """
        text_lower = text.lower()
        found_symbols = set()
        
        # 심볼 매핑에서 검색
        for keyword, symbol in self.crypto_symbols.items():
            if keyword in text_lower:
                found_symbols.add(symbol)
        
        # 직접적인 심볼 패턴 매칭 (대문자 2-5자리)
        symbol_matches = re.findall(r'\b([A-Z]{2,5})\b', text)
        for symbol in symbol_matches:
            if symbol in ['BTC', 'ETH', 'XRP', 'SOL', 'ADA', 'DOGE', 'MATIC', 'LINK', 'DOT', 'AVAX', 'LTC', 'SHIB', 'TRX']:
                found_symbols.add(symbol)
        
        return list(found_symbols)
    
    def calculate_importance_score(self, news_data: Dict) -> float:
        """
        암호화폐 뉴스의 중요도 점수 계산
        
        Args:
            news_data: 뉴스 데이터
            
        Returns:
            중요도 점수 (0.0 ~ 1.0)
        """
        score = 0.5  # 기본 점수
        title_content = f"{news_data.get('title', '')} {news_data.get('content', '')}".lower()
        
        # 중요한 암호화폐 키워드들
        important_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth',
            'regulation', 'sec', 'etf', 'approval',
            'surge', 'rally', 'crash', 'dump',
            'breaking', 'major', 'adoption',
            'partnership', 'launch', 'upgrade',
            'hack', 'security', 'whale',
            'market cap', 'price', 'trading'
        ]
        
        # 키워드 점수
        keyword_count = 0
        for keyword in important_keywords:
            if keyword in title_content:
                keyword_count += 1
        
        score += min(keyword_count * 0.05, 0.3)  # 키워드 당 0.05점, 최대 0.3점
        
        # 주요 코인 관련 뉴스 가중치
        major_coins = ['BTC', 'ETH', 'XRP', 'SOL']
        crypto_symbols = news_data.get('crypto_symbols', [])
        
        for symbol in crypto_symbols:
            if symbol in major_coins:
                score += 0.15
            else:
                score += 0.1
        
        # 소스별 가중치
        source = news_data.get('source', '')
        if source == 'coindesk':
            score += 0.1  # CoinDesk는 권위있는 소스
        elif source == 'cointelegraph':
            score += 0.05
        
        # 제목에 Breaking, Major 등이 있으면 가중치
        title_lower = news_data.get('title', '').lower()
        if any(word in title_lower for word in ['breaking', 'major', 'urgent']):
            score += 0.2
        
        return min(score, 1.0)  # 최대 1.0으로 제한
    
    async def collect_and_store_news(self) -> int:
        """
        암호화폐 뉴스 수집하여 DB에 저장
        
        Returns:
            저장된 뉴스 개수
        """
        all_news = []
        
        # CoinDesk 뉴스 수집
        coindesk_news = await self.fetch_coindesk_news()
        all_news.extend(coindesk_news)
        
        # 요청 간 딜레이
        await asyncio.sleep(2)
        
        # CoinTelegraph 뉴스 수집
        cointelegraph_news = await self.fetch_cointelegraph_news()
        all_news.extend(cointelegraph_news)
        
        logger.info(f"Total collected crypto news: {len(all_news)}")
        
        if not all_news:
            return 0
        
        db = get_db_session()
        new_news_count = 0
        
        try:
            for news_data in all_news:
                # 이미 저장된 뉴스인지 확인 (URL 기준)
                existing = db.query(News).filter(
                    News.url == news_data['url']
                ).first()
                
                if existing:
                    logger.debug(f"News already exists: {news_data['url']}")
                    continue
                
                # 중요도 점수 계산
                importance_score = self.calculate_importance_score(news_data)
                
                # 새 뉴스 저장
                try:
                    news = News(
                        title=news_data['title'],
                        content=news_data.get('content'),
                        url=news_data['url'],
                        source=news_data['source'],
                        published_at=news_data.get('published_at'),
                        stock_codes=news_data.get('crypto_symbols', []),  # crypto symbols을 stock_codes 필드에 저장
                        importance_score=importance_score
                    )
                    
                    # market 필드가 있으면 설정 (DB 스키마에 따라)
                    if hasattr(news, 'market'):
                        news.market = news_data['market']
                    
                    db.add(news)
                    new_news_count += 1
                    
                    logger.info(f"New crypto news: {news.title[:50]}... (symbols: {news_data.get('crypto_symbols', [])})")
                    
                except Exception as e:
                    logger.warning(f"Failed to save news item, trying without market field: {e}")
                    # market 필드 없이 다시 시도
                    news = News(
                        title=news_data['title'],
                        content=news_data.get('content'),
                        url=news_data['url'],
                        source=news_data['source'],
                        published_at=news_data.get('published_at'),
                        stock_codes=news_data.get('crypto_symbols', []),
                        importance_score=importance_score
                    )
                    db.add(news)
                    new_news_count += 1
                    logger.info(f"New crypto news (fallback): {news.title[:50]}...")
            
            db.commit()
            logger.info(f"Successfully saved {new_news_count} new crypto news items")
            
            # 수집된 뉴스 자동 번역 실행
            if new_news_count > 0:
                try:
                    from ..services.translator import translate_news_batch
                    translated_count = await translate_news_batch(market='crypto', limit=new_news_count)
                    logger.info(f"Auto-translated {translated_count} crypto news items")
                except Exception as e:
                    logger.warning(f"Auto-translation failed: {e}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to store crypto news: {e}")
            
        finally:
            db.close()
            
        return new_news_count

# Helper function for manual testing
async def test_crypto_news_collector():
    """암호화폐 뉴스 수집기 테스트"""
    async with CryptoNewsCollector() as collector:
        # CoinDesk 뉴스 테스트
        coindesk_news = await collector.fetch_coindesk_news()
        logger.info(f"Found {len(coindesk_news)} CoinDesk news items")
        
        for news in coindesk_news[:3]:  # Show first 3
            logger.info(f"- {news['title'][:60]}... (symbols: {news.get('crypto_symbols', [])})")
        
        # CoinTelegraph 뉴스 테스트
        await asyncio.sleep(2)
        cointelegraph_news = await collector.fetch_cointelegraph_news()
        logger.info(f"Found {len(cointelegraph_news)} CoinTelegraph news items")
        
        for news in cointelegraph_news[:3]:
            logger.info(f"- {news['title'][:60]}... (symbols: {news.get('crypto_symbols', [])})")

# Test function for collection and storage
async def test_crypto_news_collection():
    """암호화폐 뉴스 수집 테스트"""
    async with CryptoNewsCollector() as collector:
        new_articles = await collector.collect_and_store_news()
        logger.info(f"Test completed: {new_articles} new articles")
        return new_articles

if __name__ == "__main__":
    # Test run
    asyncio.run(test_crypto_news_collector())