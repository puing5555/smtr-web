# -*- coding: utf-8 -*-
"""
DART 공시 필터링 + AI 요약 + 텔레그램 알림 메인 파이프라인
"""
import asyncio
from typing import List, Dict
from loguru import logger
from datetime import datetime
import pytz

from .collectors.dart import DartCollector
from .analyzers.filing_filter import FilingFilter, FilingGrade
from .analyzers.ai_summarizer import AISummarizer
from .alerts.telegram_bot import InvestmentTelegramBot
from .alerts.telegram_alert import telegram_alert
from .db.database import get_db_session
from .db.models import DartFiling

class DartAnalysisPipeline:
    """DART 공시 분석 파이프라인"""
    
    def __init__(self):
        self.dart_collector = None
        self.filing_filter = FilingFilter()
        self.ai_summarizer = AISummarizer()
        self.telegram_bot = InvestmentTelegramBot()
    
    async def run_pipeline(self, days_back: int = 1, send_alerts: bool = True) -> Dict[str, int]:
        """
        전체 파이프라인 실행
        
        Args:
            days_back: 조회할 일수
            send_alerts: 알림 전송 여부
            
        Returns:
            Dict[str, int]: 실행 결과 통계
        """
        logger.info(f"Starting DART analysis pipeline (days_back={days_back})")
        
        stats = {
            'total_filings': 0,
            'grade_a': 0,
            'grade_b': 0, 
            'grade_c': 0,
            'alerts_sent': 0,
            'analysis_done': 0,
            'errors': 0
        }
        
        try:
            # 1. DART API로 최근 공시 수집
            logger.info("Step 1: Collecting DART filings...")
            async with DartCollector() as collector:
                self.dart_collector = collector
                filings = await collector.get_recent_filings(days_back)
            
            stats['total_filings'] = len(filings)
            logger.info(f"Collected {len(filings)} filings")
            
            if not filings:
                logger.warning("No filings found")
                return stats
            
            # 2. 필터링 (A/B/C 분류)
            logger.info("Step 2: Filtering filings by grade...")
            distribution = self.filing_filter.analyze_filing_distribution(filings)
            stats.update({
                'grade_a': distribution['A'],
                'grade_b': distribution['B'],
                'grade_c': distribution['C']
            })
            
            # 모든 공시에 등급 부여
            from .analyzers.filing_filter import FilingGrade
            all_graded = self.filing_filter.filter_filings_by_grade(filings, [FilingGrade.A, FilingGrade.B, FilingGrade.C])
            
            # A+B등급만 추출 (중요 공시)
            important_filings = [f for f in all_graded if f.get('grade') in ('A', 'B')]
            logger.info(f"Found {len(important_filings)} important filings (A+B grade)")
            
            # 3. A+B등급만 AI 분석
            if important_filings:
                logger.info("Step 3: AI analysis for important filings...")
                analyzed_filings = await self._analyze_filings(important_filings)
                stats['analysis_done'] = len(analyzed_filings)
                
                # 4. 텔레그램으로 발송
                if send_alerts and analyzed_filings:
                    logger.info("Step 4: Sending Telegram alerts...")
                    sent_count = await self._send_alerts(analyzed_filings)
                    stats['alerts_sent'] = sent_count
            
            # 5. 분석 결과를 all_graded에 병합 후 DB 저장
            if important_filings and analyzed_filings:
                analyzed_map = {f.get('rcept_no'): f for f in analyzed_filings}
                for i, f in enumerate(all_graded):
                    if f.get('rcept_no') in analyzed_map:
                        all_graded[i] = analyzed_map[f['rcept_no']]
            
            logger.info("Step 5: Saving to database...")
            await self._save_to_database(all_graded)
            
            # 6. 새로운 텔레그램 알림 시스템으로 중요 공시 알림 추가 발송
            if send_alerts:
                try:
                    logger.info("Step 6: Processing important filings with new alert system...")
                    additional_alerts = await telegram_alert.process_important_filings(['A', 'B'])
                    stats['additional_alerts'] = additional_alerts
                    logger.info(f"Additional telegram alerts sent: {additional_alerts}")
                except Exception as e:
                    logger.error(f"Failed to send additional telegram alerts: {e}")
                    stats['additional_alerts'] = 0
            
            # 파이프라인 완료 메시지
            if send_alerts:
                await self._send_pipeline_summary(stats)
            
            logger.info(f"Pipeline completed successfully: {stats}")
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            stats['errors'] = 1
            
            # 에러 알림
            if send_alerts:
                error_msg = f"❌ <b>DART 파이프라인 오류</b>\n\n{str(e)}"
                await self.telegram_bot.send_message(error_msg)
        
        return stats
    
    async def _analyze_filings(self, filings: List[Dict]) -> List[Dict]:
        """
        공시 AI 분석 실행
        
        Args:
            filings: 분석할 공시 리스트
            
        Returns:
            List[Dict]: 분석 결과가 추가된 공시 리스트
        """
        analyzed_filings = []
        
        for filing in filings:
            grade = filing.get('grade')
            corp_name = filing.get('corp_name')
            
            try:
                logger.info(f"Analyzing {grade}-grade filing: {corp_name}")
                
                if grade == 'A':
                    # A등급: 정기공시 분석
                    analysis = await self.ai_summarizer.analyze_grade_a_filing(filing)
                elif grade == 'B':
                    # B등급: 중요 비정기공시 분석
                    analysis = await self.ai_summarizer.analyze_grade_b_filing(filing)
                else:
                    continue  # C등급은 분석하지 않음
                
                # 분석 결과 추가
                filing_with_analysis = filing.copy()
                filing_with_analysis['analysis'] = analysis
                analyzed_filings.append(filing_with_analysis)
                
                logger.info(f"Successfully analyzed: {corp_name}")
                
            except Exception as e:
                logger.error(f"Failed to analyze {corp_name}: {e}")
                # 분석 실패해도 원본 공시는 유지
                filing_without_analysis = filing.copy()
                filing_without_analysis['analysis'] = None
                analyzed_filings.append(filing_without_analysis)
        
        return analyzed_filings
    
    async def _send_alerts(self, analyzed_filings: List[Dict]) -> int:
        """
        분석된 공시들에 대한 텔레그램 알림 발송
        
        Args:
            analyzed_filings: 분석된 공시 리스트
            
        Returns:
            int: 성공적으로 발송된 알림 수
        """
        sent_count = 0
        
        for filing in analyzed_filings:
            corp_name = filing.get('corp_name')
            analysis = filing.get('analysis')
            
            try:
                success = await self.telegram_bot.send_dart_alert(filing, analysis)
                if success:
                    sent_count += 1
                    logger.info(f"Alert sent: {corp_name}")
                else:
                    logger.warning(f"Failed to send alert: {corp_name}")
                
                # 알림 간격 (너무 빠르게 보내지 않도록)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error sending alert for {corp_name}: {e}")
        
        return sent_count
    
    async def _save_to_database(self, filings: List[Dict]):
        """
        공시 정보를 데이터베이스에 저장
        
        Args:
            filings: 저장할 공시 리스트
        """
        db = get_db_session()
        new_filings = 0
        
        try:
            for filing_data in filings:
                # 이미 저장된 공시인지 확인
                existing = db.query(DartFiling).filter(
                    DartFiling.rcept_no == filing_data.get('rcept_no')
                ).first()
                
                if existing:
                    continue
                
                # 새 공시 저장
                filing = DartFiling(
                    rcept_no=filing_data.get('rcept_no'),
                    corp_cls=filing_data.get('corp_cls'),
                    corp_name=filing_data.get('corp_name'),
                    corp_code=filing_data.get('corp_code'),
                    stock_code=filing_data.get('stock_code'),
                    report_nm=filing_data.get('report_nm'),
                    rcept_dt=filing_data.get('rcept_dt'),
                    flr_nm=filing_data.get('flr_nm'),
                    rm=filing_data.get('rm', ''),
                    # 분석 정보 추가
                    grade=filing_data.get('grade'),
                    category=filing_data.get('grade_reason', ''),
                    ai_summary=filing_data.get('analysis', {}).get('summary') if isinstance(filing_data.get('analysis'), dict) else None,
                    ai_analysis=str(filing_data.get('analysis', '')) if filing_data.get('analysis') else None
                )
                
                db.add(filing)
                new_filings += 1
            
            db.commit()
            logger.info(f"Saved {new_filings} new filings to database")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save filings to database: {e}")
            raise
        finally:
            db.close()
    
    async def _send_pipeline_summary(self, stats: Dict[str, int]):
        """
        파이프라인 실행 요약 발송
        
        Args:
            stats: 실행 통계
        """
        kst = pytz.timezone('Asia/Seoul')
        current_time = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
        
        message = f"🤖 <b>DART 분석 파이프라인 완료</b> ({current_time})\n\n"
        message += f"📊 <b>처리 결과:</b>\n"
        message += f"• 전체 공시: {stats['total_filings']}건\n"
        message += f"• A등급 (정기): {stats['grade_a']}건\n"
        message += f"• B등급 (중요): {stats['grade_b']}건\n"
        message += f"• C등급 (일반): {stats['grade_c']}건\n"
        message += f"• AI 분석: {stats['analysis_done']}건\n"
        message += f"• 알림 발송: {stats['alerts_sent']}건\n"
        
        if stats['errors'] > 0:
            message += f"• ❌ 오류: {stats['errors']}건\n"
        
        await self.telegram_bot.send_message(message)

# 스케줄링을 위한 편의 함수들
async def run_daily_pipeline():
    """일일 파이프라인 실행"""
    pipeline = DartAnalysisPipeline()
    return await pipeline.run_pipeline(days_back=1, send_alerts=True)

async def run_test_pipeline(days_back: int = 1, send_alerts: bool = False):
    """테스트용 파이프라인 실행"""
    pipeline = DartAnalysisPipeline()
    return await pipeline.run_pipeline(days_back=days_back, send_alerts=send_alerts)

# 직접 실행시 테스트
if __name__ == "__main__":
    async def test_main():
        print("=== DART Analysis Pipeline Test ===")
        stats = await run_test_pipeline(days_back=1, send_alerts=True)
        print(f"Test completed: {stats}")
    
    asyncio.run(test_main())