"""
Stock price monitoring and alert system
주가 급등락 감지 모듈
"""
import httpx
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from loguru import logger
import pytz
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..db.database import get_db_session
from ..db.models import Stock, PriceAlert
from ..alerts.telegram_bot import telegram_bot

class PriceMonitor:
    """주가 모니터링 및 급등락 감지"""
    
    def __init__(self):
        self.session = None
        self.threshold = settings.PRICE_ALERT_THRESHOLD  # ±3%
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def get_stock_price(self, symbol: str) -> Optional[Dict]:
        """
        종목 현재가 조회 (향후 실제 API 연동 필요)
        
        Args:
            symbol: 종목코드
            
        Returns:
            가격 정보
        """
        # TODO: 실제 주가 API (KRX, 네이버, 다음 등) 연동 필요
        # 현재는 더미 데이터 반환
        
        logger.debug(f"Getting price for {symbol}")
        
        # 더미 데이터 (실제 구현 시 삭제)
        import random
        base_price = random.randint(1000, 50000)
        change = random.uniform(-10, 10)
        
        return {
            'symbol': symbol,
            'current_price': base_price,
            'previous_price': int(base_price * (1 - change/100)),
            'change_percent': change,
            'volume': random.randint(10000, 1000000),
            'timestamp': datetime.now(pytz.timezone('Asia/Seoul'))
        }
    
    async def monitor_stock_prices(self, symbols: List[str]) -> List[Dict]:
        """
        여러 종목 가격 모니터링
        
        Args:
            symbols: 종목코드 리스트
            
        Returns:
            급등락 감지된 종목들
        """
        alerts = []
        
        for symbol in symbols:
            try:
                price_data = await self.get_stock_price(symbol)
                if not price_data:
                    continue
                    
                change_percent = price_data['change_percent']
                
                # 급등락 임계값 체크
                if abs(change_percent) >= self.threshold:
                    alerts.append(price_data)
                    logger.info(f"Price alert triggered: {symbol} {change_percent:+.2f}%")
                    
            except Exception as e:
                logger.error(f"Failed to monitor {symbol}: {e}")
                
        return alerts
    
    async def store_price_alert(self, stock_symbol: str, price_data: Dict) -> bool:
        """
        급등락 알림을 DB에 저장
        
        Args:
            stock_symbol: 종목코드
            price_data: 가격 데이터
            
        Returns:
            저장 성공 여부
        """
        db = get_db_session()
        
        try:
            # 종목 정보 조회
            stock = db.query(Stock).filter(Stock.symbol == stock_symbol).first()
            
            if not stock:
                logger.warning(f"Stock not found: {stock_symbol}")
                return False
            
            # 급등락 유형 결정
            change_percent = price_data['change_percent']
            alert_type = "SURGE" if change_percent > 0 else "PLUNGE"
            
            # 급등락 알림 저장
            price_alert = PriceAlert(
                stock_id=stock.id,
                alert_type=alert_type,
                price_change=change_percent,
                previous_price=price_data['previous_price'],
                current_price=price_data['current_price'],
                volume=price_data.get('volume', 0)
            )
            
            db.add(price_alert)
            db.commit()
            
            logger.info(f"Price alert stored: {stock.name} {change_percent:+.2f}%")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store price alert: {e}")
            db.rollback()
            return False
            
        finally:
            db.close()
    
    async def send_price_alerts(self, price_alerts: List[Dict]) -> int:
        """
        급등락 알림 전송
        
        Args:
            price_alerts: 급등락 데이터 리스트
            
        Returns:
            전송된 알림 수
        """
        sent_count = 0
        
        for alert_data in price_alerts:
            try:
                # DB에 저장
                await self.store_price_alert(alert_data['symbol'], alert_data)
                
                # 종목 정보 구성
                stock_info = {
                    'symbol': alert_data['symbol'],
                    'name': alert_data.get('name', alert_data['symbol']),  # 종목명이 없으면 코드 사용
                    'current_price': alert_data['current_price'],
                    'previous_price': alert_data['previous_price'],
                    'volume': alert_data.get('volume', 0)
                }
                
                # 텔레그램 알림 전송
                success = await telegram_bot.send_price_alert(
                    stock_info, 
                    alert_data['change_percent']
                )
                
                if success:
                    sent_count += 1
                    logger.info(f"Price alert sent: {stock_info['name']}")
                    
            except Exception as e:
                logger.error(f"Failed to send price alert: {e}")
        
        return sent_count
    
    def get_watchlist_symbols(self) -> List[str]:
        """
        감시 대상 종목 코드 조회
        
        Returns:
            종목코드 리스트
        """
        db = get_db_session()
        
        try:
            # 등록된 모든 종목 조회 (향후 관심종목 필터링 가능)
            stocks = db.query(Stock).all()
            return [stock.symbol for stock in stocks]
            
        except Exception as e:
            logger.error(f"Failed to get watchlist: {e}")
            return []
            
        finally:
            db.close()
    
    async def run_price_monitoring(self) -> int:
        """
        가격 모니터링 실행
        
        Returns:
            전송된 알림 수
        """
        logger.info("Starting price monitoring")
        
        try:
            # 감시 대상 종목 조회
            symbols = self.get_watchlist_symbols()
            
            if not symbols:
                logger.info("No symbols to monitor")
                return 0
            
            logger.info(f"Monitoring {len(symbols)} symbols")
            
            # 가격 모니터링
            price_alerts = await self.monitor_stock_prices(symbols)
            
            if not price_alerts:
                logger.info("No price alerts triggered")
                return 0
            
            # 알림 전송
            sent_count = await self.send_price_alerts(price_alerts)
            
            logger.info(f"Price monitoring completed: {sent_count} alerts sent")
            return sent_count
            
        except Exception as e:
            logger.error(f"Price monitoring failed: {e}")
            return 0

