import requests
import json
import random
from collections import Counter, defaultdict

# Supabase 설정
url = "https://arypzhotxflimroprmdk.supabase.co"
service_role_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

headers = {
    "apikey": service_role_key,
    "Authorization": f"Bearer {service_role_key}",
    "Content-Type": "application/json"
}

# 스피커 정보 조회
print("스피커 정보 조회 중...")
speaker_url = f"{url}/rest/v1/speakers"
speaker_response = requests.get(speaker_url, headers=headers, params={"select": "id,name"})
speaker_map = {}
if speaker_response.status_code == 200:
    speakers = speaker_response.json()
    speaker_map = {s['id']: s['name'] for s in speakers}

# 비디오 정보 조회 (제한적으로)
print("비디오 정보 조회 중...")
video_url = f"{url}/rest/v1/videos"
video_response = requests.get(video_url, headers=headers, params={"select": "id,title", "limit": "1000"})
video_map = {}
if video_response.status_code == 200:
    videos = video_response.json()
    video_map = {v['id']: v['title'] for v in videos}

# 매수 시그널 전체 조회
api_url = f"{url}/rest/v1/influencer_signals"
params = {
    "signal": "eq.매수",
    "select": "id,speaker_id,video_id,stock,signal,key_quote,timestamp,confidence,created_at",
    "order": "created_at.desc"
}

print("매수 시그널 전체 조회 중...")
response = requests.get(api_url, headers=headers, params=params)

