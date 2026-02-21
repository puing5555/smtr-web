"""
Telegram Alert System for High-Priority News and Disclosures
중요도 0.7 이상인 공시/뉴스 자동 알림 시스템
"""
import asyncio
from typing import List, Dict, Optional
from telegram import Bot
from telegram.error import TelegramError
from loguru import logger
from datetime import datetime, timedelta
import pytz
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..db.database import get_db_session
from ..db.models import News, DartFiling, AlertsLog

class TelegramAlert:
    """텔레그램 알림 시스템"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.bot = None
        self.kst = pytz.timezone('Asia/Seoul')
        
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
    
    def is_configured(self) -> bool:
        """알림 설정 여부 확인"""
        return bool(self.bot_token and self.chat_id)
    
    async def send_alert(self, message: str, content_type: str = "general", 
                        content_id: Optional[int] = None, stock_code: Optional[str] = None) -> bool:
        """
        텔레그램 알림 전송
        
        Args:
            message: 전송할 메시지
            content_type: 컨텐츠 타입 (news, filing, general)
            content_id: 컨텐츠 ID
            stock_code: 관련 종목코드
            
        Returns:
            전송 성공 여부
        """
        if not self.is_configured():
            logger.warning("Telegram not configured - skipping alert")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=False
            )
            
            # 발송 이력 저장
            self._log_alert_sent(content_type, message, stock_code, content_id)
            
            logger.info(f"Telegram alert sent: {content_type}")
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            self._log_alert_failed(content_type, message, stock_code, content_id, str(e))
            return False
    
    def format_news_alert(self, news: Dict) -> str:
        """
        뉴스 알림 메시지 포맷팅
        
        Args:
            news: 뉴스 데이터
            
        Returns:
            포맷된 메시지
        """
        title = news.get('title', '제목 없음')
        source = news.get('source', 'Unknown')
        url = news.get('url', '')
        importance_score = news.get('importance_score', 0.0)
        stock_codes = news.get('stock_codes', [])
        
        # 소스 표시명 매핑
        source_display_map = {
            'naver_finance': '네이버증권',
            'naver_finance_연합뉴스': '연합뉴스',
            'naver_finance_뉴스1': '뉴스1',
            'naver_finance_매일경제': '매경',
            'naver_finance_한국경제': '한경',
            'naver_finance_서울경제': '서울경제',
            'naver_finance_이데일리': '이데일리'
        }
        source_display = source_display_map.get(source, source)
        
        # 중요도 뱃지 생성
        importance_badge = self._get_importance_badge(importance_score)
        
        # 관련 종목 표시
        stock_info = ""
        if stock_codes:
            stock_info = f" | 관련종목: {', '.join(stock_codes[:3])}"
        
        message = f"📰 <b>[뉴스 알림]</b> {title}\n\n"
        message += f"📊 중요도: {importance_badge}\n"
        message += f"📅 출처: {source_display}{stock_info}\n"
        
        if url:
            message += f"🔗 <a href='{url}'>기사 보기</a>"
        
        return message
    
    def format_filing_alert(self, filing: Dict) -> str:
        """
        공시 알림 메시지 포맷팅
        
        Args:
            filing: 공시 데이터
            
        Returns:
            포맷된 메시지
        """
        corp_name = filing.get('corp_name', '회사명 미상')
        report_name = filing.get('report_nm', '공시명 미상')
        grade = filing.get('grade', 'C')
        rcept_no = filing.get('rcept_no', '')
        stock_code = filing.get('stock_code', '')
        rcept_dt = filing.get('rcept_dt', '')
        
        # 공시 타입별 이모지
        if grade == 'A':
            emoji = "📊"
            grade_text = "[실적공시]"
        elif grade == 'B':
            emoji = "🚨"
            grade_text = "[긴급공시]"
        else:
            emoji = "📋"
            grade_text = "[일반공시]"
        
        # 날짜 포맷팅
        formatted_date = ""
        if rcept_dt and len(rcept_dt) == 8:
            formatted_date = f"{rcept_dt[:4]}-{rcept_dt[4:6]}-{rcept_dt[6:8]}"
        
        message = f"{emoji} <b>{grade_text} {corp_name}</b>\n"
        message += f"{report_name}\n\n"
        
        if stock_code:
            message += f"📈 종목코드: {stock_code}\n"
        
        if formatted_date:
            message += f"📅 접수일: {formatted_date}\n"
        
        # 중요도 뱃지 (공시는 grade 기반)
        if grade == 'A':
            importance_badge = "⭐⭐⭐⭐⭐"
        elif grade == 'B':
            importance_badge = "⭐⭐⭐⭐"
        else:
            importance_badge = "⭐⭐⭐"
        
        message += f"📊 중요도: {importance_badge}\n"
        
        # DART 링크
        if rcept_no:
            dart_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"
            message += f"🔗 <a href='{dart_url}'>공시 상세보기</a>"
        
        return message
    
    def _get_importance_badge(self, score: float) -> str:
        """
        중요도 점수를 별 뱃지로 변환
        
        Args:
            score: 중요도 점수 (0.0 ~ 1.0)
            
        Returns:
            별 뱃지 문자열
        """
        if score >= 0.9:
            return "⭐⭐⭐⭐⭐"  # 5성급
        elif score >= 0.8:
            return "⭐⭐⭐⭐"    # 4성급
        elif score >= 0.7:
            return "⭐⭐⭐"      # 3성급
        elif score >= 0.6:
            return "⭐⭐"        # 2성급
        else:
            return "⭐"          # 1성급
    
    def _log_alert_sent(self, content_type: str, message: str, stock_code: Optional[str] = None, 
                       content_id: Optional[int] = None):
        """발송 성공 이력 저장"""
        try:
            db = get_db_session()
            
            # 제목 추출 (메시지의 첫 번째 줄에서)
            title_lines = message.split('\n')
            title = title_lines[0].replace('<b>', '').replace('</b>', '') if title_lines else 'Telegram Alert'
            
            alert_log = AlertsLog(
                alert_type="TELEGRAM",
                stock_code=stock_code,
                title=title[:200],  # 길이 제한
                message=message,
                channel="telegram",
                recipient=self.chat_id,
                status="sent"
            )
            
            db.add(alert_log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
        finally:
            db.close()
    
    def _log_alert_failed(self, content_type: str, message: str, stock_code: Optional[str] = None,
                         content_id: Optional[int] = None, error: str = ""):
        """발송 실패 이력 저장"""
        try:
            db = get_db_session()
            
            title_lines = message.split('\n')
            title = title_lines[0].replace('<b>', '').replace('</b>', '') if title_lines else 'Telegram Alert'
            
            alert_log = AlertsLog(
                alert_type="TELEGRAM",
                stock_code=stock_code,
                title=f"[FAILED] {title}"[:200],
                message=f"{message}\n\nError: {error}",
                channel="telegram",
                recipient=self.chat_id,
                status="failed"
            )
            
            db.add(alert_log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log failed alert: {e}")
        finally:
            db.close()
    
    def has_been_sent(self, content_type: str, content_id: int, hours_back: int = 24) -> bool:
        """
        최근에 동일한 컨텐츠에 대한 알림을 보냈는지 확인 (중복 방지)
        
        Args:
            content_type: 컨텐츠 타입 (news, filing)
            content_id: 컨텐츠 ID
            hours_back: 확인할 시간 범위 (시간)
            
        Returns:
            이미 발송했으면 True
        """
        try:
            db = get_db_session()
            
            # 최근 N시간 내에 동일한 컨텐츠로 발송된 알림이 있는지 확인
            cutoff_time = datetime.now(self.kst) - timedelta(hours=hours_back)
            
            existing = db.query(AlertsLog).filter(
                AlertsLog.alert_type == "TELEGRAM",
                AlertsLog.title.contains(str(content_id)),  # ID가 포함된 제목 확인
                AlertsLog.sent_at >= cutoff_time,
                AlertsLog.status == "sent"
            ).first()
            
            return existing is not None
            
        except Exception as e:
            logger.error(f"Failed to check duplicate alert: {e}")
            return False
        finally:
            db.close()
    
    async def send_test_alert(self) -> bool:
        """테스트 알림 전송"""
        kst_time = datetime.now(self.kst).strftime('%Y-%m-%d %H:%M:%S')
        
        test_message = f"""🧪 <b>[테스트 알림]</b> 투자엔진 알림 시스템 테스트

