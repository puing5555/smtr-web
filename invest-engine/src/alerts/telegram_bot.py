"""
Telegram Bot for investment alerts
"""
import asyncio
from typing import List, Dict, Optional
from telegram import Bot
from telegram.error import TelegramError
from loguru import logger
from datetime import datetime
import pytz

from ..config.settings import settings
from ..db.database import get_db_session
from ..db.models import AlertsLog

class InvestmentTelegramBot:
    """투자 알림 텔레그램 봇"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.default_chat_id = settings.TELEGRAM_CHAT_ID
        self.bot = None
        
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
    
    async def send_message(self, message: str, chat_id: Optional[str] = None, parse_mode: str = "HTML") -> bool:
        """
        메시지 전송
        
        Args:
            message: 전송할 메시지
            chat_id: 채팅 ID (없으면 기본 설정 사용)
            parse_mode: 파싱 모드 (HTML, Markdown)
            
        Returns:
            전송 성공 여부
        """
        if not self.bot:
            logger.warning("Telegram bot not configured")
            return False
            
        target_chat_id = chat_id or self.default_chat_id
        if not target_chat_id:
            logger.error("No chat ID provided")
            return False
            
        try:
            await self.bot.send_message(
                chat_id=target_chat_id,
                text=message,
                parse_mode=parse_mode
            )
            
            # 로그에 기록
            self._log_alert("MESSAGE", "General Message", message, target_chat_id, "sent")
            
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            self._log_alert("MESSAGE", "General Message", message, target_chat_id, "failed")
            return False
    
    async def send_dart_alert(self, filing: Dict, analysis_result: Optional[Dict] = None, chat_id: Optional[str] = None) -> bool:
        """
        DART 공시 알림 전송 (AI 분석 결과 포함)
        
        Args:
            filing: 공시 정보
            analysis_result: AI 분석 결과 (선택적)
            chat_id: 채팅 ID
            
        Returns:
            전송 성공 여부
        """
        # 등급별로 다른 포맷 사용
        grade = filing.get('grade', 'C')
        
        if grade == 'A' and analysis_result:
            message = self._format_grade_a_message(filing, analysis_result)
        elif grade == 'B' and analysis_result:
            message = self._format_grade_b_message(filing, analysis_result)
        else:
            message = self._format_dart_message(filing)  # 기본 포맷
        
        success = await self.send_message(message, chat_id)
        
        if success:
            self._log_alert(
                "DART", 
                f"DART Alert ({grade}): {filing.get('corp_name')}", 
                message, 
                chat_id or self.default_chat_id, 
                "sent"
            )
            
        return success
    
    async def send_price_alert(self, stock_info: Dict, price_change: float, chat_id: Optional[str] = None) -> bool:
        """
        급등락 알림 전송
        
        Args:
            stock_info: 종목 정보
            price_change: 가격 변동률 (%)
            chat_id: 채팅 ID
            
        Returns:
            전송 성공 여부
        """
        message = self._format_price_alert_message(stock_info, price_change)
        success = await self.send_message(message, chat_id)
        
        if success:
            self._log_alert(
                "PRICE", 
                f"Price Alert: {stock_info.get('name')}", 
                message, 
                chat_id or self.default_chat_id, 
                "sent"
            )
            
        return success
    
    async def send_morning_briefing(self, briefing_content: str, chat_id: Optional[str] = None) -> bool:
        """
        아침 브리핑 전송
        
        Args:
            briefing_content: 브리핑 내용
            chat_id: 채팅 ID
            
        Returns:
            전송 성공 여부
        """
        kst = pytz.timezone('Asia/Seoul')
        current_time = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
        
        message = f"🌅 <b>투자 아침 브리핑</b> ({current_time})\n\n{briefing_content}"
        success = await self.send_message(message, chat_id)
        
        if success:
            self._log_alert(
                "BRIEFING", 
                "Morning Briefing", 
                message, 
                chat_id or self.default_chat_id, 
                "sent"
            )
            
        return success
    
    async def send_market_close_summary(self, summary_content: str, chat_id: Optional[str] = None) -> bool:
        """
        마감 요약 전송
        
        Args:
            summary_content: 요약 내용
            chat_id: 채팅 ID
            
        Returns:
            전송 성공 여부
        """
        kst = pytz.timezone('Asia/Seoul')
        current_time = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
        
        message = f"📊 <b>장 마감 요약</b> ({current_time})\n\n{summary_content}"
        success = await self.send_message(message, chat_id)
        
        if success:
            self._log_alert(
                "SUMMARY", 
                "Market Close Summary", 
                message, 
                chat_id or self.default_chat_id, 
                "sent"
            )
            
        return success
    
    def _format_dart_message(self, filing: Dict) -> str:
        """
        DART 공시 메시지 포맷팅
        
        Args:
            filing: 공시 정보
            
        Returns:
            포맷된 메시지
        """
        corp_name = filing.get('corp_name', 'Unknown')
        report_name = filing.get('report_nm', 'Unknown')
        rcept_dt = filing.get('rcept_dt', '')
        stock_code = filing.get('stock_code', '')
        
        # 날짜 포맷팅 (YYYYMMDD -> YYYY-MM-DD)
        formatted_date = f"{rcept_dt[:4]}-{rcept_dt[4:6]}-{rcept_dt[6:8]}" if len(rcept_dt) == 8 else rcept_dt
        
        message = f"📋 <b>DART 공시 알림</b>\n\n"
        message += f"<b>회사:</b> {corp_name}\n"
        
        if stock_code:
            message += f"<b>종목코드:</b> {stock_code}\n"
            
        message += f"<b>공시명:</b> {report_name}\n"
        message += f"<b>접수일:</b> {formatted_date}\n"
        
        # DART 링크 (실제로는 접수번호로 상세 조회 가능)
        rcept_no = filing.get('rcept_no', '')
        if rcept_no:
            message += f"\n<a href='http://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}'>📄 상세보기</a>"
            
        return message
    
    def _format_grade_a_message(self, filing: Dict, analysis: Dict) -> str:
        """
        A등급 공시 메시지 포맷팅 (정기공시 - 실적 중심)
        
        Args:
            filing: 공시 정보
            analysis: AI 분석 결과
            
        Returns:
            포맷된 메시지
        """
        corp_name = filing.get('corp_name', 'Unknown')
        report_name = filing.get('report_nm', 'Unknown')
        rcept_dt = filing.get('rcept_dt', '')
        rcept_no = filing.get('rcept_no', '')
        
        # 날짜에서 기간 추출 (간단히 연도 사용)
        period = rcept_dt[:4] if len(rcept_dt) >= 4 else '정보 없음'
        
        # 메시지 구성
        message = f"📊 <b>[실적] {corp_name} {report_name}</b> ({period})\n\n"
        
        # 재무 정보
        message += f"매출: {analysis.get('revenue', '정보 없음')}"
        if analysis.get('revenue_prev') != '정보 없음':
            message += f" (전년 {analysis.get('revenue_prev')}, {analysis.get('revenue_change', '정보 없음')})"
        message += "\n"
        
        message += f"영업익: {analysis.get('operating_profit', '정보 없음')}"
        if analysis.get('operating_profit_prev') != '정보 없음':
            message += f" (전년 {analysis.get('operating_profit_prev')}, {analysis.get('operating_profit_change', '정보 없음')})"
        message += "\n"
        
        message += f"순이익: {analysis.get('net_profit', '정보 없음')}"
        if analysis.get('net_profit_prev') != '정보 없음':
            message += f" (전년 {analysis.get('net_profit_prev')}, {analysis.get('net_profit_change', '정보 없음')})"
        message += "\n\n"
        
        # AI 한줄평
        summary = analysis.get('summary', '분석 결과 없음')
        message += f"⚡ {summary}\n"
        
        # DART 링크
        if rcept_no:
            message += f"🔗 <a href='http://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}'>DART 상세보기</a>"
        
        return message
    
    def _format_grade_b_message(self, filing: Dict, analysis: Dict) -> str:
        """
        B등급 공시 메시지 포맷팅 (중요 비정기공시)
        
        Args:
            filing: 공시 정보
            analysis: AI 분석 결과
            
        Returns:
            포맷된 메시지
        """
        corp_name = filing.get('corp_name', 'Unknown')
        report_name = filing.get('report_nm', 'Unknown')
        rcept_no = filing.get('rcept_no', '')
        
        # 공시 유형 간단화
        filing_type = self._extract_filing_type(report_name)
        
        # 메시지 구성
        message = f"🔔 <b>[{filing_type}] {corp_name}</b>\n"
        
        # AI 핵심 요약 
        summary = analysis.get('summary', '요약 정보 없음')
        message += f"{summary}\n\n"
        
        # 주요 포인트 (있는 경우만)
        key_points = analysis.get('key_points', '')
        if key_points and key_points != '• 분석 실패':
            message += f"{key_points}\n\n"
        
        # 투자 포인트
        investment_impact = analysis.get('investment_impact', '분석 불가')
        message += f"💡 <b>투자 포인트:</b> {investment_impact}\n"
        
        # DART 링크
        if rcept_no:
            message += f"🔗 <a href='http://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}'>DART 상세보기</a>"
        
        return message
    
    def _extract_filing_type(self, report_name: str) -> str:
        """
        공시명에서 유형 추출
        
        Args:
            report_name: 공시명
            
        Returns:
            간략한 공시 유형
        """
        type_mapping = {
            '자기주식': '자기주식',
            '유상증자': '유상증자',
            '무상증자': '무상증자',
            '임원변경': '임원변경',
            '최대주주': '지분변동',
            '합병': '합병',
            '분할': '분할',
            'CB': '전환사채',
            'BW': '신주인수권',
            '전환사채': '전환사채',
            '주요사항보고': '주요사항',
            '중요한계약': '중요계약'
        }
        
        for keyword, type_name in type_mapping.items():
            if keyword in report_name:
                return type_name
        
        return '기타공시'
    
    def _format_price_alert_message(self, stock_info: Dict, price_change: float) -> str:
        """
        가격 알림 메시지 포맷팅
        
        Args:
            stock_info: 종목 정보
            price_change: 가격 변동률
            
        Returns:
            포맷된 메시지
        """
        name = stock_info.get('name', 'Unknown')
        symbol = stock_info.get('symbol', '')
        current_price = stock_info.get('current_price', 0)
        previous_price = stock_info.get('previous_price', 0)
        volume = stock_info.get('volume', 0)
        
        direction = "📈 급등" if price_change > 0 else "📉 급락"
        emoji = "🔴" if price_change > 0 else "🔵"
        
        message = f"{direction} <b>가격 알림</b>\n\n"
        message += f"<b>종목:</b> {name}"
        
        if symbol:
            message += f" ({symbol})"
            
        message += f"\n<b>변동률:</b> {emoji} {price_change:+.2f}%\n"
        message += f"<b>현재가:</b> {current_price:,}원\n"
        message += f"<b>전일가:</b> {previous_price:,}원\n"
        
        if volume:
            message += f"<b>거래량:</b> {volume:,}주\n"
            
        return message
    
    def _log_alert(self, alert_type: str, title: str, message: str, recipient: str, status: str):
        """
        알림 로그 기록
        
        Args:
            alert_type: 알림 타입
            title: 제목
            message: 메시지
            recipient: 수신자
            status: 상태
        """
        db = get_db_session()
        try:
            alert_log = AlertsLog(
                alert_type=alert_type,
                title=title,
                message=message,
                recipient=recipient,
                status=status
            )
            db.add(alert_log)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
            db.rollback()
        finally:
            db.close()

# 글로벌 봇 인스턴스
telegram_bot = InvestmentTelegramBot()

# Helper functions
async def send_test_message(message: str = "🤖 Investment Engine Test Message"):
    """테스트 메시지 전송"""
    return await telegram_bot.send_message(message)

async def test_telegram_bot():
    """텔레그램 봇 테스트"""
    success = await send_test_message("🚀 Investment Engine Started!")
    logger.info(f"Test message sent: {'Success' if success else 'Failed'}")

if __name__ == "__main__":
    # Test run
    asyncio.run(test_telegram_bot())