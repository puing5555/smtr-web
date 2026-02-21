#!/usr/bin/env python3
"""
Claude Sonnet을 사용해 코린이 아빠 시그널을 검증하는 스크립트
"""
import json
import os
import glob
from pathlib import Path
import anthropic
from typing import Dict, List, Any
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeSignalVerifier:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"  # 최신 Claude Sonnet 모델
        
    def load_signals(self, signals_path: str) -> List[Dict]:
        """시그널 파일 로드"""
        try:
            with open(signals_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # _deduped_signals.json이 없으면 _signals_with_timestamps.json 시도
            alt_path = signals_path.replace('_deduped_signals.json', '_signals_with_timestamps.json')
            logger.info(f"Primary signals file not found, trying alternative: {alt_path}")
            with open(alt_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def load_subtitle_files(self, subtitle_dirs: List[str]) -> Dict[str, str]:
        """자막 파일들 로드"""
        subtitles = {}
        
        for subtitle_dir in subtitle_dirs:
            if not os.path.exists(subtitle_dir):
                logger.warning(f"Subtitle directory not found: {subtitle_dir}")
                continue
                
            txt_files = glob.glob(os.path.join(subtitle_dir, "*.txt"))
            logger.info(f"Found {len(txt_files)} subtitle files in {subtitle_dir}")
            
            for txt_file in txt_files:
                video_id = Path(txt_file).stem
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:  # 빈 파일이 아닌 경우만 저장
                            subtitles[video_id] = content
                except Exception as e:
                    logger.warning(f"Error reading {txt_file}: {e}")
        
        logger.info(f"Loaded {len(subtitles)} subtitle files total")
        return subtitles
    
    def verify_signal(self, signal: Dict, subtitle: str) -> Dict:
        """Claude Sonnet으로 개별 시그널 검증"""
        prompt = f"""다음은 유튜브 영상에서 GPT-4o-mini가 추출한 투자 시그널입니다. 원본 자막과 비교해서 검증해주세요.

**원본 자막:**
{subtitle[:3000]}...  # 길면 자름

**GPT-4o-mini 추출 결과:**
- 종목: {signal.get('asset', 'N/A')}
- 시그널 타입: {signal.get('signal_type', 'N/A')}
- 내용: {signal.get('content', 'N/A')}
- 신뢰도: {signal.get('confidence', 'N/A')}
- 맥락: {signal.get('context', 'N/A')}

**검증 기준:**
1. 확인됨: GPT 추출이 정확함
2. 수정됨: 틀렸지만 유사한 내용이 있음 (수정 의견 제시)
3. 거부됨: 자막에 해당 내용이 없음

**응답 형식 (JSON):**
{{
    "verdict": "확인됨|수정됨|거부됨",
    "confidence": 0.85,
    "reason": "간결한 이유 (한국어, 50자 이내)",
    "correction": "수정됨인 경우 올바른 내용 (선택사항)"
}}

JSON만 응답해주세요."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # JSON 파싱 시도
            result_text = response.content[0].text.strip()
            
            # JSON 블록에서 내용 추출
            if result_text.startswith('```json'):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith('```'):
                result_text = result_text[3:-3].strip()
            
            result = json.loads(result_text)
            
            # 필수 필드 검증
            if 'verdict' not in result or 'confidence' not in result or 'reason' not in result:
                raise ValueError("Missing required fields in Claude response")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {result_text}")
            return {
                "verdict": "거부됨",
                "confidence": 0.0,
                "reason": "Claude 응답 파싱 오류",
                "correction": None
            }
        except Exception as e:
            logger.error(f"Error verifying signal: {e}")
            return {
                "verdict": "거부됨", 
                "confidence": 0.0,
                "reason": f"검증 오류: {str(e)[:30]}",
                "correction": None
            }
    
    def verify_all_signals(self, signals: List[Dict], subtitles: Dict[str, str]) -> List[Dict]:
        """모든 시그널 검증"""
        results = []
        total = len(signals)
        
        for i, signal in enumerate(signals, 1):
            video_id = signal.get('video_id')
            if not video_id:
                logger.warning(f"Signal {i} has no video_id, skipping")
                continue
            
            if video_id not in subtitles:
                logger.warning(f"No subtitle found for video {video_id}, marking as rejected")
                verification = {
                    "verdict": "거부됨",
                    "confidence": 0.0,
                    "reason": "자막 파일 없음",
                    "correction": None
                }
            else:
                logger.info(f"Verifying signal {i}/{total}: {signal.get('asset')} - {signal.get('signal_type')}")
                verification = self.verify_signal(signal, subtitles[video_id])
                
                # API 레이트 리밋 방지
                time.sleep(0.5)
            
            # 원본 시그널에 검증 결과 추가
            result = signal.copy()
            result['claude_verification'] = verification
            results.append(result)
            
            logger.info(f"Result: {verification['verdict']} (confidence: {verification['confidence']:.2f})")
        
        return results

def main():
    # 환경설정
    env_path = r"C:\Users\Mario\work\invest-engine\.env"
    api_key = None
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('ANTHROPIC_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")
    else:
        raise FileNotFoundError(f".env file not found: {env_path}")
    
    # 파일 경로
    base_dir = r"C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106"
    signals_path = os.path.join(base_dir, "_deduped_signals.json")
    subtitle_dirs = [
        base_dir,
        r"C:\Users\Mario\.openclaw\workspace\smtr_data\corinpapa1106"
    ]
    output_path = os.path.join(base_dir, "_claude_sonnet_verify.json")
    
    # 검증 실행
    verifier = ClaudeSignalVerifier(api_key)
    
    logger.info("Loading signals...")
    signals = verifier.load_signals(signals_path)
    logger.info(f"Loaded {len(signals)} signals")
    
    logger.info("Loading subtitles...")
    subtitles = verifier.load_subtitle_files(subtitle_dirs)
    
    logger.info("Starting verification process...")
    verified_signals = verifier.verify_all_signals(signals, subtitles)
    
    # 결과 저장
    logger.info(f"Saving results to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(verified_signals, f, ensure_ascii=False, indent=2)
    
    # 통계 출력
    stats = {}
    for signal in verified_signals:
        verdict = signal.get('claude_verification', {}).get('verdict', 'unknown')
        stats[verdict] = stats.get(verdict, 0) + 1
    
    logger.info("Verification completed!")
    logger.info("Statistics:")
    for verdict, count in stats.items():
        logger.info(f"  {verdict}: {count}")
    
    logger.info(f"Results saved to: {output_path}")

if __name__ == "__main__":
    main()