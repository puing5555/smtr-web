# -*- coding: utf-8 -*-
"""
AI 분석 모듈
OpenAI GPT-4o-mini를 사용하여 DART 공시 내용을 분석하고 요약
"""
import httpx
import asyncio
from typing import Dict, Optional, Tuple
from loguru import logger
import os
from datetime import datetime
import re

import json

def _parse_json_response(text: str) -> dict:
    """Parse JSON from GPT response, stripping markdown code blocks if present."""
    cleaned = re.sub(r'^```(?:json)?\s*', '', text.strip())
    cleaned = re.sub(r'\s*```$', '', cleaned)
    return json.loads(cleaned)

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Will use mock mode.")

from ..config.settings import settings

class MockAISummarizer:
    """OpenAI API가 없을 때 사용하는 목업 클래스"""
    
    async def analyze_grade_a_filing(self, filing: Dict, content: str) -> Dict[str, str]:
        """A등급 공시 목업 분석"""
        corp_name = filing.get('corp_name', 'Unknown')
        report_nm = filing.get('report_nm', '')
        
        return {
            'revenue': '123.4B KRW',
            'revenue_prev': '110.0B KRW',
            'revenue_change': '+12.2%',
            'operating_profit': '15.6B KRW', 
            'operating_profit_prev': '12.0B KRW',
            'operating_profit_change': '+30.0%',
            'net_profit': '9.8B KRW',
            'net_profit_prev': '8.5B KRW', 
            'net_profit_change': '+15.3%',
            'summary': f"[Mock] {corp_name} {report_nm} - Overall positive performance improvement"
        }
    
    async def analyze_grade_b_filing(self, filing: Dict, content: str) -> Dict[str, str]:
        """B등급 공시 목업 분석"""
        corp_name = filing.get('corp_name', 'Unknown')
        report_nm = filing.get('report_nm', '')
        
        return {
            'summary': f"[Mock] {corp_name} {report_nm} - Key changes expected.",
            'key_points': "- Major business changes\n- Financial structure improvement\n- Management changes",
            'investment_impact': "Neutral - Need to monitor from long-term perspective"
        }

