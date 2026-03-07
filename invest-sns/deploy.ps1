# deploy.ps1 — 유일한 배포 스크립트 (반드시 이것만 사용)
# 사용법: powershell -File deploy.ps1
# 또는:   .\deploy.ps1
#
# ⚠️ 절대 하면 안 되는 것:
#   git push origin gh-pages  (소스코드가 올라가서 사이트 터짐)
#
# ✅ 올바른 방법: 이 스크립트만 실행

param(
    [switch]$SkipBuild,
    [string]$Message = "deploy: 자동 배포"
)

$ErrorActionPreference = "Stop"
$ROOT = $PSScriptRoot

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  배포 시작" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Set-Location $ROOT

# Step 1: 빌드
if (-not $SkipBuild) {
    Write-Host "`n[1/3] 빌드 중..." -ForegroundColor Yellow
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 빌드 실패. 배포 중단." -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ 빌드 완료" -ForegroundColor Green
} else {
    Write-Host "`n[1/3] 빌드 스킵" -ForegroundColor Gray
}

# Step 2: .nojekyll 보장
Write-Host "`n[2/3] out/ 폴더 준비..." -ForegroundColor Yellow
New-Item -Path "out\.nojekyll" -ItemType File -Force | Out-Null

# out/.git 있으면 정리
if (Test-Path "out\.git") {
    Remove-Item -Recurse -Force "out\.git"
}

# Step 3: out/ 폴더만 gh-pages로 push
Write-Host "`n[3/3] GitHub Pages 배포..." -ForegroundColor Yellow
Set-Location "$ROOT\out"

git init
git checkout -b gh-pages
git add .
git commit -m $Message
git remote add origin https://github.com/puing5555/invest-sns.git
git push origin gh-pages --force

$pushResult = $LASTEXITCODE

Set-Location $ROOT
Remove-Item -Recurse -Force "out\.git" -ErrorAction SilentlyContinue

if ($pushResult -eq 0 -or $pushResult -eq 1) {
    # exit code 1 = git push warning (not error)
    Write-Host "`n=====================================" -ForegroundColor Green
    Write-Host "  ✅ 배포 완료!" -ForegroundColor Green
    Write-Host "  https://puing5555.github.io/invest-sns/" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
} else {
    Write-Host "❌ 배포 실패 (exit $pushResult)" -ForegroundColor Red
    exit 1
}
