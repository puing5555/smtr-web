# -*- coding: utf-8 -*-
"""
기존 공시를 새로운 재무 API 방식으로 재분석
"""
import asyncio
import sqlite3
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analyzers.ai_summarizer import AISummarizer

async def reanalyze_a_grade_filings():
    """A등급 공시를 재무 API로 재분석"""
    
    # 데이터베이스 연결
    conn = sqlite3.connect('invest_engine.db')
    cursor = conn.cursor()
    
    # A등급 공시 중 corp_code가 있는 것들 가져오기
    cursor.execute("""
        SELECT id, corp_name, report_nm, rcept_dt, corp_code, rcept_no, stock_code, ai_summary
        FROM dart_filings 
        WHERE grade = 'A' AND corp_code IS NOT NULL
        ORDER BY rcept_dt DESC 
        LIMIT 3
    """)
    
    filings = cursor.fetchall()
    
    if not filings:
        print("No A-grade filings found")
        conn.close()
        return
    
    print(f"Found {len(filings)} A-grade filings to reanalyze with financial data")
    
    # AI 분석기 생성
    summarizer = AISummarizer()
    
    for filing in filings:
        filing_id, corp_name, report_nm, rcept_dt, corp_code, rcept_no, stock_code, old_ai_summary = filing
        
        print(f"\n=== Re-analyzing Filing ID: {filing_id} ===")
        print(f"Company: {corp_name}")
        print(f"Report: {report_nm}")
        print(f"Date: {rcept_dt}")
        print(f"Corp Code: {corp_code}")
        
        # 기존 AI 요약 출력
        print(f"\n--- Previous Summary ---")
        if old_ai_summary:
            try:
                old_data = json.loads(old_ai_summary)
                if 'summary' in old_data:
                    print(f"Old: {old_data['summary'][:100]}...")
            except:
                print(f"Old: {old_ai_summary[:100]}...")
        
        try:
            # 공시 데이터 준비
            filing_data = {
                'corp_name': corp_name,
                'report_nm': report_nm,
                'rcept_dt': rcept_dt,
                'corp_code': corp_code,
                'rcept_no': rcept_no,
                'stock_code': stock_code
            }
            
            # 새로운 방식으로 분석 실행
            print("\n--- New Analysis with Financial Data ---")
            result = await summarizer.analyze_grade_a_filing(filing_data)
            
            # 결과를 ai_summary에 JSON으로 저장
            new_ai_summary = json.dumps(result, ensure_ascii=False)
            
            print("New analysis completed:")
            for key, value in result.items():
                try:
                    if key == 'summary':
                        print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")
                except UnicodeEncodeError:
                    print(f"  {key}: [Korean text]")
            
            # 실제 재무 데이터가 사용되었는지 확인
            has_real_data = (
                result.get('revenue') != '정보 없음' and 
                result.get('operating_profit') != '정보 없음'
            )
            
            if has_real_data:
                print("✅ Real financial data was used!")
                
                # 데이터베이스 업데이트
                cursor.execute("""
                    UPDATE dart_filings 
                    SET ai_summary = ?
                    WHERE id = ?
                """, (new_ai_summary, filing_id))
                
                conn.commit()
                print(f"✅ Updated filing ID {filing_id} with new financial analysis")
            else:
                print("⚠️ No financial data available, used fallback method")
            
        except Exception as e:
            print(f"❌ Failed to reanalyze filing ID {filing_id}: {e}")
    
    conn.close()
    print(f"\n=== Reanalysis Complete ===")

async def show_before_after():
    """재분석 전후 비교"""
    
    conn = sqlite3.connect('invest_engine.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT corp_name, report_nm, ai_summary
        FROM dart_filings 
        WHERE grade = 'A' AND ai_summary IS NOT NULL
        ORDER BY rcept_dt DESC 
        LIMIT 2
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    print("\n=== Updated AI Summaries ===")
    for corp_name, report_nm, ai_summary in results:
        print(f"\n📊 {corp_name} - {report_nm}")
        try:
            summary_data = json.loads(ai_summary)
            
            # 매출, 영업이익, 순이익 정보 출력
            revenue = summary_data.get('revenue', 'N/A')
            operating_profit = summary_data.get('operating_profit', 'N/A')
            summary_text = summary_data.get('summary', 'N/A')
            
            print(f"  매출액: {revenue}")
            print(f"  영업이익: {operating_profit}")
            try:
                print(f"  AI 분석: {summary_text}")
            except UnicodeEncodeError:
                print(f"  AI 분석: [Korean text - encoding issue]")
                
        except json.JSONDecodeError:
            print(f"  Raw summary: {ai_summary[:200]}...")

if __name__ == "__main__":
    print("Starting financial data reanalysis...")
    asyncio.run(reanalyze_a_grade_filings())
    asyncio.run(show_before_after())