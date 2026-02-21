# -*- coding: utf-8 -*-
"""
Simple pipeline test without Unicode issues
"""
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.pipeline import run_test_pipeline

async def simple_test():
    """Simple pipeline test"""
    print("=== DART Analysis Pipeline Test ===")
    
    try:
        # Test pipeline without sending alerts
        stats = await run_test_pipeline(days_back=1, send_alerts=False)
        
        print("Pipeline Test Results:")
        print(f"  Total filings: {stats['total_filings']}")
        print(f"  Grade A: {stats['grade_a']}")  
        print(f"  Grade B: {stats['grade_b']}")
        print(f"  Grade C: {stats['grade_c']}")
        print(f"  Analysis done: {stats['analysis_done']}")
        print(f"  Alerts sent: {stats['alerts_sent']}")
        print(f"  Errors: {stats['errors']}")
        
        if stats['errors'] == 0:
            print("SUCCESS: Pipeline completed without errors!")
        else:
            print(f"WARNING: Pipeline completed with {stats['errors']} errors")
            
    except Exception as e:
        print(f"ERROR: Pipeline failed - {e}")

if __name__ == "__main__":
    asyncio.run(simple_test())