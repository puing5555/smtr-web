"""
DART (Data Analysis, Retrieval and Transfer System) API collector
공시정보 수집 모듈
"""
import httpx
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
import pytz
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..db.database import get_db_session
from ..db.models import DartFiling, AlertsLog

class DartCollector:
    """DART 공시 정보 수집기"""
    
    def __init__(self):
        self.api_key = settings.DART_API_KEY
        self.base_url = settings.DART_BASE_URL
        self.session = None
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def get_recent_filings(self, days_back: int = 1) -> List[Dict]:
        """
        최근 공시 정보 조회
        
        Args:
            days_back: 조회할 일수 (기본 1일)
            
        Returns:
            공시 정보 리스트
        """
        if not self.api_key:
            logger.warning("DART API key not configured")
            return []
            
        # 조회 날짜 설정 (한국시간 기준)
        kst = pytz.timezone('Asia/Seoul')
        end_date = datetime.now(kst)
        start_date = end_date - timedelta(days=days_back)
        
        params = {
            'crtfc_key': self.api_key,
            'bgn_de': start_date.strftime('%Y%m%d'),
            'end_de': end_date.strftime('%Y%m%d'),
            'pblntf_ty': 'A',  # 정기공시: A, 주요사항보고: B, 발행공시: C, 지분공시: D, 기타공시: E
        }
        
        try:
            response = await self.session.get(
                f"{self.base_url}/list.json",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != '000':
                logger.error(f"DART API error: {data.get('message')}")
                return []
                
            return data.get('list', [])
            
        except Exception as e:
            logger.error(f"Failed to fetch DART filings: {e}")
            return []
    
    async def collect_and_store_filings(self, days_back: int = 1) -> int:
        """
        공시 정보 수집하여 DB에 저장
        
        Args:
            days_back: 조회할 일수
            
        Returns:
            저장된 공시 개수
        """
        filings = await self.get_recent_filings(days_back)
        if not filings:
            return 0
            
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
                    rm=filing_data.get('rm', '')
                )
                
                db.add(filing)
                new_filings += 1
                
                logger.info(f"New DART filing: {filing.corp_name} - {filing.report_nm}")
                
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to store DART filings: {e}")
            
        finally:
            db.close()
            
        return new_filings
    
    def get_important_filing_keywords(self) -> List[str]:
        """
        중요한 공시 키워드 목록
        
        Returns:
            중요 키워드 리스트
        """
        return [
            '증자', '감자', '분할', '합병', 
            '중요한계약', '영업양수도', 
            '주요사항보고서', '정정신고서',
            '자기주식', '임원변경',
            '재무제표', '감사보고서',
            '유상증자', '무상증자',
            '주식매수선택권', 'CB', 'BW'
        ]
    
    def is_important_filing(self, filing: Dict) -> bool:
        """
        중요한 공시인지 판단
        
        Args:
            filing: 공시 정보
            
        Returns:
            중요 공시 여부
        """
        report_name = filing.get('report_nm', '')
        keywords = self.get_important_filing_keywords()
        
        return any(keyword in report_name for keyword in keywords)
    
    async def get_filing_detail(self, rcept_no: str) -> Optional[Dict]:
        """
        공시 상세 정보 조회
        
        Args:
            rcept_no: 접수번호
            
        Returns:
            공시 상세 정보
        """
        if not self.api_key:
            return None
            
        params = {
            'crtfc_key': self.api_key,
            'rcept_no': rcept_no
        }
        
        try:
            response = await self.session.get(
                f"{self.base_url}/document.json",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != '000':
                logger.error(f"DART API error: {data.get('message')}")
                return None
                
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch filing detail: {e}")
            return None

# Helper function for manual testing
async def test_dart_collector():
    """DART 수집기 테스트"""
    async with DartCollector() as collector:
        filings = await collector.get_recent_filings(1)
        logger.info(f"Found {len(filings)} filings")
        
        for filing in filings[:5]:  # Show first 5
            logger.info(f"- {filing.get('corp_name')}: {filing.get('report_nm')}")

if __name__ == "__main__":
    # Test run
    asyncio.run(test_dart_collector())