class AISummarizer:
    """AI 분석 클래스"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        # 테스트용으로 목업 모드 강제 활성화 (유효한 API 키가 없으면)
        self.use_mock = not (OPENAI_AVAILABLE and self.openai_api_key and self.openai_api_key != 'your_openai_api_key_here')
        
        if self.use_mock:
            logger.warning("Using mock AI summarizer (no OpenAI API key or library)")
            self.mock = MockAISummarizer()
        else:
            self.client = AsyncOpenAI(api_key=self.openai_api_key)
            logger.info("Using OpenAI GPT-4o-mini for analysis")
    
    async def get_filing_content(self, rcept_no: str) -> Optional[str]:
        """
        DART API에서 공시 본문 내용 가져오기 (기존 방식)
        
        Args:
            rcept_no: 접수번호
            
        Returns:
            Optional[str]: 공시 본문 내용
        """
        if not settings.DART_API_KEY:
            logger.error("DART API key not configured")
            return None
        
        # DART document API 호출
        url = "https://opendart.fss.or.kr/api/document.xml"
        params = {
            'crtfc_key': settings.DART_API_KEY,
            'rcept_no': rcept_no
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                # XML 응답에서 텍스트 추출 (간단한 파싱)
                content = response.text
                
                # HTML 태그 제거 및 정리
                content = re.sub(r'<[^>]+>', '', content)
                content = re.sub(r'\s+', ' ', content).strip()
                
                # 너무 길면 앞부분만 (토큰 제한 고려)
                if len(content) > 8000:
                    content = content[:8000] + "..."
                
                return content
                
        except Exception as e:
            logger.error(f"Failed to fetch filing content for {rcept_no}: {e}")
            return None
    
    async def get_financial_data(self, corp_code: str, bsns_year: str, reprt_code: str) -> Optional[Dict]:
        """
        DART API에서 단일회사 재무제표 데이터 가져오기
        
        Args:
            corp_code: 회사 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY)
            reprt_code: 보고서 코드 (11011:사업보고서, 11012:반기보고서, 11013:1분기보고서, 11014:3분기보고서)
            
        Returns:
            Optional[Dict]: 재무제표 데이터
        """
        if not settings.DART_API_KEY:
            logger.error("DART API key not configured")
            return None
        
        # DART 재무제표 API 호출
        url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"
        params = {
            'crtfc_key': settings.DART_API_KEY,
            'corp_code': corp_code,
            'bsns_year': bsns_year,
            'reprt_code': reprt_code
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # API 응답 상태 확인
                if data.get('status') != '000':
                    logger.warning(f"DART API error: {data.get('message', 'Unknown error')}")
                    return None
                
                # 재무데이터 리스트
                financial_list = data.get('list', [])
                if not financial_list:
                    logger.warning(f"No financial data found for corp_code: {corp_code}")
                    return None
                
                # 주요 재무 지표 추출
                financial_data = {}
                
                for item in financial_list:
                    account_nm = item.get('account_nm', '')
                    thstrm_amount = item.get('thstrm_amount', '0')  # 당기금액
                    frmtrm_amount = item.get('frmtrm_amount', '0')  # 전기금액
                    
                    # 매출액 (여러 표현 가능)
                    if any(keyword in account_nm for keyword in ['매출액', '수익', '매출']):
                        if not financial_data.get('revenue'):
                            financial_data['revenue'] = thstrm_amount
                            financial_data['revenue_prev'] = frmtrm_amount
                    
                    # 영업이익 
                    elif '영업이익' in account_nm:
                        if not financial_data.get('operating_profit'):
                            financial_data['operating_profit'] = thstrm_amount  
                            financial_data['operating_profit_prev'] = frmtrm_amount
                    
                    # 당기순이익
                    elif any(keyword in account_nm for keyword in ['당기순이익', '순이익']):
                        if not financial_data.get('net_profit'):
                            financial_data['net_profit'] = thstrm_amount
                            financial_data['net_profit_prev'] = frmtrm_amount
                
                logger.info(f"Successfully fetched financial data for corp_code: {corp_code}")
                return financial_data
                
        except Exception as e:
            logger.error(f"Failed to fetch financial data for {corp_code}: {e}")
            return None
    
    def _get_report_code(self, report_nm: str) -> str:
        """
        보고서명에 따라 DART API 보고서 코드 반환
        
        Args:
            report_nm: 보고서명
            
        Returns:
            str: 보고서 코드
        """
        if '사업보고서' in report_nm:
            return '11011'
        elif '반기보고서' in report_nm:
            return '11012' 
        elif '1분기보고서' in report_nm:
            return '11013'
        elif '3분기보고서' in report_nm:
            return '11014'
        else:
            # 기본값은 사업보고서
            return '11011'
    
    def _format_amount(self, amount_str: str) -> str:
        """
        금액 문자열을 읽기 쉬운 형태로 포맷
        
        Args:
            amount_str: 금액 문자열 (예: "123456789012")
            
        Returns:
            str: 포맷된 금액 (예: "1,235억원")
        """
        try:
            # 콤마와 음수 기호 제거
            amount_str = amount_str.replace(',', '').replace('-', '')
            amount = int(amount_str)
            
            if amount == 0:
                return "0원"
            
            # 억 단위로 변환
            if amount >= 100000000:  # 1억 이상
                billion = amount / 100000000
                return f"{billion:,.1f}억원"
            elif amount >= 10000:  # 1만 이상
                thousand = amount / 10000
                return f"{thousand:,.1f}만원"
            else:
                return f"{amount:,}원"
                
        except (ValueError, TypeError):
            return "정보 없음"
    
    def _calculate_change_rate(self, current: str, previous: str) -> str:
        """
        변동률 계산
        
        Args:
            current: 당기 금액
            previous: 전기 금액
            
        Returns:
            str: 변동률 (예: "+15.3%" or "-5.2%")
        """
        try:
            current_val = int(current.replace(',', '').replace('-', ''))
            previous_val = int(previous.replace(',', '').replace('-', ''))
            
            if previous_val == 0:
                return "정보 없음"
            
            change_rate = ((current_val - previous_val) / previous_val) * 100
            
            if change_rate > 0:
                return f"+{change_rate:.1f}%"
            else:
                return f"{change_rate:.1f}%"
                
        except (ValueError, TypeError):
            return "정보 없음"
    
    async def analyze_grade_a_filing(self, filing: Dict, content: str = None) -> Dict[str, str]:
        """
        A등급 공시 분석 (정기공시 - 매출/영업익/순이익 추출)
        
        Args:
            filing: 공시 정보
            content: 공시 본문 (None이면 자동으로 가져옴)
            
        Returns:
            Dict[str, str]: 분석 결과
        """
        if self.use_mock:
            return await self.mock.analyze_grade_a_filing(filing, content)
        
        corp_name = filing.get('corp_name', 'Unknown')
        report_nm = filing.get('report_nm', '')
        stock_code = filing.get('stock_code', '')
        rcept_dt = filing.get('rcept_dt', '')
        corp_code = filing.get('corp_code', '')  # 회사 고유번호
        
        # 1. 먼저 DART API에서 실제 재무 데이터 가져오기 시도
        financial_data = None
        if corp_code and rcept_dt:
            try:
                # 보고서명에서 사업연도 추출 (예: "사업보고서 (2025.12)" → 2025)
                import re as _re
                year_match = _re.search(r'\((\d{4})\.\d{2}\)', report_nm)
                if year_match:
                    bsns_year = year_match.group(1)
                else:
                    # 접수일 기준 전년도 (보통 이전 연도 실적)
                    bsns_year = str(int(rcept_dt[:4]) - 1) if len(rcept_dt) >= 4 else str(datetime.now().year - 1)
                reprt_code = self._get_report_code(report_nm)
                
                logger.info(f"Fetching financial data: corp_code={corp_code}, year={bsns_year}, report={reprt_code}")
                financial_data = await self.get_financial_data(corp_code, bsns_year, reprt_code)
                
            except Exception as e:
                logger.warning(f"Failed to fetch financial data for {corp_name}: {e}")
        
        # 2. 재무데이터가 있으면 포맷팅해서 사용
        if financial_data:
            logger.info(f"Using actual financial data for {corp_name}")
            
            # 실제 재무 데이터를 포맷팅
            revenue = self._format_amount(financial_data.get('revenue', '0'))
            revenue_prev = self._format_amount(financial_data.get('revenue_prev', '0'))
            revenue_change = self._calculate_change_rate(
                financial_data.get('revenue', '0'), 
                financial_data.get('revenue_prev', '0')
            )
            
            operating_profit = self._format_amount(financial_data.get('operating_profit', '0'))
            operating_profit_prev = self._format_amount(financial_data.get('operating_profit_prev', '0'))
            operating_profit_change = self._calculate_change_rate(
                financial_data.get('operating_profit', '0'),
                financial_data.get('operating_profit_prev', '0')
            )
            
            net_profit = self._format_amount(financial_data.get('net_profit', '0'))
            net_profit_prev = self._format_amount(financial_data.get('net_profit_prev', '0'))
            net_profit_change = self._calculate_change_rate(
                financial_data.get('net_profit', '0'),
                financial_data.get('net_profit_prev', '0')
            )
            
            # GPT에게 실제 재무 데이터와 함께 분석 요청
            financial_summary = f"""
