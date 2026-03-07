# DEPLOYMENT.md — GitHub Pages 배포 가이드

## 🚨 배포 규칙 — 반드시 준수

```
❌ 절대 금지: git push origin gh-pages    ← 소스코드 올라가서 사이트 파괴
❌ 절대 금지: git add -A → commit → push  ← 위와 동일

✅ 유일한 올바른 배포 방법:
   powershell -File deploy.ps1
```

서브에이전트 포함 모든 작업자가 반드시 위 방법만 사용.

---

## 배포 방법

### 기본 배포 (빌드 포함)
```powershell
.\deploy.ps1
```

### 빌드 스킵 (이미 빌드된 경우)
```powershell
.\deploy.ps1 -SkipBuild
```

### 커밋 메시지 지정
```powershell
.\deploy.ps1 -Message "deploy: 포트폴리오 페이지 추가"
```

---

## 왜 이 방식인가?

GitHub Pages는 `gh-pages` 브랜치의 **루트**를 서빙한다.
- `out/` 폴더 안의 빌드 결과물만 올라가야 함
- 소스코드가 올라가면 README.md가 메인 페이지가 됨 = 사이트 파괴

`deploy.ps1`은 `out/` 폴더에서 git init → commit → push 하는 방식으로
빌드 결과물만 gh-pages 브랜치에 올린다.