📊 중요도: ⭐⭐⭐⭐
📅 시간: {kst_time}
🔗 시스템 정상 작동 중

이 메시지는 텔레그램 알림 시스템의 테스트 메시지입니다."""

        return await self.send_alert(test_message, "test")
    
    async def process_high_importance_news(self, min_importance: float = 0.7) -> int:
        """
        높은 중요도 뉴스들을 찾아서 알림 전송
        
        Args:
            min_importance: 최소 중요도 임계값
            
        Returns:
            전송된 알림 개수
        """
        if not self.is_configured():
            return 0
        
        try:
            db = get_db_session()
            
            # 최근 24시간 내, 중요도 높은 뉴스 중 아직 알림 안 보낸 것들
            cutoff_time = datetime.now(self.kst) - timedelta(hours=24)
            
            high_importance_news = db.query(News).filter(
                News.importance_score >= min_importance,
                News.created_at >= cutoff_time
            ).order_by(News.importance_score.desc()).all()
            
            sent_count = 0
            
            for news in high_importance_news:
                # 중복 발송 방지 체크
                if self.has_been_sent("news", news.id):
                    continue
                
                # 뉴스 데이터를 dict로 변환
                news_dict = {
                    'title': news.title,
                    'source': news.source,
                    'url': news.url,
                    'importance_score': news.importance_score,
                    'stock_codes': news.stock_codes or []
                }
                
                # 알림 포맷팅 및 전송
                message = self.format_news_alert(news_dict)
                
                success = await self.send_alert(
                    message, 
                    "news", 
                    news.id, 
                    news.stock_codes[0] if news.stock_codes else None
                )
                
                if success:
                    sent_count += 1
                    # 연속 전송 시 간격 두기
                    await asyncio.sleep(1)
                
            logger.info(f"Processed {len(high_importance_news)} high-importance news, sent {sent_count} alerts")
            return sent_count
            
        except Exception as e:
            logger.error(f"Failed to process high importance news: {e}")
            return 0
        finally:
            db.close()
    
    async def process_important_filings(self, grades: List[str] = ['A', 'B']) -> int:
        """
        중요 공시들을 찾아서 알림 전송
        
        Args:
            grades: 전송할 공시 등급 리스트
            
        Returns:
            전송된 알림 개수
        """
        if not self.is_configured():
            return 0
        
        try:
            db = get_db_session()
            
            # 최근 24시간 내, 중요 등급 공시 중 아직 알림 안 보낸 것들
            cutoff_time = datetime.now(self.kst) - timedelta(hours=24)
            
            important_filings = db.query(DartFiling).filter(
                DartFiling.grade.in_(grades),
                DartFiling.created_at >= cutoff_time,
                DartFiling.is_alerted == False
            ).order_by(DartFiling.created_at.desc()).all()
            
            sent_count = 0
            
            for filing in important_filings:
                # 공시 데이터를 dict로 변환
                filing_dict = {
                    'corp_name': filing.corp_name,
                    'report_nm': filing.report_nm,
                    'grade': filing.grade,
                    'rcept_no': filing.rcept_no,
                    'stock_code': filing.stock_code,
                    'rcept_dt': filing.rcept_dt
                }
                
                # 알림 포맷팅 및 전송
                message = self.format_filing_alert(filing_dict)
                
                success = await self.send_alert(
                    message, 
                    "filing", 
                    filing.id, 
                    filing.stock_code
                )
                
                if success:
                    # 알림 발송 표시
                    filing.is_alerted = True
                    db.commit()
                    sent_count += 1
                    # 연속 전송 시 간격 두기
                    await asyncio.sleep(1)
            
            logger.info(f"Processed {len(important_filings)} important filings, sent {sent_count} alerts")
            return sent_count
            
        except Exception as e:
            logger.error(f"Failed to process important filings: {e}")
            return 0
        finally:
            db.close()

# 글로벌 인스턴스
telegram_alert = TelegramAlert()

# Helper functions
async def send_test_telegram_alert():
    """테스트 알림 전송"""
    return await telegram_alert.send_test_alert()

async def process_all_high_priority_content(importance_threshold: float = 0.7):
    """모든 높은 우선순위 컨텐츠 처리"""
    news_sent = await telegram_alert.process_high_importance_news(importance_threshold)
    filings_sent = await telegram_alert.process_important_filings(['A', 'B'])
    
    logger.info(f"Alert processing complete: {news_sent} news alerts, {filings_sent} filing alerts sent")
    return {"news_alerts": news_sent, "filing_alerts": filings_sent}

if __name__ == "__main__":
    # Test run
    asyncio.run(send_test_telegram_alert())