#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Pages 자동 배포 스크립트 (Simple 버전)
"""

import os
import shutil
import subprocess
from datetime import datetime

def run_cmd(cmd, cwd=None):
    """명령어 실행"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode != 0:
            print(f"명령어 실패: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"예외 발생: {e}")
        return False

def deploy():
    """배포 실행"""
    print("GitHub Pages 배포 시작...")
    
    # 기존 폴더 삭제
    if os.path.exists("invest-sns-pages"):
        shutil.rmtree("invest-sns-pages")
        print("기존 폴더 삭제 완료")
    
    # 레포 클론
    print("GitHub 레포 클론...")
    if not run_cmd("git clone https://github.com/puing5555/invest-sns.git invest-sns-pages"):
        return False
    
    # gh-pages 브랜치 생성/체크아웃
    print("gh-pages 브랜치 설정...")
    run_cmd("git checkout gh-pages", cwd="invest-sns-pages")
    if not os.path.exists("invest-sns-pages/.git"):
        print("브랜치 생성 실패")
        return False
    
    # 기존 파일 삭제 (git 제외)
    for item in os.listdir("invest-sns-pages"):
        if item != ".git":
            item_path = os.path.join("invest-sns-pages", item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    
    # 빌드 파일 복사
    print("빌드 파일 복사...")
    source_dir = "invest-sns/out"
    dest_dir = "invest-sns-pages"
    
    for item in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item)
        dest_path = os.path.join(dest_dir, item)
        
        if os.path.isdir(source_path):
            shutil.copytree(source_path, dest_path)
        else:
            shutil.copy2(source_path, dest_path)
    
    # .nojekyll 파일 생성
    with open(os.path.join(dest_dir, ".nojekyll"), "w") as f:
        f.write("")
    
    # Git 커밋 및 푸시
    print("Git 커밋 및 푸시...")
    run_cmd("git add .", cwd="invest-sns-pages")
    
    commit_msg = f"Deploy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    run_cmd(f'git commit -m "{commit_msg}"', cwd="invest-sns-pages")
    
    if not run_cmd("git push origin gh-pages", cwd="invest-sns-pages"):
        print("푸시 실패")
        return False
    
    # 정리
    shutil.rmtree("invest-sns-pages")
    
    print("GitHub Pages 배포 완료!")
    print("URL: https://puing5555.github.io/invest-sns/")
    
    return True

if __name__ == "__main__":
    deploy()