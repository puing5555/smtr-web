"""
스케줄러 테스트 스크립트
"""
import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scheduler import auto_scheduler

async def test_scheduler():
    """스케줄러 기능 테스트"""
    print("🚀 Auto Collection Scheduler Test Starting...")
    
    # 스케줄러 시작
    await auto_scheduler.start()
    
    # 상태 확인
    status = auto_scheduler.get_scheduler_status()
    print(f"\n📊 Scheduler Status:")
    print(f"  - Running: {status['running']}")
    print(f"  - Total Jobs: {status['total_jobs']}")
    
    print(f"\n📅 Scheduled Jobs:")
    for job in status['jobs']:
        print(f"  - {job['name']}: {job['next_run']}")
    
    print(f"\n⏱️  Waiting 10 seconds...")
    await asyncio.sleep(10)
    
    # 스케줄러 중지
    await auto_scheduler.stop()
    print(f"\n✅ Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_scheduler())