실제 재무 데이터:
• 매출액: {revenue} (전년: {revenue_prev}, 변동률: {revenue_change})
• 영업이익: {operating_profit} (전년: {operating_profit_prev}, 변동률: {operating_profit_change}) 
• 순이익: {net_profit} (전년: {net_profit_prev}, 변동률: {net_profit_change})
"""
            
            prompt = f"""
{corp_name} (종목코드: {stock_code})의 {report_nm} 실적 데이터입니다.
접수일: {rcept_dt}

{financial_summary}

위 실제 재무 데이터를 바탕으로 투자자 관점에서 의미 있는 한줄평을 작성해주세요.
단순한 "IT 분야 기업입니다" 같은 뻔한 내용이 아닌, 실적 수치를 바탕으로 한 구체적인 분석을 부탁합니다.

응답은 반드시 다음 형태의 JSON만 출력하세요:
{{
    "revenue": "{revenue}",
    "revenue_prev": "{revenue_prev}",
    "revenue_change": "{revenue_change}",
    "operating_profit": "{operating_profit}",
    "operating_profit_prev": "{operating_profit_prev}",
    "operating_profit_change": "{operating_profit_change}",
    "net_profit": "{net_profit}",
    "net_profit_prev": "{net_profit_prev}",
    "net_profit_change": "{net_profit_change}",
    "summary": "실적을 바탕으로 한 AI 분석 한줄평"
}}
"""
            
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=600
                )
                
                result_text = response.choices[0].message.content.strip()
                result = _parse_json_response(result_text)
                
                logger.info(f"Successfully analyzed A-grade filing with financial data: {corp_name}")
                return result
                
            except Exception as e:
                logger.error(f"Failed to analyze with GPT for {corp_name}: {e}")
                # GPT 실패시 직접 계산한 데이터 반환
                return {
                    'revenue': revenue,
                    'revenue_prev': revenue_prev,
                    'revenue_change': revenue_change,
                    'operating_profit': operating_profit,
                    'operating_profit_prev': operating_profit_prev,
                    'operating_profit_change': operating_profit_change,
                    'net_profit': net_profit,
                    'net_profit_prev': net_profit_prev,
                    'net_profit_change': net_profit_change,
                    'summary': f'{corp_name} 실적: 매출 {revenue_change}, 영업이익 {operating_profit_change}, 순이익 {net_profit_change}'
                }
        
        # 3. 재무데이터가 없으면 기존 방식으로 폴백
        else:
            logger.warning(f"No financial data available for {corp_name}, using fallback method")
            
            # 공시 본문 가져오기 (기존 방식)
            if content is None:
                rcept_no = filing.get('rcept_no')
                if rcept_no:
                    content = await self.get_filing_content(rcept_no)
                else:
                    content = ""
            
            content_section = ""
            if content and content != "내용을 가져올 수 없습니다.":
                content_section = f"\n공시 본문:\n{content}\n"
            else:
                content_section = "\n(본문 데이터 없음 - 공시명과 회사 정보를 기반으로 분석해주세요)\n"
                logger.warning(f"No content available for {corp_name} - using metadata only")
            
            # GPT 프롬프트 (기존 방식)
            prompt = f"""
