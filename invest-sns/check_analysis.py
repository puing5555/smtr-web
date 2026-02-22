#!/usr/bin/env python3
"""분석 결과 확인"""
import requests
import json

response = requests.get("http://localhost:8901/api/opus4-analysis")
analysis_data = response.json()

print("=== 분석 결과 확인 ===")
for signal_id, data in analysis_data.items():
    print(f"\n시그널 ID: {signal_id}")
    print(f"상태: {data.get('status', 'N/A')}")
    
    if 'error' in data:
        print(f"오류: {data['error']}")
    
    if 'raw_response' in data:
        print(f"원본 응답 (처음 500자):\n{data['raw_response'][:500]}...")
        
    print("-" * 50)