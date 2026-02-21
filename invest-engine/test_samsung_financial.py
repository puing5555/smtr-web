# -*- coding: utf-8 -*-
"""
삼성전자 재무 데이터로 DART API 테스트
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analyzers.ai_summarizer import AISummarizer

async def test_samsung_financial():
    """삼성전자 재무 데이터 테스트"""
    
    summarizer = AISummarizer()
    
    print("=== Testing DART Financial API with Samsung Electronics ===")
    
    # 삼성전자 corp_code: 00126380
    corp_code = "00126380"
    bsns_year = "2023"  # 2023년 데이터 (확실히 있을 것)
    reprt_code = "11011"  # 사업보고서
    
    print(f"Fetching Samsung financial data: {corp_code}, year: {bsns_year}")
    
    financial_data = await summarizer.get_financial_data(corp_code, bsns_year, reprt_code)
    
    if financial_data:
        print("\n=== Samsung Financial Data Found ===")
        for key, value in financial_data.items():
            print(f"{key}: {value}")
            
        # 포맷팅된 결과도 출력
        print("\n=== Formatted Samsung Results ===")
        revenue = summarizer._format_amount(financial_data.get('revenue', '0'))
        revenue_prev = summarizer._format_amount(financial_data.get('revenue_prev', '0'))
        revenue_change = summarizer._calculate_change_rate(
            financial_data.get('revenue', '0'), 
            financial_data.get('revenue_prev', '0')
        )
        
        operating_profit = summarizer._format_amount(financial_data.get('operating_profit', '0'))
        operating_profit_prev = summarizer._format_amount(financial_data.get('operating_profit_prev', '0'))
        operating_profit_change = summarizer._calculate_change_rate(
            financial_data.get('operating_profit', '0'),
            financial_data.get('operating_profit_prev', '0')
        )
        
        print(f"매출액: {revenue} (전년: {revenue_prev}, 변동률: {revenue_change})")
        print(f"영업이익: {operating_profit} (전년: {operating_profit_prev}, 변동률: {operating_profit_change})")
        
        # 삼성전자 가상 공시로 AI 분석 테스트
        print("\n=== Testing AI Analysis with Samsung data ===")
        
        test_filing = {
            'corp_name': '삼성전자',
            'report_nm': '사업보고서',
            'rcept_dt': '20240315',
            'corp_code': corp_code,
            'rcept_no': 'test123',
            'stock_code': '005930'
        }
        
        result = await summarizer.analyze_grade_a_filing(test_filing)
        
        print("\n=== Samsung AI Analysis Result ===")
        for key, value in result.items():
            try:
                print(f"{key}: {value}")
            except UnicodeEncodeError:
                print(f"{key}: [Korean text - encoding issue]")
        
    else:
        print("No Samsung financial data found")
        
        # 다른 연도들도 시도해보기
        print("\n=== Trying other years ===")
        for year in ["2022", "2021", "2020"]:
            print(f"Trying year: {year}")
            data = await summarizer.get_financial_data(corp_code, year, reprt_code)
            if data:
                print(f"Found data for {year}!")
                break
            else:
                print(f"No data for {year}")

if __name__ == "__main__":
    asyncio.run(test_samsung_financial())