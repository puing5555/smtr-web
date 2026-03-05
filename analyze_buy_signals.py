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

# 먼저 speaker 테이블에서 speaker_id와 name 매핑 조회
print("스피커 정보 조회 중...")
speaker_url = f"{url}/rest/v1/speakers"
speaker_response = requests.get(speaker_url, headers=headers, params={"select": "id,name"})

speaker_map = {}
if speaker_response.status_code == 200:
    speakers = speaker_response.json()
    speaker_map = {s['id']: s['name'] for s in speakers}
    print(f"스피커 {len(speaker_map)}명 정보 로드됨")

# video 테이블에서 video_id와 title 매핑 조회
print("비디오 정보 조회 중...")
video_url = f"{url}/rest/v1/videos"
video_response = requests.get(video_url, headers=headers, params={"select": "id,title,published_at"})

video_map = {}
if video_response.status_code == 200:
    videos = video_response.json()
    video_map = {v['id']: {'title': v['title'], 'published_at': v['published_at']} for v in videos}
    print(f"비디오 {len(video_map)}개 정보 로드됨")

# 매수 시그널 조회
api_url = f"{url}/rest/v1/influencer_signals"
params = {
    "signal": "eq.매수",
    "select": "id,speaker_id,video_id,stock,signal,key_quote,timestamp,confidence,created_at",
    "order": "created_at.desc"
}

print("매수 시그널 데이터 조회 중...")
response = requests.get(api_url, headers=headers, params=params)

if response.status_code == 200:
    buy_signals = response.json()
    total_count = len(buy_signals)
    print(f"총 매수 시그널 개수: {total_count}")
    
    # 스피커별 분포 확인
    speaker_counts = Counter()
    for signal in buy_signals:
        speaker_id = signal['speaker_id']
        speaker_name = speaker_map.get(speaker_id, f"Unknown({speaker_id[:8]})")
        speaker_counts[speaker_name] += 1
    
    print(f"\n스피커별 매수 시그널 분포:")
    for speaker, count in speaker_counts.most_common():
        print(f"  {speaker}: {count}개")
    
    # 랜덤 50개 샘플링 (스피커별 골고루 분포)
    sample_signals = []
    
    # 각 스피커별로 비례해서 샘플링
    total_sample = min(50, total_count)
    for speaker_name, count in speaker_counts.items():
        # 비례 계산
        speaker_sample_size = max(1, int(count * total_sample / total_count))
        speaker_signals = [s for s in buy_signals if speaker_map.get(s['speaker_id'], '') == speaker_name]
        
        if len(speaker_signals) <= speaker_sample_size:
            sample_signals.extend(speaker_signals)
        else:
            sample_signals.extend(random.sample(speaker_signals, speaker_sample_size))
    
    # 50개를 넘으면 랜덤하게 줄이기
    if len(sample_signals) > 50:
        sample_signals = random.sample(sample_signals, 50)
    
    print(f"\n샘플링된 시그널 개수: {len(sample_signals)}")
    
    # 분석 결과
    analysis_results = {
        '진짜_매수': [],
        '단순_긍정': [],
        '애매': []
    }
    
    # 매수 추천 키워드들
    strong_buy_keywords = ['사야한다', '매수 추천', '비중 확대', '저가 매수', '담아라', '사들여라', 
                          '매수하세요', '사세요', '매수타이밍', '지금 사', '추천 매수', '살 때']
    positive_keywords = ['좋은 회사', '성장 가능성', '관심', '전망 밝', '긍정적', '괜찮', '주목',
                        '기대', '잠재력', '성장성', '유망']
    
    # 각 시그널 분석
    for i, signal in enumerate(sample_signals):
        speaker_name = speaker_map.get(signal['speaker_id'], 'Unknown')
        video_info = video_map.get(signal['video_id'], {'title': 'Unknown', 'published_at': 'Unknown'})
        key_quote = signal['key_quote']
        video_title = video_info['title']
        
        # 분석 로직
        combined_text = f"{key_quote} {video_title}".lower()
        
        has_strong_buy = any(keyword in combined_text for keyword in strong_buy_keywords)
        has_positive_only = any(keyword in combined_text for keyword in positive_keywords)
        
        analysis_item = {
            'id': signal['id'],
            'speaker': speaker_name,
            'stock': signal['stock'],
            'key_quote': key_quote,
            'video_title': video_title,
            'published_at': video_info['published_at'],
            'confidence': signal['confidence']
        }
        
        if has_strong_buy:
            analysis_results['진짜_매수'].append(analysis_item)
        elif has_positive_only and not has_strong_buy:
            analysis_results['단순_긍정'].append(analysis_item)
        else:
            analysis_results['애매'].append(analysis_item)
    
    # 결과 출력
    total_sample_count = len(sample_signals)
    real_buy_count = len(analysis_results['진짜_매수'])
    positive_only_count = len(analysis_results['단순_긍정'])
    ambiguous_count = len(analysis_results['애매'])
    
    print(f"\n=== 분석 결과 ===")
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
    
    for speaker, stats in speaker_accuracy.items():
        accuracy = stats['real'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"  {speaker}: {stats['real']}/{stats['total']} ({accuracy:.1f}%)")
    
    # 오분류 사례 (단순 긍정으로 분류된 것들)
    print(f"\n=== 오분류 사례 TOP 10 ===")
    misclassified = analysis_results['단순_긍정'] + analysis_results['애매']
    for i, item in enumerate(misclassified[:10]):
        print(f"{i+1}. [{item['speaker']}] {item['stock']}")
        print(f"    발언: {item['key_quote'][:100]}...")
        print(f"    영상: {item['video_title'][:80]}...")
        print()
    
    # 결과를 JSON으로 저장
    result_data = {
        'total_buy_signals': total_count,
        'sample_size': total_sample_count,
        'analysis': {
            '진짜_매수': {'count': real_buy_count, 'percentage': real_buy_count/total_sample_count*100},
            '단순_긍정': {'count': positive_only_count, 'percentage': positive_only_count/total_sample_count*100},
            '애매': {'count': ambiguous_count, 'percentage': ambiguous_count/total_sample_count*100}
        },
        'speaker_accuracy': dict(speaker_accuracy),
        'misclassified_examples': misclassified[:10],
        'all_samples': sample_signals
    }
    
    with open('buy_signal_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"분석 결과를 buy_signal_analysis.json에 저장했습니다.")

else:
    print(f"에러: {response.status_code} - {response.text}")