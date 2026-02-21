# -*- coding: utf-8 -*-
"""
DART 공시 필터링 시스템
공시를 A/B/C 등급으로 분류하는 모듈
"""
from enum import Enum
from typing import Dict, List, Tuple
from loguru import logger
import re

class FilingGrade(Enum):
    """공시 등급"""
    A = "A"  # 정기공시 (사업보고서, 반기보고서, 분기보고서)
    B = "B"  # 중요 비정기공시
    C = "C"  # 기타 공시

class FilingFilter:
    """공시 필터링 클래스"""
    
    def __init__(self):
        # A등급: 정기공시 키워드
        self.grade_a_keywords = [
            "사업보고서", "반기보고서", "분기보고서"
        ]
        
        # B등급: 중요 비정기공시 키워드
        self.grade_b_keywords = [
            "자기주식", "유상증자", "무상증자", "임원변경", "최대주주", 
            "합병", "분할", "CB", "BW", "전환사채", "주요사항보고", 
            "중요한계약", "영업양수도", "지분변동", "주식매수선택권",
            "신주인수권부사채", "교환사채", "감자", "주식분할",
            "타법인주식", "출자", "투자", "계열회사", "관계회사",
            "재무제표", "감사보고서", "외부감사", "회계처리기준",
            "대표이사", "등기임원", "감사위원", "사외이사"
        ]
    
    def classify_filing(self, filing: Dict) -> Tuple[FilingGrade, str]:
        """
        공시 등급 분류
        
        Args:
            filing: DART 공시 정보 딕셔너리
            
        Returns:
            Tuple[FilingGrade, str]: (등급, 분류 이유)
        """
        report_nm = filing.get('report_nm', '').strip()
        corp_name = filing.get('corp_name', '')
        
        logger.debug(f"Classifying filing: {corp_name} - {report_nm}")
        
        # A등급 체크: 정기공시
        for keyword in self.grade_a_keywords:
            if keyword in report_nm:
                reason = f"정기공시 키워드 '{keyword}' 포함"
                logger.info(f"Grade A: {corp_name} - {reason}")
                return FilingGrade.A, reason
        
        # B등급 체크: 중요 비정기공시
        for keyword in self.grade_b_keywords:
            if keyword in report_nm:
                reason = f"중요 공시 키워드 '{keyword}' 포함"
                logger.info(f"Grade B: {corp_name} - {reason}")
                return FilingGrade.B, reason
        
        # C등급: 나머지
        reason = "일반 공시"
        logger.debug(f"Grade C: {corp_name} - {reason}")
        return FilingGrade.C, reason
    
    def filter_filings_by_grade(self, filings: List[Dict], target_grades: List[FilingGrade]) -> List[Dict]:
        """
        특정 등급의 공시만 필터링
        
        Args:
            filings: 공시 리스트
            target_grades: 원하는 등급 리스트
            
        Returns:
            List[Dict]: 필터링된 공시 리스트 (grade와 reason 추가됨)
        """
        filtered_filings = []
        
        for filing in filings:
            grade, reason = self.classify_filing(filing)
            
            if grade in target_grades:
                # 원본 filing에 등급 정보 추가
                filing_with_grade = filing.copy()
                filing_with_grade['grade'] = grade.value
                filing_with_grade['grade_reason'] = reason
                filtered_filings.append(filing_with_grade)
        
        logger.info(f"Filtered {len(filtered_filings)} filings from {len(filings)} total")
        return filtered_filings
    
    def get_grade_a_filings(self, filings: List[Dict]) -> List[Dict]:
        """A등급 공시만 추출"""
        return self.filter_filings_by_grade(filings, [FilingGrade.A])
    
    def get_grade_b_filings(self, filings: List[Dict]) -> List[Dict]:
        """B등급 공시만 추출"""
        return self.filter_filings_by_grade(filings, [FilingGrade.B])
    
    def get_grade_c_filings(self, filings: List[Dict]) -> List[Dict]:
        """C등급 공시만 추출"""
        return self.filter_filings_by_grade(filings, [FilingGrade.C])
    
    def get_important_filings(self, filings: List[Dict]) -> List[Dict]:
        """A+B등급 (중요) 공시만 추출"""
        return self.filter_filings_by_grade(filings, [FilingGrade.A, FilingGrade.B])
    
    def analyze_filing_distribution(self, filings: List[Dict]) -> Dict[str, int]:
        """
        공시 등급별 분포 분석
        
        Args:
            filings: 공시 리스트
            
        Returns:
            Dict[str, int]: 등급별 개수
        """
        distribution = {"A": 0, "B": 0, "C": 0}
        
        for filing in filings:
            grade, _ = self.classify_filing(filing)
            distribution[grade.value] += 1
        
        logger.info(f"Filing distribution: A={distribution['A']}, B={distribution['B']}, C={distribution['C']}")
        return distribution

# 테스트용 함수들
def test_filing_filter():
    """필터링 테스트"""
    # 테스트 데이터
    test_filings = [
        {"corp_name": "삼성전자", "report_nm": "사업보고서", "rcept_no": "20240001"},
        {"corp_name": "LG전자", "report_nm": "분기보고서", "rcept_no": "20240002"},
        {"corp_name": "현대차", "report_nm": "자기주식 취득 신탁계약 체결", "rcept_no": "20240003"},
        {"corp_name": "SK하이닉스", "report_nm": "유상증자 결정", "rcept_no": "20240004"},
        {"corp_name": "네이버", "report_nm": "정정신고서", "rcept_no": "20240005"},
        {"corp_name": "카카오", "report_nm": "주주총회소집공고", "rcept_no": "20240006"},
    ]
    
    filter_instance = FilingFilter()
    
    print("\n=== 공시 필터링 테스트 ===")
    for filing in test_filings:
        grade, reason = filter_instance.classify_filing(filing)
        print(f"{filing['corp_name']} - {filing['report_nm']}")
        print(f"  → {grade.value}등급: {reason}\n")
    
    print("=== 등급별 분포 ===")
    distribution = filter_instance.analyze_filing_distribution(test_filings)
    print(f"A등급 (정기공시): {distribution['A']}건")
    print(f"B등급 (중요공시): {distribution['B']}건") 
    print(f"C등급 (일반공시): {distribution['C']}건")
    
    print("\n=== 중요 공시 (A+B) ===")
    important_filings = filter_instance.get_important_filings(test_filings)
    for filing in important_filings:
        print(f"- {filing['corp_name']}: {filing['report_nm']} ({filing['grade']}등급)")

if __name__ == "__main__":
    test_filing_filter()