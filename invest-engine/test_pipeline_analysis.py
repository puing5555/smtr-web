# -*- coding: utf-8 -*-
"""
파이프라인 분석 테스트 - 실제 공시 데이터에 AI 분석 적용
"""
import asyncio
import sqlite3
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analyzers.ai_summarizer import AISummarizer

async def analyze_recent_filings():
    """최근 공시에 AI 분석 적용 테스트"""
    
    # 데이터베이스 연결
    conn = sqlite3.connect('invest_engine.db')
    cursor = conn.cursor()
    
    # AI 분석이 아직 안 된 최근 공시들 가져오기
    cursor.execute("""
        SELECT id, corp_name, report_nm, rcept_dt, corp_code, rcept_no, stock_code, grade
        FROM dart_filings 
        WHERE ai_summary IS NULL OR ai_summary = ''
        ORDER BY rcept_dt DESC 
        LIMIT 3
    """)
    
    filings = cursor.fetchall()
    
    if not filings:
        print("No filings found that need analysis")
        conn.close()
        return
    
    print(f"Found {len(filings)} filings to analyze")
    
    # AI 분석기 생성
    summarizer = AISummarizer()
    
    for filing in filings:
        filing_id, corp_name, report_nm, rcept_dt, corp_code, rcept_no, stock_code, grade = filing
        
        print(f"\n=== Analyzing Filing ID: {filing_id} ===")
        print(f"Company: {corp_name}")
        print(f"Report: {report_nm}")
        print(f"Grade: {grade}")
        print(f"Date: {rcept_dt}")
        
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
            
            # 등급에 따라 분석 실행
            if grade == 'A':
                result = await summarizer.analyze_grade_a_filing(filing_data)
                
                # A등급 결과를 ai_summary에 JSON으로 저장
                ai_summary = json.dumps(result, ensure_ascii=False)
                
                print("A-grade analysis completed:")
                for key, value in result.items():
                    try:
                        print(f"  {key}: {value}")
                    except UnicodeEncodeError:
                        print(f"  {key}: [Korean text]")
                
            elif grade == 'B':
                result = await summarizer.analyze_grade_b_filing(filing_data)
                
                # B등급 결과를 ai_summary에 JSON으로 저장  
                ai_summary = json.dumps(result, ensure_ascii=False)
                
                print("B-grade analysis completed:")
                for key, value in result.items():
                    try:
                        print(f"  {key}: {value}")
                    except UnicodeEncodeError:
                        print(f"  {key}: [Korean text]")
            else:
                print("Skipping - not A or B grade")
                continue
            
            # 결과를 데이터베이스에 업데이트
            cursor.execute("""
                UPDATE dart_filings 
                SET ai_summary = ?
                WHERE id = ?
            """, (ai_summary, filing_id))
            
            conn.commit()
            print(f"✅ Updated filing ID {filing_id} with AI analysis")
            
        except Exception as e:
            print(f"❌ Failed to analyze filing ID {filing_id}: {e}")
    
    conn.close()
    print(f"\n=== Analysis Complete ===")

async def check_updated_summaries():
    """업데이트된 AI 요약 확인"""
    
    conn = sqlite3.connect('invest_engine.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT corp_name, report_nm, ai_summary
        FROM dart_filings 
        WHERE ai_summary IS NOT NULL AND ai_summary != ''
        ORDER BY rcept_dt DESC 
        LIMIT 3
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    print("\n=== Recent AI Summaries in Database ===")
    for corp_name, report_nm, ai_summary in results:
        print(f"\nCompany: {corp_name}")
        print(f"Report: {report_nm}")
        try:
            summary_data = json.loads(ai_summary)
            print("AI Analysis:")
            for key, value in summary_data.items():
                try:
                    print(f"  {key}: {value}")
                except UnicodeEncodeError:
                    print(f"  {key}: [Korean text]")
        except json.JSONDecodeError:
            print(f"AI Summary: {ai_summary[:100]}...")

if __name__ == "__main__":
    print("Starting pipeline analysis test...")
    asyncio.run(analyze_recent_filings())
    asyncio.run(check_updated_summaries())