# API 연동 예시 (향후 구현)
class KoreanStockAPI:
    """한국 주식 API 연동 (예시)"""
    
    @staticmethod
    async def get_kospi_kosdaq_prices(symbols: List[str]) -> Dict[str, Dict]:
        """
        KOSPI/KOSDAQ 종목 가격 조회 (예시)
        
        실제로는 다음과 같은 API들을 사용할 수 있습니다:
        - KRX API
        - 한국투자증권 API
        - 네이버/다음 파이낸스 크롤링
        - Alpha Vantage (일부 한국 주식 지원)
        """
        # TODO: 실제 API 구현
        pass
    
    @staticmethod  
    async def get_real_time_prices(symbols: List[str]) -> Dict[str, Dict]:
        """실시간 가격 조회 (예시)"""
        # TODO: 웹소켓 또는 실시간 API 구현
        pass

# Sample stock data for testing
SAMPLE_STOCKS = [
    {"symbol": "005930", "name": "삼성전자", "market": "KOSPI"},
    {"symbol": "000660", "name": "SK하이닉스", "market": "KOSPI"}, 
    {"symbol": "035420", "name": "NAVER", "market": "KOSPI"},
    {"symbol": "051910", "name": "LG화학", "market": "KOSPI"},
    {"symbol": "006400", "name": "삼성SDI", "market": "KOSPI"},
]

async def initialize_sample_stocks():
    """샘플 종목 데이터 초기화"""
    db = get_db_session()
    
    try:
        for stock_data in SAMPLE_STOCKS:
            existing = db.query(Stock).filter(Stock.symbol == stock_data["symbol"]).first()
            
            if not existing:
                stock = Stock(
                    symbol=stock_data["symbol"],
                    name=stock_data["name"],
                    market=stock_data["market"],
                    sector="기타"
                )
                db.add(stock)
                logger.info(f"Added sample stock: {stock.name}")
        
        db.commit()
        logger.info("Sample stocks initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize sample stocks: {e}")
        db.rollback()
        
    finally:
        db.close()

# Helper function for testing
async def test_price_monitor():
    """가격 모니터 테스트"""
    # 샘플 종목 초기화
    await initialize_sample_stocks()
    
    async with PriceMonitor() as monitor:
        alerts_sent = await monitor.run_price_monitoring()
        logger.info(f"Test completed: {alerts_sent} alerts sent")

if __name__ == "__main__":
    # Test run
    asyncio.run(test_price_monitor())