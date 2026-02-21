"""
Investment Engine - Main FastAPI Application
"""
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import settings
from src.db.database import create_tables, get_db
from src.scheduler.job_scheduler import scheduler
# from src.scheduler import auto_scheduler  # 새 자동 수집 스케줄러
from src.alerts.telegram_bot import telegram_bot, send_test_message
from src.alerts.telegram_alert import telegram_alert, send_test_telegram_alert, process_all_high_priority_content
from src.alerts.briefing import briefing_generator
from src.collectors.dart import DartCollector
from src.collectors.naver_news import NaverNewsCollector
from src.collectors.us_news import USNewsCollector
from src.collectors.crypto_news import CryptoNewsCollector
from src.services.translator import translate_news_batch

# Import API routers
from src.api.notes import router as notes_router
from src.api.sns import router as sns_router

# Setup logging
logger.add(
    settings.LOG_FILE,
    level=settings.LOG_LEVEL,
    rotation="1 day",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Investment Engine")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created")
    
    # Start scheduler
    await scheduler.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Investment Engine")
    await scheduler.stop()

# Create FastAPI app
app = FastAPI(
    title="Investment Engine",
    description="투자 플랫폼용 알림/데이터 수집 시스템",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(notes_router)
app.include_router(sns_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Investment Engine API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        from src.db.database import get_db_session
        db = get_db_session()
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check scheduler
    scheduler_status = "running" if scheduler.is_running else "stopped"
    
    # Check Telegram bot
    bot_status = "configured" if telegram_bot.bot else "not_configured"
    
    return {
        "status": "healthy",
        "database": db_status,
        "scheduler": scheduler_status,
        "telegram_bot": bot_status,
        "timestamp": "2026-02-20T10:59:00+07:00"
    }

@app.get("/status")
async def get_status():
    """Get detailed system status"""
    jobs_status = scheduler.get_jobs_status()
    
    return {
        "scheduler": jobs_status,
        "settings": {
            "morning_briefing": settings.MORNING_BRIEFING_TIME,
            "market_close": settings.MARKET_CLOSE_TIME,
            "timezone": str(settings.TIMEZONE),
            "price_threshold": settings.PRICE_ALERT_THRESHOLD
        },
        "configuration": {
            "dart_api": "configured" if settings.DART_API_KEY else "not_configured",
            "telegram_bot": "configured" if settings.TELEGRAM_BOT_TOKEN else "not_configured",
            "openai_api": "configured" if settings.OPENAI_API_KEY else "not_configured"
        }
    }

# Manual trigger endpoints
@app.post("/trigger/morning-briefing")
async def trigger_morning_briefing():
    """Manually trigger morning briefing"""
    try:
        success = await briefing_generator.send_morning_briefing()
        return {
            "success": success,
            "message": "Morning briefing sent" if success else "Failed to send morning briefing"
        }
    except Exception as e:
        logger.error(f"Manual morning briefing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger/market-close-summary")
async def trigger_market_close_summary():
    """Manually trigger market close summary"""
    try:
        success = await briefing_generator.send_market_close_summary()
        return {
            "success": success,
            "message": "Market close summary sent" if success else "Failed to send market close summary"
        }
    except Exception as e:
        logger.error(f"Manual market close summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger/dart-collection")
async def trigger_dart_collection():
    """Manually trigger DART collection"""
    try:
        async with DartCollector() as collector:
            new_filings = await collector.collect_and_store_filings(days_back=1)
            return {
                "success": True,
                "new_filings": new_filings,
                "message": f"DART collection completed: {new_filings} new filings"
            }
    except Exception as e:
        logger.error(f"Manual DART collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger/test-telegram")
async def trigger_test_telegram():
    """Test Telegram bot"""
    try:
        success = await send_test_message("🧪 Manual test message from Investment Engine API")
        return {
            "success": success,
            "message": "Test message sent" if success else "Failed to send test message"
        }
    except Exception as e:
        logger.error(f"Telegram test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger/telegram-alert-test")
async def trigger_telegram_alert_test():
    """Test new Telegram alert system"""
    try:
        success = await send_test_telegram_alert()
        return {
            "success": success,
            "message": "Telegram alert test sent" if success else "Failed to send telegram alert test"
        }
    except Exception as e:
        logger.error(f"Telegram alert test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger/process-high-priority")
async def trigger_process_high_priority():
    """Process and send high priority news/filings alerts"""
    try:
        result = await process_all_high_priority_content()
        total_sent = result["news_alerts"] + result["filing_alerts"]
        return {
            "success": True,
            "news_alerts_sent": result["news_alerts"],
            "filing_alerts_sent": result["filing_alerts"],
            "total_sent": total_sent,
            "message": f"Processed high priority content: {total_sent} alerts sent"
        }
    except Exception as e:
        logger.error(f"High priority processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger/news-collection")
async def trigger_news_collection():
    """Manually trigger Naver news collection"""
    try:
        async with NaverNewsCollector() as collector:
            new_news = await collector.collect_and_store_news(collect_stock_news=True)
            return {
                "success": True,
                "new_news": new_news,
                "message": f"News collection completed: {new_news} new articles"
            }
    except Exception as e:
        logger.error(f"Manual news collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger/us-news-collection")
async def trigger_us_news_collection():
    """Manually trigger US news collection"""
    try:
        async with USNewsCollector() as collector:
            new_news = await collector.collect_and_store_news(
                collect_stock_specific=True,
                market_news_limit=20,
                stock_limit_per_ticker=5
            )
            return {
                "success": True,
                "new_news": new_news,
                "message": f"US news collection completed: {new_news} new articles"
            }
    except Exception as e:
        logger.error(f"Manual US news collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger/crypto-news-collection")
async def trigger_crypto_news_collection():
    """Manually trigger crypto news collection"""
    try:
        async with CryptoNewsCollector() as collector:
            new_news = await collector.collect_and_store_news()
            return {
                "success": True,
                "new_news": new_news,
                "message": f"Crypto news collection completed: {new_news} new articles"
            }
    except Exception as e:
        logger.error(f"Manual crypto news collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Scheduler Control endpoints
@app.get("/api/scheduler/status")
async def get_scheduler_status():
    """스케줄러 상태 조회"""
    try:
        status = auto_scheduler.get_scheduler_status()
        return {
            "success": True,
            "scheduler": status
        }
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scheduler/toggle")
async def toggle_scheduler():
    """스케줄러 on/off 토글"""
    try:
        new_state = auto_scheduler.toggle_scheduler()
        status = auto_scheduler.get_scheduler_status()
        
        return {
            "success": True,
            "running": new_state,
            "message": f"Scheduler {'started' if new_state else 'stopped'}",
            "scheduler": status
        }
    except Exception as e:
        logger.error(f"Failed to toggle scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Alert Settings endpoints
@app.get("/api/alert-settings")
async def get_alert_settings():
    """Get current alert settings"""
    try:
        # 현재 설정 상태 반환
        alert_config = {
            "telegram_configured": telegram_alert.is_configured(),
            "telegram_chat_id": settings.TELEGRAM_CHAT_ID if settings.TELEGRAM_CHAT_ID else None,
            "importance_threshold": 0.7,  # 기본값
            "filing_grades": ["A", "B"],  # A, B 등급 공시만 알림
            "enabled": telegram_alert.is_configured(),
            "last_checked": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "settings": alert_config
        }
    except Exception as e:
        logger.error(f"Failed to get alert settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/alert-settings")
async def update_alert_settings(settings_data: dict):
    """Update alert settings"""
    try:
        # 현재는 기본 설정만 반환 (실제 구현 시 DB에 저장)
        importance_threshold = settings_data.get("importance_threshold", 0.7)
        filing_grades = settings_data.get("filing_grades", ["A", "B"])
        enabled = settings_data.get("enabled", True)
        
        # 설정 유효성 검사
        if not 0.0 <= importance_threshold <= 1.0:
            raise HTTPException(status_code=400, detail="Importance threshold must be between 0.0 and 1.0")
        
        if not all(grade in ["A", "B", "C"] for grade in filing_grades):
            raise HTTPException(status_code=400, detail="Filing grades must be A, B, or C")
        
        updated_config = {
            "telegram_configured": telegram_alert.is_configured(),
            "importance_threshold": importance_threshold,
            "filing_grades": filing_grades,
            "enabled": enabled and telegram_alert.is_configured(),
            "updated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Alert settings updated: threshold={importance_threshold}, grades={filing_grades}, enabled={enabled}")
        
        return {
            "success": True,
            "message": "Alert settings updated successfully",
            "settings": updated_config
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update alert settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Data endpoints
@app.get("/api/filings")
async def get_filings(
    grade: str = None, 
    search: str = None, 
    page: int = 1, 
    limit: int = 20,
    db=Depends(get_db)
):
    """Get DART filings with filters for timeline feed"""
    try:
        from src.db.models import DartFiling
        from sqlalchemy import and_, or_
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Build query
        query = db.query(DartFiling)
        
        # Apply filters
        conditions = []
        
        if grade:
            if grade == "A":
                conditions.append(DartFiling.grade == "A")
            elif grade == "B":
                conditions.append(DartFiling.grade == "B")
            # 전체는 필터링 없음
        
        if search:
            conditions.append(
                or_(
                    DartFiling.corp_name.contains(search),
                    DartFiling.report_nm.contains(search)
                )
            )
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        # Order by receipt date desc, then created_at desc
        query = query.order_by(
            DartFiling.rcept_dt.desc(),
            DartFiling.created_at.desc()
        )
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination
        filings = query.offset(offset).limit(limit).all()
        
        def format_time(filing):
            """Format created_at to HH:MM"""
            if filing.created_at:
                return filing.created_at.strftime("%H:%M")
            return "00:00"
        
        def get_grade_icon(grade):
            """Get grade icon"""
            if grade == "A":
                return "📊"
            elif grade == "B":
                return "🔔"
            else:
                return "📋"
        
        def format_dart_url(rcept_no):
            """Format DART URL"""
            return f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"
        
        return {
            "success": True,
            "filings": [
                {
                    "id": filing.id,
                    "time": format_time(filing),
                    "grade": filing.grade or "C",
                    "grade_icon": get_grade_icon(filing.grade),
                    "corp_name": filing.corp_name,
                    "report_name": filing.report_nm,
                    "ai_summary": filing.ai_summary,
                    "dart_url": format_dart_url(filing.rcept_no),
                    "receipt_date": filing.rcept_dt,
                    "stock_code": filing.stock_code,
                    "created_at": filing.created_at.isoformat() if filing.created_at else None
                }
                for filing in filings
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit,
                "has_next": page * limit < total_count,
                "has_prev": page > 1
            }
        }
    except Exception as e:
        logger.error(f"Failed to get filings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news")
async def get_news(
    search: str = None, 
    market: str = None,
    page: int = 1, 
    limit: int = 20,
    db=Depends(get_db)
):
    """Get news with filters and pagination"""
    try:
        from src.db.models import News
        from sqlalchemy import and_, or_
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Build query
        query = db.query(News)
        
        # Apply filters
        conditions = []
        
        if search:
            conditions.append(
                or_(
                    News.title.contains(search),
                    News.source.contains(search)
                )
            )
        
        # Market filter (if market field exists)
        if market:
            try:
                if hasattr(News, 'market'):
                    conditions.append(News.market == market)
                else:
                    # Fallback: filter by source for crypto
                    if market == 'crypto':
                        conditions.append(
                            or_(
                                News.source == 'coindesk',
                                News.source == 'cointelegraph'
                            )
                        )
            except Exception as e:
                logger.warning(f"Market filter error: {e}")
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        # Order by published_at desc, then created_at desc
        query = query.order_by(
            News.published_at.desc().nullslast(),
            News.created_at.desc()
        )
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination
        news_items = query.offset(offset).limit(limit).all()
        
        def format_time(news_item):
            """Format published_at or created_at to HH:MM"""
            dt = news_item.published_at or news_item.created_at
            if dt:
                return dt.strftime("%H:%M")
            return "00:00"
        
        def format_source_display(source):
            """Format source for display"""
            source_map = {
                'naver_finance': '네이버증권',
                'naver_finance_연합뉴스': '연합뉴스',
                'naver_finance_뉴스1': '뉴스1',
                'naver_finance_매일경제': '매경',
                'naver_finance_한국경제': '한경',
                'yahoo_finance': 'Yahoo Finance',
                'google_finance': 'Google Finance',
                'coindesk': 'CoinDesk',
                'cointelegraph': 'CoinTelegraph'
            }
            return source_map.get(source, source)
        
        return {
            "success": True,
            "news": [
                {
                    "id": news.id,
                    "time": format_time(news),
                    "title": news.title,
                    "url": news.url,
                    "source": format_source_display(news.source),
                    "stock_codes": news.stock_codes or [],
                    "importance_score": news.importance_score,
                    "ai_summary": news.ai_summary,
                    "published_at": news.published_at.isoformat() if news.published_at else None,
                    "created_at": news.created_at.isoformat() if news.created_at else None
                }
                for news in news_items
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit,
                "has_next": page * limit < total_count,
                "has_prev": page > 1
            }
        }
    except Exception as e:
        logger.error(f"Failed to get news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/feed")
async def get_feed(
    content_type: str = "all",  # all, filings, news
    search: str = None,
    market: str = None,
    page: int = 1,
    limit: int = 20,
    db=Depends(get_db)
):
    """Get integrated feed of filings and news"""
    try:
        from src.db.models import DartFiling, News
        from sqlalchemy import and_, or_, union_all, literal, func
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Separate queries and combine manually
        feed_items = []
        
        if content_type == "filings" or content_type == "all":
            # Get filings
            filing_query = db.query(DartFiling).order_by(DartFiling.created_at.desc())
            
            if search:
                filing_query = filing_query.filter(
                    or_(
                        DartFiling.corp_name.contains(search),
                        DartFiling.report_nm.contains(search)
                    )
                )
            
            if content_type == "filings":
                filing_query = filing_query.offset(offset).limit(limit)
                
            filings = filing_query.all()
            
            # Convert filings to feed items
            for filing in filings:
                feed_items.append({
                    'id': filing.id,
                    'type': 'filing',
                    'created_at': filing.created_at,
                    'title': filing.corp_name,
                    'subtitle': filing.report_nm,
                    'grade': filing.grade,
                    'ai_summary': filing.ai_summary,
                    'external_id': filing.rcept_no,
                    'stock_code': filing.stock_code,
                    'url': None,
                    'source': None,
                    'importance_score': None
                })
        
        if content_type == "news" or content_type == "all":
            # Get news
            news_query = db.query(News).order_by(News.created_at.desc())
            
            if search:
                news_query = news_query.filter(News.title.contains(search))
            
            # Market filter for news
            if market:
                try:
                    if hasattr(News, 'market'):
                        news_query = news_query.filter(News.market == market)
                    else:
                        # Fallback: filter by source for crypto
                        if market == 'crypto':
                            news_query = news_query.filter(
                                or_(
                                    News.source == 'coindesk',
                                    News.source == 'cointelegraph'
                                )
                            )
                except Exception as e:
                    logger.warning(f"Market filter error in feed: {e}")
            
            if content_type == "news":
                news_query = news_query.offset(offset).limit(limit)
                
            news_items = news_query.all()
            
            # Convert news to feed items
            for news in news_items:
                feed_items.append({
                    'id': news.id,
                    'type': 'news',
                    'created_at': news.created_at,
                    'title': news.title,
                    'subtitle': None,
                    'grade': None,
                    'ai_summary': news.ai_summary,
                    'external_id': None,
                    'stock_code': None,
                    'url': news.url,
                    'source': news.source,
                    'importance_score': news.importance_score
                })
        
        # Sort by created_at desc if combining both
        if content_type == "all":
            feed_items.sort(key=lambda x: x['created_at'] if x['created_at'] else datetime.min, reverse=True)
            total_count = len(feed_items)
            # Apply pagination
            feed_items = feed_items[offset:offset + limit]
        else:
            total_count = len(feed_items)
        
        def format_time(created_at):
            """Format created_at to HH:MM"""
            if created_at:
                return created_at.strftime("%H:%M")
            return "00:00"
        
        def format_feed_item(item):
            """Format feed item for display"""
            if item['type'] == "filing":
                # Format DART URL
                dart_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item['external_id']}" if item['external_id'] else None
                
                # Grade icon
                grade_icon = "📊" if item['grade'] == "A" else ("🔔" if item['grade'] == "B" else "📋")
                
                return {
                    "id": item['id'],
                    "type": "filing",
                    "time": format_time(item['created_at']),
                    "icon": grade_icon,
                    "title": item['title'],  # corp_name
                    "subtitle": item['subtitle'],  # report_nm
                    "grade": item['grade'] or "C",
                    "ai_summary": item['ai_summary'],
                    "url": dart_url,
                    "stock_code": item['stock_code'],
                    "created_at": item['created_at'].isoformat() if item['created_at'] else None
                }
            else:  # news
                # Source display
                source_map = {
                    'naver_finance': '네이버증권',
                    'naver_finance_연합뉴스': '연합뉴스',
                    'naver_finance_뉴스1': '뉴스1',
                    'naver_finance_매일경제': '매경',
                    'naver_finance_한국경제': '한경',
                    'yahoo_finance': 'Yahoo Finance',
                    'google_finance': 'Google Finance'
                }
                source_display = source_map.get(item['source'], item['source']) if item['source'] else "뉴스"
                
                return {
                    "id": item['id'],
                    "type": "news",
                    "time": format_time(item['created_at']),
                    "icon": "📰",
                    "title": item['title'],
                    "subtitle": source_display,
                    "ai_summary": item['ai_summary'],
                    "url": item['url'],
                    "importance_score": item['importance_score'],
                    "created_at": item['created_at'].isoformat() if item['created_at'] else None
                }
        
        return {
            "success": True,
            "feed": [format_feed_item(item) for item in feed_items],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit,
                "has_next": page * limit < total_count,
                "has_prev": page > 1
            }
        }
    except Exception as e:
        logger.error(f"Failed to get feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/filings")
async def get_recent_filings(limit: int = 10, db=Depends(get_db)):
    """Get recent DART filings (legacy endpoint)"""
    try:
        from src.db.models import DartFiling
        
        filings = db.query(DartFiling).order_by(
            DartFiling.created_at.desc()
        ).limit(limit).all()
        
        return {
            "filings": [
                {
                    "id": filing.id,
                    "corp_name": filing.corp_name,
                    "report_name": filing.report_nm,
                    "stock_code": filing.stock_code,
                    "receipt_date": filing.rcept_dt,
                    "created_at": filing.created_at.isoformat() if filing.created_at else None
                }
                for filing in filings
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get filings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/alerts")
async def get_recent_alerts(limit: int = 20, db=Depends(get_db)):
    """Get recent alerts log"""
    try:
        from src.db.models import AlertsLog
        
        alerts = db.query(AlertsLog).order_by(
            AlertsLog.sent_at.desc()
        ).limit(limit).all()
        
        return {
            "alerts": [
                {
                    "id": alert.id,
                    "type": alert.alert_type,
                    "title": alert.title,
                    "recipient": alert.recipient,
                    "status": alert.status,
                    "sent_at": alert.sent_at.isoformat() if alert.sent_at else None
                }
                for alert in alerts
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger/translate-news")
async def trigger_translate_news(
    market: Optional[str] = None,
    limit: int = 50
):
    """
    번역되지 않은 뉴스 일괄 번역
    
    Args:
        market: 'us', 'crypto' 또는 None (둘 다)
        limit: 한 번에 처리할 최대 뉴스 개수
    """
    try:
        logger.info(f"뉴스 번역 시작: market={market}, limit={limit}")
        
        # 번역 실행
        translated_count = await translate_news_batch(market=market, limit=limit)
        
        return {
            "success": True,
            "message": f"뉴스 번역 완료: {translated_count}개 번역됨",
            "translated_count": translated_count,
            "market": market,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"뉴스 번역 실패: {e}")
        raise HTTPException(status_code=500, detail=f"번역 실패: {str(e)}")

# Profile and Badge API Endpoints

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    investment_style: Optional[str] = None
    is_public: Optional[bool] = None

class UserProfile(BaseModel):
    user_id: str
    name: str
    bio: Optional[str] = None
    investment_style: str
    avatar: Optional[str] = None
    is_public: bool = True
    is_verified: bool = False
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    badges: List[dict] = []

@app.get("/api/profile/{user_id}")
async def get_profile(user_id: str, db=Depends(get_db)):
    """사용자 프로필 조회"""
    try:
        from src.db.models import User, UserBadge, Badge
        
        # 사용자 조회
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        # 사용자 뱃지 조회
        user_badges = db.query(UserBadge, Badge).join(
            Badge, UserBadge.badge_id == Badge.id
        ).filter(
            UserBadge.user_id == user_id,
            UserBadge.is_displayed == True
        ).all()
        
        badges = [
            {
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "icon": badge.icon,
                "category": badge.category,
                "rarity": badge.rarity,
                "earned_at": user_badge.earned_at.isoformat() if user_badge.earned_at else None,
                "earned_reason": user_badge.earned_reason
            }
            for user_badge, badge in user_badges
        ]
        
        return {
            "success": True,
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "bio": user.bio,
                "investment_style": user.investment_style,
                "avatar": user.avatar,
                "is_public": user.is_public,
                "is_verified": user.is_verified,
                "followers_count": user.followers_count,
                "following_count": user.following_count,
                "posts_count": user.posts_count,
                "badges": badges,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/profile/{user_id}")
async def update_profile(user_id: str, profile: UserProfileUpdate, db=Depends(get_db)):
    """사용자 프로필 업데이트"""
    try:
        from src.db.models import User
        
        # 사용자 조회
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            # 사용자가 없으면 새로 생성
            user = User(user_id=user_id)
            db.add(user)
        
        # 필드 업데이트
        if profile.name is not None:
            user.name = profile.name
        if profile.bio is not None:
            user.bio = profile.bio
        if profile.investment_style is not None:
            # 유효한 투자성향인지 확인
            valid_styles = [
                "가치투자자", "모멘텀투자자", "단타", "스윙", 
                "배당투자자", "인덱스투자자", "비트코이너"
            ]
            if profile.investment_style not in valid_styles:
                raise HTTPException(status_code=400, detail="유효하지 않은 투자성향입니다")
            user.investment_style = profile.investment_style
        if profile.is_public is not None:
            user.is_public = profile.is_public
        
        user.updated_at = now_kst()
        
        db.commit()
        db.refresh(user)
        
        return {
            "success": True,
            "message": "프로필이 업데이트되었습니다",
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "bio": user.bio,
                "investment_style": user.investment_style,
                "is_public": user.is_public,
                "updated_at": user.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update profile: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-badges") 
async def test_badges_simple():
    """Simple test badges endpoint"""
    return {
        "success": True,
        "message": "Badge API is working",
        "badges": [
            {"name": "Test Badge", "icon": "🎯", "rarity": "common"}
        ]
    }

@app.get("/api/badges")
async def get_all_badges(db=Depends(get_db)):
    """모든 뱃지 목록 조회"""
    try:
        from src.db.models import Badge
        
        badges = db.query(Badge).filter(Badge.is_active == True).all()
        
        return {
            "success": True,
            "badges": [
                {
                    "id": badge.id,
                    "name": badge.name,
                    "description": badge.description,
                    "icon": badge.icon,
                    "category": badge.category,
                    "rarity": badge.rarity
                }
                for badge in badges
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get badges: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/badges/initialize")
async def initialize_badges(db=Depends(get_db)):
    """기본 뱃지들을 초기화"""
    try:
        from src.db.models import Badge
        
        # 기본 뱃지 데이터
        default_badges = [
            {
                "name": "등록 인플루언서",
                "description": "인증된 투자 인플루언서입니다",
                "icon": "⭐",
                "category": "achievement",
                "rarity": "rare"
            },
            {
                "name": "비트코이너",
                "description": "암호화폐 투자 전문가입니다",
                "icon": "₿",
                "category": "special",
                "rarity": "epic"
            },
            {
                "name": "가치투자 마스터",
                "description": "가치투자에 정통한 투자자입니다",
                "icon": "💎",
                "category": "achievement",
                "rarity": "epic"
            },
            {
                "name": "신규 회원",
                "description": "투자 SNS에 오신 것을 환영합니다!",
                "icon": "🎉",
                "category": "general",
                "rarity": "common"
            },
            {
                "name": "활동적인 투자자",
                "description": "활발한 투자 소통을 하고 있습니다",
                "icon": "🚀",
                "category": "achievement",
                "rarity": "rare"
            }
        ]
        
        # 기존 뱃지가 없을 경우에만 생성
        created_count = 0
        for badge_data in default_badges:
            existing = db.query(Badge).filter(Badge.name == badge_data["name"]).first()
            if not existing:
                badge = Badge(**badge_data)
                db.add(badge)
                created_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"{created_count}개의 기본 뱃지가 생성되었습니다",
            "created_count": created_count
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize badges: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

class GrantBadgeRequest(BaseModel):
    badge_name: str
    reason: Optional[str] = ""

@app.post("/api/users/{user_id}/badges")
async def grant_badge_to_user(user_id: str, request: GrantBadgeRequest, db=Depends(get_db)):
    """사용자에게 뱃지 부여"""
    try:
        from src.db.models import User, Badge, UserBadge
        
        # 사용자 확인/생성
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            # 사용자가 없으면 기본값으로 생성
            user = User(
                user_id=user_id,
                name="새 사용자",
                investment_style="가치투자자"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 뱃지 확인
        badge = db.query(Badge).filter(Badge.name == request.badge_name).first()
        if not badge:
            raise HTTPException(status_code=404, detail=f"뱃지 '{request.badge_name}'를 찾을 수 없습니다")
        
        # 이미 보유한 뱃지인지 확인
        existing_user_badge = db.query(UserBadge).filter(
            UserBadge.user_id == user_id,
            UserBadge.badge_id == badge.id
        ).first()
        
        if existing_user_badge:
            return {
                "success": True,
                "message": f"이미 '{badge.name}' 뱃지를 보유하고 있습니다",
                "badge": {
                    "name": badge.name,
                    "icon": badge.icon,
                    "earned_at": existing_user_badge.earned_at.isoformat()
                }
            }
        
        # 뱃지 부여
        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge.id,
            earned_reason=request.reason
        )
        db.add(user_badge)
        db.commit()
        
        return {
            "success": True,
            "message": f"'{badge.name}' 뱃지가 부여되었습니다",
            "badge": {
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "icon": badge.icon,
                "category": badge.category,
                "rarity": badge.rarity,
                "earned_reason": request.reason
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to grant badge: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/users/{user_id}/badges/{badge_name}")
async def remove_badge_from_user(user_id: str, badge_name: str, db=Depends(get_db)):
    """사용자에게서 뱃지 제거"""
    try:
        from src.db.models import Badge, UserBadge
        
        # 뱃지 확인
        badge = db.query(Badge).filter(Badge.name == badge_name).first()
        if not badge:
            raise HTTPException(status_code=404, detail=f"뱃지 '{badge_name}'를 찾을 수 없습니다")
        
        # 사용자 뱃지 확인 및 제거
        user_badge = db.query(UserBadge).filter(
            UserBadge.user_id == user_id,
            UserBadge.badge_id == badge.id
        ).first()
        
        if not user_badge:
            raise HTTPException(status_code=404, detail="해당 뱃지를 보유하고 있지 않습니다")
        
        db.delete(user_badge)
        db.commit()
        
        return {
            "success": True,
            "message": f"'{badge.name}' 뱃지가 제거되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove badge: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Influencer API Endpoints  
@app.get("/api/influencers")
async def get_influencers():
    """인플루언서 목록 조회"""
    try:
        # Mock data - 실제로는 DB에서 가져올 것
        influencers = [
            {
                "id": 6,
                "name": "박두환",
                "channel": "YouTube",
                "style": "단타/스윙",
                "color": "#3b82f6",
                "accuracy": 75.2,
                "avg_return": 18.5,
                "main_stock": "삼성전자",
                "img": "https://randomuser.me/api/portraits/men/75.jpg",
                "signal_count": 45,
                "follower_count": 12500
            },
            {
                "id": 11, 
                "name": "이효석",
                "channel": "YouTube",
                "style": "장기투자",
                "color": "#a855f7",
                "accuracy": 82.1,
                "avg_return": 24.3,
                "main_stock": "엔비디아",
                "img": "https://randomuser.me/api/portraits/men/32.jpg",
                "signal_count": 38,
                "follower_count": 8900
            },
            {
                "id": 15,
                "name": "세상학개론", 
                "channel": "YouTube",
                "style": "성장주",
                "color": "#10b981",
                "accuracy": 88.7,
                "avg_return": 35.2,
                "main_stock": "팔란티어",
                "img": "https://randomuser.me/api/portraits/men/45.jpg",
                "signal_count": 52,
                "follower_count": 15600
            },
            {
                "id": 18,
                "name": "코린이아빠",
                "channel": "YouTube", 
                "style": "코인/주식",
                "color": "#f59e0b",
                "accuracy": 68.9,
                "avg_return": 42.1,
                "main_stock": "비트코인",
                "img": "https://randomuser.me/api/portraits/men/67.jpg",
                "signal_count": 73,
                "follower_count": 23400
            }
        ]
        
        return {
            "success": True,
            "data": influencers
        }
    except Exception as e:
        logger.error(f"Failed to get influencers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/signals/recent")
async def get_recent_signals(limit: int = 10):
    """최근 인플루언서 시그널 조회"""
    try:
        # Mock data - 실제로는 DB에서 가져올 것
        recent_signals = [
            {
                "id": "s1",
                "influencer_name": "박두환",
                "stock": "삼성전자",
                "signal": "buy",
                "content": "3분기 실적 발표 후 조정받은 현재가는 매수 기회",
                "date": "2026-02-21T02:30:00Z",
                "accuracy": 85
            },
            {
                "id": "s2",
                "influencer_name": "이효석", 
                "stock": "엔비디아",
                "signal": "strong-buy",
                "content": "AI 반도체 수요 급증으로 향후 2년간 고성장 예상",
                "date": "2026-02-20T07:15:00Z", 
                "accuracy": 92
            },
            {
                "id": "s3",
                "influencer_name": "세상학개론",
                "stock": "팔란티어",
                "signal": "hold",
                "content": "정부 계약 증가로 실적 개선 중. 현재가에서 홀딩 유지",
                "date": "2026-02-19T12:45:00Z",
                "accuracy": 78
            }
        ]
        
        return {
            "success": True,
            "data": recent_signals[:limit]
        }
    except Exception as e:
        logger.error(f"Failed to get recent signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Signal Verification API endpoints
@app.get("/smtr_data/corinpapa1106/_extracted_signals.json")
async def get_extracted_signals():
    """Get original extracted signals for signal review"""
    try:
        import json
        signals_file = r"C:\Users\Mario\.openclaw\workspace\smtr_data\corinpapa1106\_extracted_signals.json"
        
        if not os.path.exists(signals_file):
            raise HTTPException(status_code=404, detail="Signals file not found")
            
        with open(signals_file, 'r', encoding='utf-8') as f:
            signals_data = json.load(f)
            
        return signals_data
    except Exception as e:
        logger.error(f"Failed to get extracted signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/smtr_data/corinpapa1106/_verify_batch_test_result.jsonl")
async def get_verification_results():
    """Get GPT-4o verification results in JSONL format"""
    try:
        from fastapi.responses import PlainTextResponse
        
        results_file = r"C:\Users\Mario\.openclaw\workspace\smtr_data\corinpapa1106\_verify_batch_test_result.jsonl"
        
        if not os.path.exists(results_file):
            raise HTTPException(status_code=404, detail="Verification results file not found")
            
        with open(results_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return PlainTextResponse(content, media_type="application/jsonl")
    except Exception as e:
        logger.error(f"Failed to get verification results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/smtr_data/corinpapa1106/_verify_batch_full_result.jsonl")
async def get_full_verification_results():
    """Get full GPT-4o verification results in JSONL format"""
    try:
        from fastapi.responses import PlainTextResponse
        
        results_file = r"C:\Users\Mario\.openclaw\workspace\smtr_data\corinpapa1106\_verify_batch_full_result.jsonl"
        
        if not os.path.exists(results_file):
            # If full results don't exist, fallback to test results
            return await get_verification_results()
            
        with open(results_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return PlainTextResponse(content, media_type="application/jsonl")
    except Exception as e:
        logger.error(f"Failed to get full verification results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/signal-reviews")
async def save_signal_review(review_data: dict):
    """Save human review results"""
    try:
        # For now, just return success since we're using localStorage
        # In the future, this could save to database
        return {
            "success": True,
            "message": "Review saved successfully",
            "data": review_data
        }
    except Exception as e:
        logger.error(f"Failed to save signal review: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/signal-reviews")
async def get_signal_reviews():
    """Get all human review results"""
    try:
        # For now, return empty since we're using localStorage
        # In the future, this could fetch from database
        return {
            "success": True,
            "data": {},
            "message": "Using localStorage for now"
        }
    except Exception as e:
        logger.error(f"Failed to get signal reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

def run_server():
    """Run the server"""
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    run_server()