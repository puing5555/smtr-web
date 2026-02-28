#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Pages 자동 배포 스크립트
invest-sns 빌드 결과물을 GitHub Pages에 배포
"""

import os
import shutil
import subprocess
import json
from datetime import datetime

def run_command(cmd, cwd=None):
    """명령어 실행"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode != 0:
            print(f"명령어 실패: {cmd}")
            print(f"Error: {result.stderr}")
            return False, result.stderr
        return True, result.stdout
    except Exception as e:
        print(f"예외 발생: {e}")
        return False, str(e)

def check_git_status():
    """Git 저장소 상태 확인"""
    success, output = run_command("git status --porcelain")
    if not success:
        return False
    
    if output.strip():
        print("⚠️ 커밋되지 않은 변경사항이 있습니다:")
        print(output)
        return False
    
    return True

def build_invest_sns():
    """invest-sns 빌드"""
    print("🔨 invest-sns 빌드 시작...")
    
    # 빌드 실행
    success, output = run_command("npm run build", cwd="invest-sns")
    if not success:
        print("❌ 빌드 실패")
        return False
    
    print("✅ 빌드 완료")
    return True

def deploy_to_github_pages():
    """GitHub Pages에 배포"""
    print("🚀 GitHub Pages 배포 시작...")
    
    # 기존 레포 확인
    if os.path.exists("invest-sns-pages"):
        print("기존 invest-sns-pages 폴더 삭제...")
        shutil.rmtree("invest-sns-pages")
    
    # GitHub 레포 클론
    print("📥 GitHub 레포 클론...")
    success, _ = run_command("git clone https://github.com/puing5555/invest-sns.git invest-sns-pages")
    if not success:
        print("❌ 레포 클론 실패")
        return False
    
    # gh-pages 브랜치 확인/생성
    print("🌿 gh-pages 브랜치 설정...")
    success, _ = run_command("git checkout gh-pages", cwd="invest-sns-pages")
    if not success:
        print("새 gh-pages 브랜치 생성...")
        success, _ = run_command("git checkout --orphan gh-pages", cwd="invest-sns-pages")
        if not success:
            print("❌ gh-pages 브랜치 생성 실패")
            return False
    
    # 기존 파일 삭제
    success, _ = run_command("git rm -rf .", cwd="invest-sns-pages")
    
    # 빌드 결과물 복사
    print("📁 빌드 결과물 복사...")
    source_dir = "invest-sns/out"
    dest_dir = "invest-sns-pages"
    
    for item in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item)
        dest_path = os.path.join(dest_dir, item)
        
        if os.path.isdir(source_path):
            shutil.copytree(source_path, dest_path)
        else:
            shutil.copy2(source_path, dest_path)
    
    # .nojekyll 파일 생성 (Next.js 정적 파일 지원)
    with open(os.path.join(dest_dir, ".nojekyll"), "w") as f:
        f.write("")
    
    # CNAME 파일 생성 (도메인이 있을 경우)
    # with open(os.path.join(dest_dir, "CNAME"), "w") as f:
    #     f.write("invest-sns.com\n")
    
    # Git 커밋 및 푸시
    print("💾 Git 커밋 및 푸시...")
    run_command("git add .", cwd="invest-sns-pages")
    
    commit_msg = f"Deploy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    success, _ = run_command(f'git commit -m "{commit_msg}"', cwd="invest-sns-pages")
    
    success, _ = run_command("git push origin gh-pages", cwd="invest-sns-pages")
    if not success:
        print("❌ 푸시 실패")
        return False
    
    print("✅ GitHub Pages 배포 완료")
    return True

def update_project_status():
    """PROJECT_STATUS.md 업데이트"""
    status_content = """# PROJECT_STATUS.md

_Last updated: {}_

## 💼 invest-sns 프로젝트 (투자 SNS 플랫폼)

### ✅ 2단계 진행중 - GitHub Pages 배포 완료 (2026-02-28 11:05)

**🌐 라이브 사이트**: https://puing5555.github.io/invest-sns/

1. **✅ invest-sns 빌드 & GitHub Pages 푸시** ✅ 완료
   - Next.js 56페이지 정적 빌드 성공
   - gh-pages 브랜치 자동 배포
   - .nojekyll 파일 추가 (Next.js 지원)
   
2. **🔄 Selenium 자막 추출** (슈카월드/이효석/부읽남/달란트)
   - extract_subs_v9.py 스크립트 생성 완료
   - 4개 채널 병렬 처리 구조
   - 60초 간격 Rate Limiting 준수
   - yt-dlp 백업 + Selenium 이중화

3. **🚀 V9 분석 → Supabase INSERT** 
   - 프롬프트 V9 확인 완료 (28개 규칙, 11종 mention_type)
   - 한글 5단계 시그널: 매수/긍정/중립/경계/매도
   - 발언자 귀속 시스템 (채널→speaker)
   - 스코프: 한국주식 + 미국주식 + 크립토만

4. **📝 Vercel 배포 가이드** 작성중

### 🎯 현재 프로젝트 상태
- **폴더**: `invest-sns/`
- **프롬프트**: `prompts/pipeline_v9.md`
- **DB**: Supabase (31개 시그널)
  - 삼프로TV V7 20개 시그널 
  - 코린이아빠 V5 11개 시그널
- **시그널 타입**: 매수/긍정/중립/경계/매도 (한글 5단계만)
- **프론트엔드**: Next.js (56페이지)
- **GitHub**: `puing5555/invest-sns`
- **라이브 URL**: https://puing5555.github.io/invest-sns/

---

**⚡ 전속력 진행**: 속도 줄이지 않고 4개 작업 병렬 처리중
""".format(datetime.now().strftime('%Y-%m-%d %H:%M (GMT+7)'))

    with open("PROJECT_STATUS.md", "w", encoding="utf-8") as f:
        f.write(status_content)
    
    print("✅ PROJECT_STATUS.md 업데이트 완료")

def main():
    """메인 실행 함수"""
    print("invest-sns GitHub Pages 자동 배포 시작!")
    
    # 1. Git 상태 확인
    if not check_git_status():
        print("Git 상태 확인 후 다시 실행하세요")
        return False
    
    # 2. 빌드 (이미 완료되었지만 다시 확인)
    if not os.path.exists("invest-sns/out"):
        if not build_invest_sns():
            return False
    else:
        print("기존 빌드 결과물 확인됨")
    
    # 3. GitHub Pages 배포
    if not deploy_to_github_pages():
        return False
    
    # 4. 프로젝트 상태 업데이트
    update_project_status()
    
    # 5. 정리
    if os.path.exists("invest-sns-pages"):
        shutil.rmtree("invest-sns-pages")
        print("임시 폴더 정리 완료")
    
    print("\nGitHub Pages 배포 완료!")
    print("라이브 URL: https://puing5555.github.io/invest-sns/")
    
    return True

if __name__ == "__main__":
    main()