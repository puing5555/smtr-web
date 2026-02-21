# -*- coding: utf-8 -*-
"""
수정된 AI 분석기 테스트 - 실제 재무 데이터 가져오기 테스트
"""
import asyncio
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analyzers.ai_summarizer import AISummarizer

async def test_real_financial_data():
    """실제 공시 데이터로 재무 분석 테스트"""
    
    # 데이터베이스에서 최신 공시 데이터 가져오기
    conn = sqlite3.connect('invest_engine.db')
    cursor = conn.cursor()
    
    # A등급 공시 중 최신 데이터 하나 가져오기
    cursor.execute("""
        SELECT corp_name, report_nm, rcept_dt, corp_code, rcept_no, stock_code
        FROM dart_filings 
        WHERE grade = 'A' AND corp_code IS NOT NULL
        ORDER BY rcept_dt DESC 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print("No A-grade filing found in database")
        return
    
    # 테스트용 공시 데이터 생성
    test_filing = {
        'corp_name': result[0],
        'report_nm': result[1], 
        'rcept_dt': result[2],
        'corp_code': result[3],
        'rcept_no': result[4],
        'stock_code': result[5]
    }
    
    print("=== Testing with real filing data ===")
    print(f"Company: {test_filing['corp_name']}")
    print(f"Report: {test_filing['report_nm']}")
    print(f"Date: {test_filing['rcept_dt']}")
    print(f"Corp Code: {test_filing['corp_code']}")
    print("")
    
    # AI 분석기 생성 및 분석 실행
    summarizer = AISummarizer()
    
    print("Starting analysis...")
    result = await summarizer.analyze_grade_a_filing(test_filing)
    
    print("\n=== Analysis Result ===")
    for key, value in result.items():
        print(f"{key}: {value}")

async def test_dart_financial_api():
    """DART 재무 API 직접 테스트"""
    
    summarizer = AISummarizer()
    
    print("=== Testing DART Financial API directly ===")
    
    # 티맥스소프트 데이터로 테스트 (corp_code: 00340111)
    corp_code = "00340111"
    bsns_year = "2024"  # 2024년 데이터
    reprt_code = "11011"  # 사업보고서
    
    print(f"Fetching financial data for corp_code: {corp_code}, year: {bsns_year}")
    
    financial_data = await summarizer.get_financial_data(corp_code, bsns_year, reprt_code)
    
    if financial_data:
        print("\n=== Financial Data Found ===")
        for key, value in financial_data.items():
            print(f"{key}: {value}")
            
        # 포맷팅된 결과도 출력
        print("\n=== Formatted Results ===")
        revenue = summarizer._format_amount(financial_data.get('revenue', '0'))
        revenue_prev = summarizer._format_amount(financial_data.get('revenue_prev', '0'))
        revenue_change = summarizer._calculate_change_rate(
            financial_data.get('revenue', '0'), 
            financial_data.get('revenue_prev', '0')
        )
        print(f"매출액: {revenue} (전년: {revenue_prev}, 변동률: {revenue_change})")
        
    else:
        print("No financial data found")

if __name__ == "__main__":
    # 두 가지 테스트 실행
    print("Starting DART Financial API tests...\n")
    asyncio.run(test_dart_financial_api())
    print("\n" + "="*50 + "\n")
    asyncio.run(test_real_financial_data())