# -*- coding: utf-8 -*-
"""
DART 필터링 + AI 요약 + 텔레그램 알림 파이프라인 테스트 스크립트
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.pipeline import DartAnalysisPipeline, run_test_pipeline
from src.analyzers.filing_filter import FilingFilter, test_filing_filter
from src.analyzers.ai_summarizer import AISummarizer, test_ai_summarizer
from src.collectors.dart import DartCollector, test_dart_collector
from src.alerts.telegram_bot import InvestmentTelegramBot, test_telegram_bot
from loguru import logger

# 로깅 설정
logger.add("logs/test_pipeline_{time}.log", rotation="1 day", level="DEBUG")

class TestRunner:
    """테스트 실행 클래스"""
    
    def __init__(self):
        self.results = {}
    
    async def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 DART Analysis Pipeline - Full Test Suite")
        print("=" * 50)
        
        # 1. 개별 모듈 테스트
        await self.test_filing_filter()
        await self.test_ai_summarizer() 
        await self.test_dart_collector()
        await self.test_telegram_bot()
        
        # 2. 통합 파이프라인 테스트
        await self.test_full_pipeline()
        
        # 3. 결과 요약
        self.print_summary()
    
    async def test_filing_filter(self):
        """공시 필터링 테스트"""
        print("\n📋 Testing Filing Filter...")
        try:
            # 기존 테스트 함수 호출
            test_filing_filter()
            self.results['filing_filter'] = '✅ PASS'
        except Exception as e:
            logger.error(f"Filing filter test failed: {e}")
            self.results['filing_filter'] = f'❌ FAIL: {e}'
    
    async def test_ai_summarizer(self):
        """AI 분석기 테스트"""
        print("\n🤖 Testing AI Summarizer...")
        try:
            await test_ai_summarizer()
            self.results['ai_summarizer'] = '✅ PASS'
        except Exception as e:
            logger.error(f"AI summarizer test failed: {e}")
            self.results['ai_summarizer'] = f'❌ FAIL: {e}'
    
    async def test_dart_collector(self):
        """DART 수집기 테스트"""  
        print("\n📡 Testing DART Collector...")
        try:
            await test_dart_collector()
            self.results['dart_collector'] = '✅ PASS'
        except Exception as e:
            logger.error(f"DART collector test failed: {e}")
            self.results['dart_collector'] = f'❌ FAIL: {e}'
    
    async def test_telegram_bot(self):
        """텔레그램 봇 테스트"""
        print("\n📱 Testing Telegram Bot...")
        try:
            await test_telegram_bot()
            self.results['telegram_bot'] = '✅ PASS'
        except Exception as e:
            logger.error(f"Telegram bot test failed: {e}")
            self.results['telegram_bot'] = f'❌ FAIL: {e}'
    
    async def test_full_pipeline(self):
        """전체 파이프라인 통합 테스트"""
        print("\n🔄 Testing Full Pipeline...")
        try:
            # 실제 DART 데이터로 테스트 (알림 안 보냄)
            stats = await run_test_pipeline(days_back=1, send_alerts=False)
            
            print(f"\n📊 Pipeline Test Results:")
            print(f"   Total filings: {stats['total_filings']}")
            print(f"   Grade A: {stats['grade_a']}")
            print(f"   Grade B: {stats['grade_b']}")
            print(f"   Grade C: {stats['grade_c']}")
            print(f"   Analysis done: {stats['analysis_done']}")
            print(f"   Alerts sent: {stats['alerts_sent']}")
            print(f"   Errors: {stats['errors']}")
            
            if stats['errors'] == 0:
                self.results['full_pipeline'] = '✅ PASS'
            else:
                self.results['full_pipeline'] = f'⚠️ PARTIAL: {stats["errors"]} errors'
                
        except Exception as e:
            logger.error(f"Full pipeline test failed: {e}")
            self.results['full_pipeline'] = f'❌ FAIL: {e}'
    
    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        for test_name, result in self.results.items():
            print(f"{test_name:20s}: {result}")
        
        # 전체 결과
        passed = sum(1 for result in self.results.values() if result.startswith('✅'))
        failed = sum(1 for result in self.results.values() if result.startswith('❌'))
        partial = sum(1 for result in self.results.values() if result.startswith('⚠️'))
        
        print(f"\nOVERALL: {passed} passed, {failed} failed, {partial} partial")
        
        if failed == 0:
            print("🎉 All tests completed successfully!")
        else:
            print("⚠️ Some tests failed. Check logs for details.")

async def test_specific_functionality():
    """특정 기능 세부 테스트"""
    print("\n🔍 Detailed Functionality Tests")
    print("=" * 40)
    
    # 실제 DART 데이터로 테스트
    async with DartCollector() as collector:
        print("1. Fetching real DART data...")
        filings = await collector.get_recent_filings(1)
        
        if not filings:
            print("   ❌ No filings found")
            return
        
        print(f"   ✅ Found {len(filings)} filings")
        
        # 필터링 테스트
        print("\n2. Testing filtering...")
        filter_instance = FilingFilter()
        important_filings = filter_instance.get_important_filings(filings)
        print(f"   ✅ {len(important_filings)} important filings identified")
        
        # 첫 번째 중요 공시로 AI 분석 테스트
        if important_filings:
            print("\n3. Testing AI analysis...")
            test_filing = important_filings[0]
            grade = test_filing.get('grade')
            
            ai_summarizer = AISummarizer()
            
            if grade == 'A':
                analysis = await ai_summarizer.analyze_grade_a_filing(test_filing)
                print("   ✅ A-grade analysis completed")
                print(f"      Revenue: {analysis.get('revenue', 'N/A')}")
                print(f"      Summary: {analysis.get('summary', 'N/A')[:50]}...")
            elif grade == 'B':
                analysis = await ai_summarizer.analyze_grade_b_filing(test_filing)
                print("   ✅ B-grade analysis completed")
                print(f"      Summary: {analysis.get('summary', 'N/A')[:50]}...")
                print(f"      Impact: {analysis.get('investment_impact', 'N/A')}")
            
            # 텔레그램 메시지 포맷 테스트 (실제 전송은 안 함)
            print("\n4. Testing message formatting...")
            telegram_bot = InvestmentTelegramBot()
            
            if grade == 'A':
                message = telegram_bot._format_grade_a_message(test_filing, analysis)
            elif grade == 'B':
                message = telegram_bot._format_grade_b_message(test_filing, analysis)
            else:
                message = telegram_bot._format_dart_message(test_filing)
            
            print("   ✅ Message formatted successfully")
            print(f"   Message length: {len(message)} characters")
            print(f"   Preview: {message[:100]}...")

async def run_live_test():
    """실제 환경에서 라이브 테스트 (알림 발송 포함)"""
    print("\n🚀 LIVE TEST - Will send actual Telegram alerts!")
    
    # 사용자 확인
    response = input("Are you sure you want to run live test? (y/N): ")
    if response.lower() != 'y':
        print("❌ Live test cancelled")
        return
    
    print("🔴 Running live test with alerts...")
    
    try:
        stats = await run_test_pipeline(days_back=1, send_alerts=True)
        print("\n✅ Live test completed!")
        print(f"   Alerts sent: {stats['alerts_sent']}")
        print(f"   Total processed: {stats['total_filings']}")
    except Exception as e:
        print(f"❌ Live test failed: {e}")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DART Analysis Pipeline Test')
    parser.add_argument('--mode', choices=['all', 'specific', 'live'], 
                       default='all', help='Test mode')
    
    args = parser.parse_args()
    
    if args.mode == 'all':
        # 전체 테스트 스위트 실행
        runner = TestRunner()
        asyncio.run(runner.run_all_tests())
    
    elif args.mode == 'specific':
        # 특정 기능 세부 테스트
        asyncio.run(test_specific_functionality())
    
    elif args.mode == 'live':
        # 라이브 테스트 (실제 알림 발송)
        asyncio.run(run_live_test())

if __name__ == "__main__":
    main()