다음은 {corp_name} (종목코드: {stock_code})의 {report_nm} 공시 정보입니다.
접수일: {rcept_dt}
{content_section}

위 공시를 분석하여 다음 정보를 JSON 형태로 제공해주세요.
본문이 없는 경우, 공시명과 회사 정보를 기반으로 초보 투자자에게 도움이 되는 한줄평을 작성해주세요.

1. 매출액 (revenue)
2. 전년 매출액 (revenue_prev) 
3. 매출 변동률 (revenue_change, 예: +15.3% 또는 -5.2%)
4. 영업이익 (operating_profit)
5. 전년 영업이익 (operating_profit_prev)
6. 영업이익 변동률 (operating_profit_change)
7. 순이익 (net_profit)
8. 전년 순이익 (net_profit_prev)
9. 순이익 변동률 (net_profit_change)
10. AI 한줄평 (summary, 실적에 대한 간단한 평가)

정보가 없으면 "정보 없음"으로 표시하세요.
모든 금액은 "1,234억원" 형태로 표시하고, 변동률은 "+12.3%" 또는 "-5.2%" 형태로 표시하세요.

응답은 반드시 다음 형태의 JSON만 출력하세요:
{{
    "revenue": "매출액",
    "revenue_prev": "전년 매출액",
    "revenue_change": "매출 변동률",
    "operating_profit": "영업이익", 
    "operating_profit_prev": "전년 영업이익",
    "operating_profit_change": "영업이익 변동률",
    "net_profit": "순이익",
    "net_profit_prev": "전년 순이익",
    "net_profit_change": "순이익 변동률",
    "summary": "AI 한줄평"
}}
"""
            
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=800
                )
                
                result_text = response.choices[0].message.content.strip()
                result = _parse_json_response(result_text)
                
                logger.info(f"Successfully analyzed A-grade filing (fallback): {corp_name}")
                return result
                
            except Exception as e:
                logger.error(f"Failed to analyze A-grade filing {corp_name}: {e}")
                # 에러시 기본값 반환
                return {
                    'revenue': '정보 없음',
                    'revenue_prev': '정보 없음',
                    'revenue_change': '정보 없음',
                    'operating_profit': '정보 없음',
                    'operating_profit_prev': '정보 없음',
                    'operating_profit_change': '정보 없음',
                    'net_profit': '정보 없음',
                    'net_profit_prev': '정보 없음',
                    'net_profit_change': '정보 없음',
                    'summary': '분석 중 오류가 발생했습니다.'
                }
    
    async def analyze_grade_b_filing(self, filing: Dict, content: str = None) -> Dict[str, str]:
        """
        B등급 공시 분석 (중요 비정기공시 - 핵심 내용 + 투자 영향)
        
        Args:
            filing: 공시 정보  
            content: 공시 본문
            
        Returns:
            Dict[str, str]: 분석 결과
        """
        if self.use_mock:
            return await self.mock.analyze_grade_b_filing(filing, content)
        
        # 공시 본문 가져오기
        if content is None:
            rcept_no = filing.get('rcept_no')
            if rcept_no:
                content = await self.get_filing_content(rcept_no)
            else:
                content = ""
        
        if not content:
            logger.warning(f"No content available for {filing.get('corp_name')} analysis")
            content = "내용을 가져올 수 없습니다."
        
        corp_name = filing.get('corp_name', 'Unknown')
        report_nm = filing.get('report_nm', '')
        
        # GPT 프롬프트  
        prompt = f"""
