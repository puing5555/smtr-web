"""
Job scheduler for automated tasks
"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
import pytz

from ..config.settings import settings
from ..collectors.dart import DartCollector
from ..alerts.briefing import briefing_generator
from ..alerts.telegram_bot import telegram_bot
from ..alerts.telegram_alert import telegram_alert

class InvestmentScheduler:
    """투자 엔진 스케줄러"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)
        self.is_running = False
        
    def setup_jobs(self):
        """작업 스케줄 설정"""
        
        # 1. 아침 브리핑 (평일 08:30)
        morning_time = settings.MORNING_BRIEFING_TIME.split(':')
        self.scheduler.add_job(
            self.morning_briefing_job,
            CronTrigger(
                hour=int(morning_time[0]),
                minute=int(morning_time[1]),
                day_of_week='mon-fri',  # 평일만
                timezone=settings.TIMEZONE
            ),
            id='morning_briefing',
            name='Morning Briefing',
            max_instances=1
        )
        
        # 2. 마감 요약 (평일 16:00)
        close_time = settings.MARKET_CLOSE_TIME.split(':')
        self.scheduler.add_job(
            self.market_close_summary_job,
            CronTrigger(
                hour=int(close_time[0]),
                minute=int(close_time[1]),
                day_of_week='mon-fri',  # 평일만
                timezone=settings.TIMEZONE
            ),
            id='market_close_summary',
            name='Market Close Summary',
            max_instances=1
        )
        
        # 3. DART 공시 수집 (평일 매시 정각)
        self.scheduler.add_job(
            self.dart_collection_job,
            CronTrigger(
                minute=0,  # 매시 정각
                day_of_week='mon-fri',
                timezone=settings.TIMEZONE
            ),
            id='dart_collection',
            name='DART Collection',
            max_instances=1
        )
        
        # 4. 급등락 감지 (평일 장중 5분마다 - 09:00~15:30)
        self.scheduler.add_job(
            self.price_monitoring_job,
            CronTrigger(
                minute='*/5',  # 5분마다
                hour='9-15',   # 09:00~15:59
                day_of_week='mon-fri',
                timezone=settings.TIMEZONE
            ),
            id='price_monitoring',
            name='Price Monitoring',
            max_instances=1
        )
        
        # 5. 시스템 상태 체크 (매일 자정)
        self.scheduler.add_job(
            self.system_health_check_job,
            CronTrigger(
                hour=0,
                minute=0,
                timezone=settings.TIMEZONE
            ),
            id='system_health_check',
            name='System Health Check',
            max_instances=1
        )
        
        # 6. 높은 중요도 컨텐츠 알림 체크 (평일 15분마다)
        self.scheduler.add_job(
            self.high_priority_alert_job,
            CronTrigger(
                minute='*/15',  # 15분마다
                day_of_week='mon-fri',
                timezone=settings.TIMEZONE
            ),
            id='high_priority_alerts',
            name='High Priority Content Alerts',
            max_instances=1
        )
        
        logger.info("Scheduled jobs configured")
    
    async def start(self):
        """스케줄러 시작"""
        if not self.is_running:
            self.setup_jobs()
            self.scheduler.start()
            self.is_running = True
            logger.info("Investment scheduler started")
            
            # 시작 알림
            await telegram_bot.send_message(
                "🤖 <b>Investment Engine Started</b>\n\n"
                "스케줄러가 시작되었습니다:\n"
                f"• 아침 브리핑: 평일 {settings.MORNING_BRIEFING_TIME}\n"
                f"• 마감 요약: 평일 {settings.MARKET_CLOSE_TIME}\n"
                "• DART 수집: 평일 매시 정각\n"
                "• 급등락 감지: 평일 장중 5분마다\n"
                "• 중요 알림 체크: 평일 15분마다"
            )
    
    async def stop(self):
        """스케줄러 중지"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Investment scheduler stopped")
            
            await telegram_bot.send_message("🛑 Investment Engine Stopped")
    
    def get_jobs_status(self) -> dict:
        """작업 상태 조회"""
        jobs_info = []
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time
            jobs_info.append({
                'id': job.id,
                'name': job.name,
                'next_run': next_run.strftime('%Y-%m-%d %H:%M:%S %Z') if next_run else 'N/A'
            })
        
        return {
            'running': self.is_running,
            'jobs': jobs_info
        }
    
    # Job functions
    async def morning_briefing_job(self):
        """아침 브리핑 작업"""
        logger.info("Starting morning briefing job")
        try:
            success = await briefing_generator.send_morning_briefing()
            if success:
                logger.info("Morning briefing sent successfully")
            else:
                logger.error("Failed to send morning briefing")
        except Exception as e:
            logger.error(f"Morning briefing job failed: {e}")
    
    async def market_close_summary_job(self):
        """마감 요약 작업"""
        logger.info("Starting market close summary job")
        try:
            success = await briefing_generator.send_market_close_summary()
            if success:
                logger.info("Market close summary sent successfully")
            else:
                logger.error("Failed to send market close summary")
        except Exception as e:
            logger.error(f"Market close summary job failed: {e}")
    
    async def dart_collection_job(self):
        """DART 공시 수집 작업"""
        logger.info("Starting DART collection job")
        try:
            async with DartCollector() as collector:
                new_filings = await collector.collect_and_store_filings()
                logger.info(f"DART collection completed: {new_filings} new filings")
                
                # 중요한 공시가 있으면 즉시 알림
                if new_filings > 0:
                    # 최근 공시 중 중요한 것들 확인
                    from ..db.database import get_db_session
                    from ..db.models import DartFiling
                    
                    db = get_db_session()
                    try:
                        recent_filings = db.query(DartFiling).order_by(
                            DartFiling.created_at.desc()
                        ).limit(new_filings).all()
                        
                        for filing in recent_filings:
                            filing_dict = {
                                'corp_name': filing.corp_name,
                                'report_nm': filing.report_nm,
                                'rcept_dt': filing.rcept_dt,
                                'stock_code': filing.stock_code,
                                'rcept_no': filing.rcept_no
                            }
                            
                            # 중요한 공시인지 확인
                            if collector.is_important_filing(filing_dict):
                                await telegram_bot.send_dart_alert(filing_dict)
                                logger.info(f"Important DART filing alert sent: {filing.corp_name}")
                                
                    finally:
                        db.close()
                        
        except Exception as e:
            logger.error(f"DART collection job failed: {e}")
    
    async def price_monitoring_job(self):
        """급등락 감지 작업 (향후 구현)"""
        logger.debug("Price monitoring job executed")
        # 향후 주가 API 연동하여 구현
        # 현재는 로그만 남김
        pass
    
    async def high_priority_alert_job(self):
        """높은 중요도 컨텐츠 알림 체크 작업"""
        logger.debug("Checking for high priority content to alert")
        try:
            # 중요도 높은 뉴스와 공시 체크하여 알림 발송
            news_alerts = await telegram_alert.process_high_importance_news(min_importance=0.7)
            filing_alerts = await telegram_alert.process_important_filings(['A', 'B'])
            
            total_alerts = news_alerts + filing_alerts
            
            if total_alerts > 0:
                logger.info(f"High priority alerts sent: {news_alerts} news, {filing_alerts} filings")
            else:
                logger.debug("No high priority content found for alerting")
                
        except Exception as e:
            logger.error(f"High priority alert job failed: {e}")
    
    async def system_health_check_job(self):
        """시스템 상태 체크 작업"""
        logger.info("Starting system health check")
        try:
            kst = pytz.timezone('Asia/Seoul')
            current_time = datetime.now(kst)
            
            # 기본 상태 메시지
            status_message = f"💚 <b>시스템 상태 체크</b>\n"
            status_message += f"시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # 스케줄러 상태
            jobs_status = self.get_jobs_status()
            status_message += f"스케줄러 상태: {'🟢 실행중' if jobs_status['running'] else '🔴 중지'}\n"
            status_message += f"등록된 작업 수: {len(jobs_status['jobs'])}개\n\n"
            
            # 데이터베이스 상태 체크
            from ..db.database import get_db_session
            db_status = "🟢 정상"
            try:
                db = get_db_session()
                db.execute("SELECT 1")
                db.close()
            except Exception as e:
                db_status = f"🔴 오류: {str(e)[:50]}"
            
            status_message += f"데이터베이스: {db_status}\n"
            
            # Telegram Bot 상태
            bot_status = "🟢 정상" if telegram_bot.bot else "🔴 설정되지 않음"
            status_message += f"텔레그램 봇: {bot_status}"
            
            # 상태 메시지 전송
            await telegram_bot.send_message(status_message)
            
            logger.info("System health check completed")
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            await telegram_bot.send_message(
                f"❌ <b>시스템 상태 체크 실패</b>\n\n오류: {str(e)}"
            )

# 글로벌 스케줄러 인스턴스
scheduler = InvestmentScheduler()

# Helper functions for testing
async def test_scheduler():
    """스케줄러 테스트"""
    await scheduler.start()
    
    # 잠시 대기 후 상태 출력
    await asyncio.sleep(2)
    status = scheduler.get_jobs_status()
    logger.info(f"Scheduler status: {status}")
    
    return status

if __name__ == "__main__":
    async def main():
        await test_scheduler()
        
        # 5초 후 중지
        await asyncio.sleep(5)
        await scheduler.stop()
    
    asyncio.run(main())