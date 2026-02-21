"""
News Translation Service
OpenAI GPT-4o-mini를 사용한 영문 뉴스 제목 번역/요약 서비스
"""
import openai
import asyncio
import json
from typing import List, Dict, Optional
from loguru import logger
import os
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..config.settings import settings
from ..db.database import get_db_session
from ..db.models import News


class NewsTranslator:
    """뉴스 번역/요약 서비스"""
    
    def __init__(self):
        self.openai_client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment")
        else:
            self.openai_client = openai.AsyncOpenAI(api_key=self.api_key)
    
    async def translate_batch(self, titles: List[str], batch_size: int = 15) -> List[str]:
        """
        영문 뉴스 제목들을 배치로 번역
        
        Args:
            titles: 번역할 영문 제목 리스트
            batch_size: 한 번에 번역할 제목 개수
            
        Returns:
            번역된 한글 제목 리스트
        """
        if not self.openai_client:
            logger.error("OpenAI client not initialized")
            return ["번역 서비스 이용불가"] * len(titles)
        
        if not titles:
            return []
        
        translated_titles = []
        
        # 배치 단위로 처리
        for i in range(0, len(titles), batch_size):
            batch = titles[i:i + batch_size]
            
            try:
                batch_result = await self._translate_batch_internal(batch)
                translated_titles.extend(batch_result)
                
                # API 요청 제한 고려하여 잠시 대기
                if i + batch_size < len(titles):
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"배치 번역 실패: {e}")
                # 실패한 배치는 원문 그대로 추가
                translated_titles.extend(batch)
        
        return translated_titles
    
    async def _translate_batch_internal(self, titles: List[str]) -> List[str]:
        """
        내부 배치 번역 메서드
        """
        titles_json = json.dumps(titles, ensure_ascii=False)
        
        prompt = f"""다음 영문 뉴스 제목들을 한국어로 자연스럽게 번역해주세요. 
투자/금융 용어는 한국 투자자들에게 친숙한 표현을 사용하세요.

영문 제목들:
{titles_json}

응답 형식: JSON 배열로 번역된 제목들만 반환
예시: ["테슬라, 3분기 실적 예상 상회", "애플, 신제품 발표 예정"]

번역 규칙:
- 회사명은 한국어로 번역 (Tesla → 테슬라, Apple → 애플)
- 금융 용어는 한국식 표현 (earnings → 실적, shares → 주가, market → 시장)
- 간결하고 이해하기 쉽게 번역
- 원본의 의미와 뉘앙스 보존"""
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 전문 금융 번역가입니다. 영문 뉴스 제목을 정확하고 자연스러운 한국어로 번역합니다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        try:
            content = response.choices[0].message.content.strip()
            
            # JSON 파싱 시도
            if content.startswith('[') and content.endswith(']'):
                translated = json.loads(content)
            else:
                # JSON 형태가 아닌 경우 파싱 시도
                content = content.replace('```json', '').replace('```', '').strip()
                translated = json.loads(content)
            
            # 길이 검증
            if len(translated) != len(titles):
                logger.warning(f"번역 결과 개수 불일치: {len(titles)} -> {len(translated)}")
                # 부족한 부분은 원문으로 채움
                while len(translated) < len(titles):
                    translated.append(titles[len(translated)])
            
            return translated[:len(titles)]
            
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"번역 결과 파싱 실패: {e}, content: {content}")
            return titles  # 실패시 원문 반환
    
    async def translate_untranslated_news(self, market: str = None, limit: int = 50) -> int:
        """
        번역되지 않은 뉴스들을 일괄 번역
        
        Args:
            market: 'us' 또는 'crypto' (None이면 둘 다)
            limit: 한 번에 처리할 최대 뉴스 개수
            
        Returns:
            번역된 뉴스 개수
        """
        if not self.openai_client:
            logger.error("OpenAI API 키가 설정되지 않음")
            return 0
        
        db = get_db_session()
        
        try:
            # 번역 대상 뉴스 조회
            query = db.query(News).filter(
                and_(
                    News.ai_summary.is_(None),  # 번역되지 않은 것
                    News.title.isnot(None)      # 제목이 있는 것
                )
            )
            
            if market:
                query = query.filter(News.market == market)
            else:
                query = query.filter(News.market.in_(['us', 'crypto']))
            
            news_list = query.limit(limit).all()
            
            if not news_list:
                logger.info("번역할 뉴스가 없음")
                return 0
            
            logger.info(f"번역 대상 뉴스: {len(news_list)}개")
            
            # 제목 추출
            titles = [news.title for news in news_list]
            
            # 번역 실행
            translated_titles = await self.translate_batch(titles)
            
            # DB 업데이트
            updated_count = 0
            for news, translated_title in zip(news_list, translated_titles):
                if translated_title and translated_title != news.title:
                    news.ai_summary = translated_title
                    updated_count += 1
                    logger.debug(f"번역: {news.title} -> {translated_title}")
            
            db.commit()
            logger.info(f"뉴스 번역 완료: {updated_count}개")
            
            return updated_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"뉴스 번역 중 오류: {e}")
            raise
        finally:
            db.close()
    
    async def translate_single_title(self, title: str) -> str:
        """
        단일 제목 번역 (테스트용)
        """
        if not title:
            return ""
        
        result = await self.translate_batch([title])
        return result[0] if result else title


# 전역 인스턴스
news_translator = NewsTranslator()


async def translate_news_batch(market: str = None, limit: int = 50) -> int:
    """
    번역 서비스 진입점
    """
    return await news_translator.translate_untranslated_news(market=market, limit=limit)


async def translate_title(title: str) -> str:
    """
    단일 제목 번역 진입점
    """
    return await news_translator.translate_single_title(title)