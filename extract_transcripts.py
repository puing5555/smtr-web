from youtube_transcript_api import YouTubeTranscriptApi
import json
import sys

video_ids = [
    "6R1HiMUAQkM",  # 심텍·기아·SK스퀘어·쿼드메디슨·한국전력
    "RdAzQQJUvRU",  # 랠리는 아직 끝나지 않았다
    "8-hYd-8eojE",  # 자금 흐름이 바뀌고 있다
    "qYAiv0Kljas",  # 현대그룹주, 외국인이 쐈다
    "XFHD_1M3Mxg",  # 외국인 관광객, 신세계 따라간다
    "ldT75QwBB6g"   # 6천피 시대! 반도체 다음 주자는 화학?
]

video_titles = [
    "심텍·기아·SK스퀘어·쿼드메디슨·한국전력 | 차영주 와이즈경제연구소 소장",
    "랠리는 아직 끝나지 않았다. 포트폴리오 전략 | 이재규 SK증권 PB차장",
    "자금 흐름이 바뀌고 있다. 코스닥 상승 싸이클 | 장우진 작가",
    "[마감시황] 현대그룹주, 외국인이 쐈다 | 홍선애, 김장열, 이권희",
    "외국인 관광객, 신세계 따라간다 | 김동훈, 여도은, 허재무",
    "6천피 시대! 반도체 다음 주자는 화학? | 박지훈, 여도은, 허재무"
]

for i, video_id in enumerate(video_ids):
    try:
        print(f"Extracting transcript for: {video_titles[i]}")
        
        # 한국어 자막 우선 시도, 없으면 자동 생성된 한국어 자막 시도
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_manually_created_transcript(['ko'])
        except:
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript = transcript_list.find_generated_transcript(['ko'])
            except:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript = transcript_list.find_transcript(['ko'])
        
        transcript_data = transcript.fetch()
        
        # 자막을 텍스트로 변환
        full_text = ""
        for entry in transcript_data:
            timestamp = f"{int(entry['start']//60):02d}:{int(entry['start']%60):02d}"
            full_text += f"[{timestamp}] {entry['text']}\n"
        
        # 파일로 저장
        filename = f"C:/Users/Mario/work/subs/{video_id}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        print(f"Success - saved to {filename}")
        
    except Exception as e:
        print(f"Error: {e}")
    print("---")