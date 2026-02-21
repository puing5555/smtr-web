"""
Auto Collection Scheduler
자동 수집 스케줄러 - 한국/미국/코인 뉴스 및 DART 공시 자동 수집
"""
import asyncio
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
import pytz

from .config.settings import settings
from .collectors.dart import DartCollector
from .collectors.naver_news import NaverNewsCollector
from .collectors.us_news import USNewsCollector
from .collectors.crypto_news import CryptoNewsCollector


class AutoCollectionScheduler:
    """자동 수집 스케줄러"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)
        self.is_running = False
        self.kst = pytz.timezone('Asia/Seoul')
        
    def setup_collection_jobs(self):
        """수집 작업 스케줄 설정"""
        
        # 1. 한국 뉴스 수집
        # - 기본: 매 30분
        # - 장중(09:00-18:00 KST): 매 15분
        
        # 장중 시간 (평일 09:00-18:00) - 15분 간격
        self.scheduler.add_job(
            self.korean_news_job,
            CronTrigger(
                minute='*/15',  # 15분마다
                hour='9-17',    # 09:00-17:59
                day_of_week='mon-fri',
                timezone=self.kst
            ),
            id='korean_news_market_hours',
            name='Korean News (Market Hours)',
            max_instances=1
        )
        
        # 장외 시간 - 30분 간격
        self.scheduler.add_job(
            self.korean_news_job,
            CronTrigger(
                minute='0,30',  # 매시 정각, 30분
                hour='0-8,18-23',  # 00:00-08:59, 18:00-23:59
                day_of_week='mon-fri',
                timezone=self.kst
            ),
            id='korean_news_off_hours_weekday',
            name='Korean News (Off Hours Weekday)',
            max_instances=1
        )
        
        # 주말 - 30분 간격
        self.scheduler.add_job(
            self.korean_news_job,
            CronTrigger(
                minute='0,30',  # 매시 정각, 30분
                day_of_week='sat-sun',
                timezone=self.kst
            ),
            id='korean_news_weekend',
            name='Korean News (Weekend)',
            max_instances=1
        )
        
        # 2. 미국 뉴스 수집
        # - 기본: 매 1시간
        # - 미장 시간(22:30-05:00 KST): 매 30분
        
        # 미장 시간 (22:30-05:00 KST) - 30분 간격
        self.scheduler.add_job(
            self.us_news_job,
            CronTrigger(
                minute='0,30',  # 매시 정각, 30분
                hour='22-23',   # 22:00-23:59
                day_of_week='mon-fri',
                timezone=self.kst
            ),
            id='us_news_market_hours_evening',
            name='US News (Market Hours Evening)',
            max_instances=1
        )
        
        self.scheduler.add_job(
            self.us_news_job,
            CronTrigger(
                minute='0,30',  # 매시 정각, 30분
                hour='0-5',     # 00:00-05:59
                day_of_week='tue-sat',  # 다음날
                timezone=self.kst
            ),
            id='us_news_market_hours_morning',
            name='US News (Market Hours Morning)',
            max_instances=1
        )
        
        # 미장 외 시간 - 1시간 간격
        self.scheduler.add_job(
            self.us_news_job,
            CronTrigger(
                minute=0,       # 매시 정각
                hour='6-21',    # 06:00-21:59
                day_of_week='mon-fri',
                timezone=self.kst
            ),
            id='us_news_off_hours',
            name='US News (Off Hours)',
            max_instances=1
        )
        
        # 주말 - 1시간 간격
        self.scheduler.add_job(
            self.us_news_job,
            CronTrigger(
                minute=0,       # 매시 정각
                day_of_week='sat-sun',
                timezone=self.kst
            ),
            id='us_news_weekend',
            name='US News (Weekend)',
            max_instances=1
        )
        
        # 3. 코인 뉴스 수집 - 24시간 매 30분
        self.scheduler.add_job(
            self.crypto_news_job,
            CronTrigger(
                minute='0,30',  # 매시 정각, 30분
                timezone=self.kst
            ),
            id='crypto_news_24h',
            name='Crypto News (24/7)',
            max_instances=1
        )
        
        # 4. DART 공시 수집
        # - 장중: 매 20분
        # - 장외: 매 1시간
        
        # 장중 시간 (평일 09:00-18:00) - 20분 간격
        self.scheduler.add_job(
            self.dart_collection_job,
            CronTrigger(
                minute='0,20,40',  # 0분, 20분, 40분
                hour='9-17',       # 09:00-17:59
                day_of_week='mon-fri',
                timezone=self.kst
            ),
            id='dart_market_hours',
            name='DART Collection (Market Hours)',
            max_instances=1
        )
        
        # 장외 시간 - 1시간 간격
        self.scheduler.add_job(
            self.dart_collection_job,
            CronTrigger(
                minute=0,          # 매시 정각
                hour='0-8,18-23',  # 00:00-08:59, 18:00-23:59
                day_of_week='mon-fri',
                timezone=self.kst
            ),
            id='dart_off_hours',
            name='DART Collection (Off Hours)',
            max_instances=1
        )
        
        logger.info("Auto collection jobs configured with detailed schedules")
    
    async def start(self):
        """스케줄러 시작"""
        if not self.is_running:
            self.setup_collection_jobs()
            self.scheduler.start()
            self.is_running = True
            logger.info("Auto Collection Scheduler started")
    
    async def stop(self):
        """스케줄러 중지"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Auto Collection Scheduler stopped")
    
    def toggle_scheduler(self) -> bool:
        """스케줄러 on/off 토글"""
        if self.is_running:
            asyncio.create_task(self.stop())
            return False
        else:
            asyncio.create_task(self.start())
            return True
    
    def get_scheduler_status(self) -> dict:
        """스케줄러 상태 조회"""
        jobs_info = []
        
        if self.is_running:
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time
                jobs_info.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': next_run.strftime('%Y-%m-%d %H:%M:%S %Z') if next_run else 'N/A'
                })
        
        return {
            'running': self.is_running,
            'total_jobs': len(jobs_info),
            'jobs': jobs_info,
            'last_updated': datetime.now(self.kst).isoformat()
        }
    
    # Job functions
    async def korean_news_job(self):
        """한국 뉴스 수집 작업"""
        logger.info("🇰🇷 Starting Korean news collection job")
        try:
            async with NaverNewsCollector() as collector:
                new_articles = await collector.collect_and_store_news(collect_stock_news=True)
                logger.info(f"✅ Korean news collection completed: {new_articles} new articles")
        except Exception as e:
            logger.error(f"❌ Korean news collection failed: {e}")
    
    async def us_news_job(self):
        """미국 뉴스 수집 작업"""
        logger.info("🇺🇸 Starting US news collection job")
        try:
            async with USNewsCollector() as collector:
                new_articles = await collector.collect_and_store_news()
                logger.info(f"✅ US news collection completed: {new_articles} new articles")
        except Exception as e:
            logger.error(f"❌ US news collection failed: {e}")
    
    async def crypto_news_job(self):
        """코인 뉴스 수집 작업"""
        logger.info("₿ Starting crypto news collection job")
        try:
            async with CryptoNewsCollector() as collector:
                new_articles = await collector.collect_and_store_news()
                logger.info(f"✅ Crypto news collection completed: {new_articles} new articles")
        except Exception as e:
            logger.error(f"❌ Crypto news collection failed: {e}")
    
    async def dart_collection_job(self):
        """DART 공시 수집 작업"""
        logger.info("📋 Starting DART collection job")
        try:
            async with DartCollector() as collector:
                new_filings = await collector.collect_and_store_filings(days_back=1)
                logger.info(f"✅ DART collection completed: {new_filings} new filings")
                
                # 중요한 공시 즉시 알림 (기존 로직 유지)
                if new_filings > 0:
                    await self._handle_important_dart_alerts(new_filings)
                    
        except Exception as e:
            logger.error(f"❌ DART collection failed: {e}")
    
    async def _handle_important_dart_alerts(self, new_filings_count: int):
        """중요한 DART 공시 알림 처리"""
        try:
            from .db.database import get_db_session
            from .db.models import DartFiling
            from .alerts.telegram_bot import telegram_bot
            
            db = get_db_session()
            try:
                recent_filings = db.query(DartFiling).order_by(
                    DartFiling.created_at.desc()
                ).limit(new_filings_count).all()
                
                for filing in recent_filings:
                    filing_dict = {
                        'corp_name': filing.corp_name,
                        'report_nm': filing.report_nm,
                        'rcept_dt': filing.rcept_dt,
                        'stock_code': filing.stock_code,
                        'rcept_no': filing.rcept_no
                    }
                    
                    # 중요한 공시인지 확인 (기존 로직)
                    if self._is_important_filing(filing_dict):
                        await telegram_bot.send_dart_alert(filing_dict)
                        logger.info(f"📢 Important DART filing alert sent: {filing.corp_name}")
                        
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to handle DART alerts: {e}")
    
    def _is_important_filing(self, filing: dict) -> bool:
        """중요한 공시인지 판단 (간단한 키워드 기반)"""
        important_keywords = [
            '합병', '분할', '인수', '매각', '유상증자', '전환사채', 
            '신주인수권', '배당', '대표이사', '감사', '회계감사',
            '영업정지', '관리종목', '투자주의', '상장폐지'
        ]
        
        report_name = filing.get('report_nm', '').lower()
        return any(keyword in report_name for keyword in important_keywords)


# 글로벌 스케줄러 인스턴스
auto_scheduler = AutoCollectionScheduler()


# 테스트 함수
async def test_auto_scheduler():
    """자동 수집 스케줄러 테스트"""
    await auto_scheduler.start()
    
    # 상태 확인
    await asyncio.sleep(2)
    status = auto_scheduler.get_scheduler_status()
    logger.info(f"Auto Scheduler Status: {status}")
    
    return status

if __name__ == "__main__":
    async def main():
        await test_auto_scheduler()
        
        # 10초 후 중지
        await asyncio.sleep(10)
        await auto_scheduler.stop()
    
    asyncio.run(main())