다음은 {corp_name}의 {report_nm} 공시 내용입니다.

{content}

위 공시 내용을 분석하여 다음 정보를 JSON 형태로 제공해주세요:

1. 핵심 요약 (summary): 공시의 주요 내용을 2-3줄로 요약
2. 주요 포인트 (key_points): 중요한 내용을 불릿 포인트로 나열  
3. 투자 영향 분석 (investment_impact): 이 공시가 투자자에게 미치는 영향 (긍정적/부정적/중립적)

응답은 반드시 다음 형태의 JSON만 출력하세요:
{{
    "summary": "핵심 요약 내용",
    "key_points": "• 주요 포인트 1\\n• 주요 포인트 2\\n• 주요 포인트 3",
    "investment_impact": "투자 영향 분석"
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=600
            )
            
            result_text = response.choices[0].message.content.strip()
            result = _parse_json_response(result_text)
            
            logger.info(f"Successfully analyzed B-grade filing: {corp_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze B-grade filing {corp_name}: {e}")
            # 에러시 기본값 반환
            return {
                'summary': '공시 내용 분석 중 오류가 발생했습니다.',
                'key_points': '• 분석 실패',
                'investment_impact': '분석 불가'
            }

# 테스트 함수
async def test_ai_summarizer():
    """AI 분석기 테스트"""
    summarizer = AISummarizer()
    
    # 테스트 공시 데이터
    test_filing_a = {
        'corp_name': '삼성전자',
        'report_nm': '사업보고서', 
        'rcept_no': 'test123'
    }
    
    test_filing_b = {
        'corp_name': 'LG전자',
        'report_nm': '자기주식 취득 결정',
        'rcept_no': 'test456'
    }
    
    print("=== A grade filing analysis test ===")
    result_a = await summarizer.analyze_grade_a_filing(test_filing_a, "test content")
    for key, value in result_a.items():
        print(f"{key}: {value}")
    
    print("\n=== B grade filing analysis test ===")
    result_b = await summarizer.analyze_grade_b_filing(test_filing_b, "test content") 
    for key, value in result_b.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_ai_summarizer())