if response.status_code == 200:
    buy_signals = response.json()
    total_count = len(buy_signals)
    print(f"총 매수 시그널 개수: {total_count}")
    
    # 스피커별 분포
    speaker_counts = Counter()
    for signal in buy_signals:
        speaker_id = signal['speaker_id']
        speaker_name = speaker_map.get(speaker_id, f"Unknown({speaker_id[:8]})")
        speaker_counts[speaker_name] += 1
    
    # 랜덤 50개 샘플링 (스피커별 비례)
    sample_signals = []
    total_sample = min(50, total_count)
    
    # 각 스피커별로 비례해서 샘플링
    remaining_sample = total_sample
    for speaker_name, count in speaker_counts.most_common():
        if remaining_sample <= 0:
            break
            
        speaker_sample_size = max(1, min(remaining_sample, int(count * total_sample / total_count)))
        speaker_signals = [s for s in buy_signals if speaker_map.get(s['speaker_id'], '') == speaker_name]
        
        if len(speaker_signals) <= speaker_sample_size:
            sample_signals.extend(speaker_signals)
        else:
            sample_signals.extend(random.sample(speaker_signals, speaker_sample_size))
            
        remaining_sample -= len([s for s in sample_signals if speaker_map.get(s['speaker_id'], '') == speaker_name])
    
    # 부족하면 랜덤하게 추가
    if len(sample_signals) < total_sample:
        remaining_signals = [s for s in buy_signals if s not in sample_signals]
        additional_count = min(total_sample - len(sample_signals), len(remaining_signals))
        sample_signals.extend(random.sample(remaining_signals, additional_count))
    
    print(f"샘플링된 시그널 개수: {len(sample_signals)}")
    
    # 개선된 분석 로직
    analysis_results = {
        '진짜_매수': [],
        '단순_긍정': [],
        '애매': []
    }
    
    # 더 포괄적인 매수 키워드들 (실제 데이터 기반)
    strong_buy_keywords = [
        # 직접적 매수 표현
        '매수', '사야', '담아', '사들여', '잡아', '가져가',
        # 타이밍 관련
        '타이밍', '기회', '진입', '저가', '바닥', '싸게', '할인',
        # 비중/포지션 관련
        '비중', '확대', '늘려', '올려', '증가', '포지션',
        # 추천 관련
        '추천', '권유', '제안',
        # 기타 매수 의도
        '확장', '투자', '관심 가져', '주목해', '눈여겨'
    ]
    
    # 단순 긍정 키워드들
    positive_keywords = [
        '좋은 회사', '성장 가능성', '전망 밝', '긍정적', '유망', '잠재력',
        '기대', '성장성', '괜찮', '주목할', '관심 있', '흥미로운'
    ]
    
    # 부정/경고 키워드들
    negative_keywords = [
        '위험', '주의', '조심', '경계', '안 사', '사지 마', '피해야', 
        '매도', '팔아', '줄여', '감소', '축소', '빼라'
    ]
    
    # 각 시그널 분석
    for signal in sample_signals:
        speaker_name = speaker_map.get(signal['speaker_id'], 'Unknown')
        video_title = video_map.get(signal['video_id'], 'Unknown')
        key_quote = signal['key_quote']
        
        # 분석 로직
        combined_text = f"{key_quote} {video_title}".lower()
        
        # 키워드 매칭
        strong_buy_matches = [k for k in strong_buy_keywords if k in combined_text]
        positive_matches = [k for k in positive_keywords if k in combined_text]
        negative_matches = [k for k in negative_keywords if k in combined_text]
        
        analysis_item = {
            'id': signal['id'],
            'speaker': speaker_name,
            'stock': signal['stock'],
            'key_quote': key_quote,
            'video_title': video_title,
            'confidence': signal['confidence'],
            'strong_buy_matches': strong_buy_matches,
            'positive_matches': positive_matches,
            'negative_matches': negative_matches
        }
        
        # 분류 로직
        if negative_matches:
            analysis_results['애매'].append(analysis_item)
        elif strong_buy_matches:
            analysis_results['진짜_매수'].append(analysis_item)
        elif positive_matches:
            analysis_results['단순_긍정'].append(analysis_item)
        else:
            analysis_results['애매'].append(analysis_item)
    
    # 결과 출력
    total_sample_count = len(sample_signals)
    real_buy_count = len(analysis_results['진짜_매수'])
    positive_only_count = len(analysis_results['단순_긍정'])
    ambiguous_count = len(analysis_results['애매'])
    
    print(f"\n=== 최종 분석 결과 ===")
    print(f"전체 매수 시그널: {total_count}개")
    print(f"샘플 분석 ({total_sample_count}개):")
    print(f"  [O] 진짜 매수: {real_buy_count}개 ({real_buy_count/total_sample_count*100:.1f}%)")
    print(f"  [X] 단순 긍정: {positive_only_count}개 ({positive_only_count/total_sample_count*100:.1f}%)")
    print(f"  [?] 애매: {ambiguous_count}개 ({ambiguous_count/total_sample_count*100:.1f}%)")
    
    # 스피커별 정확도
    print(f"\n=== 스피커별 정확도 ===")
    speaker_accuracy = defaultdict(lambda: {'real': 0, 'total': 0})
    for category, items in analysis_results.items():
        for item in items:
            speaker_accuracy[item['speaker']]['total'] += 1
            if category == '진짜_매수':
                speaker_accuracy[item['speaker']]['real'] += 1
    
    for speaker, stats in sorted(speaker_accuracy.items()):
        if stats['total'] > 0:
            accuracy = stats['real'] / stats['total'] * 100
            print(f"  {speaker}: {stats['real']}/{stats['total']} ({accuracy:.1f}%)")
    
    # 오분류 사례 (단순 긍정 + 애매)
    print(f"\n=== 오분류 사례 TOP 10 ===")
    misclassified = analysis_results['단순_긍정'] + analysis_results['애매']
    for i, item in enumerate(misclassified[:10]):
        print(f"{i+1}. [{item['speaker']}] {item['stock']}")
        print(f"    발언: {item['key_quote'][:100]}...")
        print(f"    매수키워드: {item['strong_buy_matches']}")
        print(f"    긍정키워드: {item['positive_matches']}")
        print()
    
    # 진짜 매수 사례
    print(f"\n=== 진짜 매수 사례 TOP 10 ===")
    for i, item in enumerate(analysis_results['진짜_매수'][:10]):
        print(f"{i+1}. [{item['speaker']}] {item['stock']}")
        print(f"    발언: {item['key_quote'][:100]}...")
        print(f"    매칭 키워드: {item['strong_buy_matches']}")
        print()
    
    # 결과 저장
    result_data = {
        'timestamp': '2026-03-05',
        'total_buy_signals': total_count,
        'sample_size': total_sample_count,
        'analysis_summary': {
            '진짜_매수': {'count': real_buy_count, 'percentage': real_buy_count/total_sample_count*100},
            '단순_긍정': {'count': positive_only_count, 'percentage': positive_only_count/total_sample_count*100},
            '애매': {'count': ambiguous_count, 'percentage': ambiguous_count/total_sample_count*100}
        },
        'speaker_accuracy': dict(speaker_accuracy),
        'detailed_results': analysis_results
    }
    
    with open('final_buy_signal_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n최종 분석 결과를 final_buy_signal_analysis.json에 저장했습니다.")

else:
    print(f"에러: {response.status_code} - {response.text}")