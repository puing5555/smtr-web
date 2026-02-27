# 삼프로TV V4 파이프라인 분석 보고서
*분석 시작: 2026-02-27 11:20 GMT+7*

## 채널 정보
- **채널**: 삼프로TV 3PROTV
- **URL**: https://www.youtube.com/@3protv
- **분석 목표**: 최근 영상 30개 투자 관련 신호 추출

## 분석 진행 상황

### ❌ STEP 1: 최근 영상 30개 목록 가져오기
**상태**: 기술적 제약으로 중단
**문제점**:
- 브라우저 제어 서비스 미작동 (Chrome extension relay 연결 필요)
- 웹 검색 API 미설정 (Brave Search API 키 필요)
- YouTube 동적 콘텐츠로 인한 web_fetch 제한

**시도한 방법**:
1. ✗ web_fetch로 /videos 페이지 접근 → JavaScript 콘텐츠 미로드
2. ✗ browser 도구 사용 → 서비스 연결 실패
3. ✗ web_search로 채널 검색 → API 키 미설정

### 필요한 설정
분석을 진행하려면 다음 중 하나가 필요합니다:

1. **브라우저 제어 활성화**:
   ```
   openclaw gateway restart
   Chrome에서 OpenClaw extension 아이콘 클릭하여 탭 연결
   ```

2. **웹 검색 API 설정**:
   ```
   openclaw configure --section web
   또는 BRAVE_API_KEY 환경변수 설정
   ```

3. **대안**: 수동으로 비디오 URL 목록 제공

## V4 분석 규칙 (준비됨)

### 신호 분류 기준
- **결론 종목**: 실제 투자 의견 → 강도별 분류
- **논거 종목**: 비교/예시 사용 → 최대 "긍정"까지
- **뉴스 종목**: 시황 전달 → "중립"

### 시그널 8가지 (V4 규칙)
- STRONG_BUY / BUY / POSITIVE / HOLD / NEUTRAL / CONCERN / SELL / STRONG_SELL

### 게스트 채널 규칙
- 진행자 질문 ≠ 신호 (예: "삼성전자 어떻게 보세요?")
- 게스트 답변만 신호로 분류
- 게스트별 별도 신호 생성

---
*상태: 기술적 제약으로 1단계 중단 - 도구 설정 필요*