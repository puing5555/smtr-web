"""
Daily briefing and market summary generator
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz
from loguru import logger
from sqlalchemy.orm import Session

from ..db.database import get_db_session
from ..db.models import DartFiling, News, PriceAlert, Stock
from .telegram_bot import telegram_bot

class BriefingGenerator:
    """일일 브리핑 및 요약 생성기"""
    
    def __init__(self):
        self.kst = pytz.timezone('Asia/Seoul')
    
    async def generate_morning_briefing(self) -> str:
        """
        아침 브리핑 생성
        
        Returns:
            브리핑 텍스트
        """
        db = get_db_session()
        
        try:
            current_time = datetime.now(self.kst)
            yesterday = current_time - timedelta(days=1)
            yesterday_str = yesterday.strftime('%Y%m%d')
            
            briefing_parts = []
            
            # 1. 인사말
            briefing_parts.append(self._get_greeting())
            
            # 2. 어제 주요 공시 (최대 5개)
            dart_summary = self._get_dart_summary(db, yesterday_str)
            if dart_summary:
                briefing_parts.append(f"📋 <b>주요 공시</b>\n{dart_summary}")
            
            # 3. 급등락 종목 (어제 장 마감 후)
            price_alerts_summary = self._get_price_alerts_summary(db, yesterday)
            if price_alerts_summary:
                briefing_parts.append(f"📊 <b>급등락 종목</b>\n{price_alerts_summary}")
            
            # 4. 주요 뉴스 (향후 구현)
            news_summary = self._get_news_summary(db, yesterday)
            if news_summary:
                briefing_parts.append(f"📰 <b>주요 뉴스</b>\n{news_summary}")
            
            # 5. 마무리
            briefing_parts.append(self._get_closing_message())
            
            return "\n\n".join(briefing_parts)
            
        except Exception as e:
            logger.error(f"Failed to generate morning briefing: {e}")
            return "❌ 브리핑 생성 중 오류가 발생했습니다."
            
        finally:
            db.close()
    
    async def generate_market_close_summary(self) -> str:
        """
        장 마감 요약 생성
        
        Returns:
            요약 텍스트
        """
        db = get_db_session()
        
        try:
            current_time = datetime.now(self.kst)
            today_str = current_time.strftime('%Y%m%d')
            
            summary_parts = []
            
            # 1. 마감 인사
            summary_parts.append("📊 오늘 하루 수고하셨습니다!")
            
            # 2. 오늘 공시 요약
            dart_summary = self._get_dart_summary(db, today_str)
            if dart_summary:
                summary_parts.append(f"📋 <b>오늘의 공시</b>\n{dart_summary}")
            
            # 3. 급등락 종목
            today_start = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
            price_alerts_summary = self._get_price_alerts_summary(db, today_start)
            if price_alerts_summary:
                summary_parts.append(f"🎯 <b>오늘의 급등락</b>\n{price_alerts_summary}")
            
            # 4. 내일 주목할 점
            tomorrow_preview = self._get_tomorrow_preview()
            if tomorrow_preview:
                summary_parts.append(f"🔮 <b>내일 주목할 점</b>\n{tomorrow_preview}")
            
            return "\n\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Failed to generate market close summary: {e}")
            return "❌ 마감 요약 생성 중 오류가 발생했습니다."
            
        finally:
            db.close()
    
    def _get_greeting(self) -> str:
        """아침 인사말"""
        current_hour = datetime.now(self.kst).hour
        
        if current_hour < 12:
            return "☀️ 좋은 아침입니다! 오늘의 투자 브리핑을 시작합니다."
        elif current_hour < 18:
            return "🌞 안녕하세요! 투자 브리핑을 전해드립니다."
        else:
            return "🌙 안녕하세요! 늦은 브리핑을 전해드립니다."
    
    def _get_dart_summary(self, db: Session, date_str: str, limit: int = 5) -> Optional[str]:
        """DART 공시 요약"""
        try:
            filings = db.query(DartFiling).filter(
                DartFiling.rcept_dt == date_str
            ).order_by(DartFiling.created_at.desc()).limit(limit).all()
            
            if not filings:
                return None
                
            summary_lines = []
            for filing in filings:
                line = f"• <b>{filing.corp_name}</b>: {filing.report_nm}"
                summary_lines.append(line)
                
            return "\n".join(summary_lines)
            
        except Exception as e:
            logger.error(f"Failed to get DART summary: {e}")
            return None
    
    def _get_price_alerts_summary(self, db: Session, since_time: datetime, limit: int = 10) -> Optional[str]:
        """급등락 종목 요약"""
        try:
            alerts = db.query(PriceAlert, Stock).join(
                Stock, PriceAlert.stock_id == Stock.id
            ).filter(
                PriceAlert.created_at >= since_time
            ).order_by(
                PriceAlert.price_change.desc()
            ).limit(limit).all()
            
            if not alerts:
                return None
                
            summary_lines = []
            for alert, stock in alerts:
                direction = "📈" if alert.price_change > 0 else "📉"
                line = f"• {direction} <b>{stock.name}</b>: {alert.price_change:+.2f}%"
                summary_lines.append(line)
                
            return "\n".join(summary_lines)
            
        except Exception as e:
            logger.error(f"Failed to get price alerts summary: {e}")
            return None
    
    def _get_news_summary(self, db: Session, since_time: datetime, limit: int = 3) -> Optional[str]:
        """뉴스 요약 (향후 구현)"""
        try:
            # 향후 뉴스 수집이 구현되면 활성화
            news_items = db.query(News).filter(
                News.created_at >= since_time,
                News.importance_score >= 0.7  # 중요도 높은 뉴스만
            ).order_by(
                News.importance_score.desc()
            ).limit(limit).all()
            
            if not news_items:
                return None
                
            summary_lines = []
            for news in news_items:
                line = f"• <b>{news.title}</b>"
                if news.source:
                    line += f" ({news.source})"
                summary_lines.append(line)
                
            return "\n".join(summary_lines)
            
        except Exception as e:
            logger.error(f"Failed to get news summary: {e}")
            return None
    
    def _get_closing_message(self) -> str:
        """마무리 메시지"""
        messages = [
            "📈 현명한 투자 되시길 바랍니다!",
            "💪 오늘도 성공적인 투자 하세요!",
            "🎯 좋은 기회를 찾아보세요!",
            "⚡ 신중하게 투자 결정하세요!",
            "🚀 좋은 하루 되세요!"
        ]
        
        import random
        return random.choice(messages)
    
    def _get_tomorrow_preview(self) -> Optional[str]:
        """내일 주목사항 (정적 메시지, 향후 확장 가능)"""
        current_time = datetime.now(self.kst)
        weekday = current_time.weekday()
        
        # 주말 체크
        if weekday == 4:  # 금요일
            return "• 주말 동안 해외 증시 동향 주의\n• 월요일 개장 전 뉴스 체크 필요"
        elif weekday == 6:  # 일요일
            return "• 내일(월요일) 개장 준비\n• 해외 증시 영향 분석"
        else:
            return "• 장 시작 전 주요 뉴스 확인\n• 관심 종목 모니터링"

    async def send_morning_briefing(self, chat_id: Optional[str] = None) -> bool:
        """아침 브리핑 전송"""
        try:
            briefing_content = await self.generate_morning_briefing()
            return await telegram_bot.send_morning_briefing(briefing_content, chat_id)
        except Exception as e:
            logger.error(f"Failed to send morning briefing: {e}")
            return False
    
    async def send_market_close_summary(self, chat_id: Optional[str] = None) -> bool:
        """마감 요약 전송"""
        try:
            summary_content = await self.generate_market_close_summary()
            return await telegram_bot.send_market_close_summary(summary_content, chat_id)
        except Exception as e:
            logger.error(f"Failed to send market close summary: {e}")
            return False

# 글로벌 브리핑 생성기 인스턴스
briefing_generator = BriefingGenerator()

# Helper functions
async def test_morning_briefing():
    """아침 브리핑 테스트"""
    content = await briefing_generator.generate_morning_briefing()
    logger.info("Morning briefing generated:")
    logger.info(content)
    return content

async def test_market_close_summary():
    """마감 요약 테스트"""
    content = await briefing_generator.generate_market_close_summary()
    logger.info("Market close summary generated:")
    logger.info(content)
    return content

if __name__ == "__main__":
    import asyncio
    
    async def main():
        await test_morning_briefing()
        await test_market_close_summary()
    
    asyncio.run(main())