#!/usr/bin/env python3
"""
Translation Service Test
번역 서비스 테스트
"""
import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.translator import news_translator

async def test_single_translation():
    """단일 제목 번역 테스트"""
    print("Single Translation Test")
    print("-" * 50)
    
    test_titles = [
        "Tesla unveils cheaper Cybertruck model for mass market",
        "Apple reports record Q3 earnings, stock surges 5%",
        "Bitcoin breaks $100,000 resistance level amid ETF optimism",
        "Federal Reserve signals potential rate cut in March",
        "NVIDIA announces new AI chip for autonomous vehicles"
    ]
    
    for title in test_titles:
        try:
            translated = await news_translator.translate_single_title(title)
            print(f"원문: {title}")
            print(f"번역: {translated}")
            print()
        except Exception as e:
            print(f"번역 실패: {title} -> {e}")
            print()

async def test_batch_translation():
    """배치 번역 테스트"""
    print("Batch Translation Test")
    print("-" * 50)
    
    test_titles = [
        "Microsoft acquires AI startup for $2.5 billion",
        "Google faces antitrust lawsuit over search dominance", 
        "Amazon Prime membership fees increase 20% starting next month",
        "Meta launches new VR headset with advanced features",
        "Tesla's Supercharger network expands to 50,000 locations globally"
    ]
    
    try:
        translated_batch = await news_translator.translate_batch(test_titles)
        
        print("배치 번역 결과:")
        for i, (original, translated) in enumerate(zip(test_titles, translated_batch), 1):
            print(f"{i}. 원문: {original}")
            print(f"   번역: {translated}")
            print()
            
    except Exception as e:
        print(f"배치 번역 실패: {e}")

async def test_db_integration():
    """DB 연동 테스트"""
    print("Database Integration Test")
    print("-" * 50)
    
    try:
        # 미번역 US 뉴스 확인
        count = await news_translator.translate_untranslated_news(market='us', limit=5)
        print(f"번역된 US 뉴스: {count}개")
        
        # 미번역 Crypto 뉴스 확인  
        count = await news_translator.translate_untranslated_news(market='crypto', limit=5)
        print(f"번역된 Crypto 뉴스: {count}개")
        
    except Exception as e:
        print(f"DB 통합 테스트 실패: {e}")

async def main():
    """메인 테스트 실행"""
    print("News Translation Service Test")
    print("=" * 60)
    
    # API 키 확인
    if not os.getenv('OPENAI_API_KEY'):
        print("X OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일을 확인해주세요.")
        return
    else:
        print("OK OPENAI_API_KEY 확인됨")
        print()
    
    # 각 테스트 실행
    try:
        await test_single_translation()
        await test_batch_translation() 
        await test_db_integration()
        
        print("=" * 60)
        print("OK 모든 테스트 완료!")
        
    except Exception as e:
        print(f"X 테스트 실행 중 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())