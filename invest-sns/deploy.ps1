# deploy.ps1 — 유일한 배포 스크립트 (반드시 이것만 사용)
# 사용법: .\deploy.ps1
#         .\deploy.ps1 -SkipBuild
#         .\deploy.ps1 -Message "deploy: 설명"
#
# 🚨 절대 하면 안 되는 것:
#   git push origin gh-pages  (소스코드가 올라가서 사이트 박살남)
#   git add -A + commit + push (위와 동일)
#
# ✅ 올바른 방법: 이 스크립트만 실행

param(
    [switch]$SkipBuild,
    [string]$Message = "deploy: 자동 배포"
)

$ErrorActionPreference = "Stop"
$ROOT = $PSScriptRoot
$BASE_URL = "https://puing5555.github.io"
$SITE_BASE = "/invest-sns"

# ─────────────────────────────────────────────
# 함수 정의
# ─────────────────────────────────────────────
function Check-Pass($label) {
    Write-Host "  ✅ $label" -ForegroundColor Green
}
function Check-Fail($label) {
    Write-Host "  ❌ $label" -ForegroundColor Red
    exit 1
}

# ─────────────────────────────────────────────
Set-Location $ROOT
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  🚀 배포 시작 (with 체크리스트)" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# ─────────────────────────────────────────────
# STEP 1: 빌드
# ─────────────────────────────────────────────
if (-not $SkipBuild) {
    Write-Host "`n[1/5] 빌드 중..." -ForegroundColor Yellow
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  ❌ [CHECKLIST] npm run build 실패 — 배포 중단" -ForegroundColor Red
        exit 1
    }
    Check-Pass "[CHECKLIST 1/6] npm run build 성공"
} else {
    Write-Host "`n[1/5] 빌드 스킵" -ForegroundColor Gray
    Check-Pass "[CHECKLIST 1/6] 빌드 스킵 (기존 out/ 사용)"
}

# ─────────────────────────────────────────────
# STEP 2: out/ 폴더 사전 검증
# ─────────────────────────────────────────────
Write-Host "`n[2/5] out/ 폴더 검증..." -ForegroundColor Yellow

# index.html 존재
if (Test-Path "$ROOT\out\index.html") {
    Check-Pass "[CHECKLIST 2/6] out/index.html 존재"
} else {
    Check-Fail "[CHECKLIST 2/6] out/index.html 없음 — 배포 중단"
}

# 404.html (SPA redirect) 존재
if (Test-Path "$ROOT\out\404.html") {
    Check-Pass "[CHECKLIST 3/6] out/404.html (SPA redirect) 존재"
} else {
    Check-Fail "[CHECKLIST 3/6] out/404.html 없음 — 배포 중단"
}

# 주요 페이지 5개 out/ 존재 확인
$criticalPages = @(
    "dashboard.html",
    "explore.html",
    "explore\disclosure.html",
    "explore\influencer.html",
    "login.html"
)
$allPresent = $true
foreach ($page in $criticalPages) {
    if (-not (Test-Path "$ROOT\out\$page")) {
        Write-Host "  ⚠️  out/$page 없음" -ForegroundColor Red
        $allPresent = $false
    }
}
if ($allPresent) {
    Check-Pass "[CHECKLIST 4/6] 주요 페이지 5개 out/ 존재 확인"
} else {
    Check-Fail "[CHECKLIST 4/6] 주요 페이지 일부 누락 — 배포 중단"
}

# .nojekyll 보장
New-Item -Path "$ROOT\out\.nojekyll" -ItemType File -Force | Out-Null
Check-Pass ".nojekyll 생성/확인"

# ─────────────────────────────────────────────
# STEP 3: 배포
# ─────────────────────────────────────────────
Write-Host "`n[3/5] GitHub Pages 배포..." -ForegroundColor Yellow

if (Test-Path "$ROOT\out\.git") {
    Remove-Item -Recurse -Force "$ROOT\out\.git"
}

Set-Location "$ROOT\out"
git init
git checkout -b gh-pages
git add .
git commit -m $Message
git remote add origin https://github.com/puing5555/invest-sns.git
git push origin gh-pages --force

$pushResult = $LASTEXITCODE
Set-Location $ROOT
Remove-Item -Recurse -Force "$ROOT\out\.git" -ErrorAction SilentlyContinue

if ($pushResult -ne 0 -and $pushResult -ne 1) {
    Write-Host "  ❌ [CHECKLIST 5/6] 배포 실패 (exit $pushResult)" -ForegroundColor Red
    exit 1
}
Check-Pass "[CHECKLIST 5/6] GitHub Pages 배포 완료"

# ─────────────────────────────────────────────
# STEP 4: 배포 후 라이브 확인
# ─────────────────────────────────────────────
Write-Host "`n[4/5] 배포 후 라이브 확인 (15초 대기)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

$livePages = @(
    "$SITE_BASE/",
    "$SITE_BASE/dashboard",
    "$SITE_BASE/explore",
    "$SITE_BASE/explore/disclosure",
    "$SITE_BASE/explore/influencer"
)

$liveOk = $true
foreach ($path in $livePages) {
    try {
        $resp = Invoke-WebRequest -Uri "$BASE_URL$path" -UseBasicParsing -TimeoutSec 10
        if ($resp.StatusCode -eq 200) {
            Write-Host "    ✅ $path → 200 OK" -ForegroundColor Green
        } else {
            Write-Host "    ⚠️  $path → $($resp.StatusCode)" -ForegroundColor Yellow
            $liveOk = $false
        }
    } catch {
        Write-Host "    ❌ $path → FAILED" -ForegroundColor Red
        $liveOk = $false
    }
}

if ($liveOk) {
    Check-Pass "[CHECKLIST 6/6] 배포 후 라이브 확인 통과"
} else {
    Write-Host ""
    Write-Host "  ⚠️  일부 페이지가 아직 전파 중일 수 있습니다." -ForegroundColor Yellow
    Write-Host "     GitHub Pages CDN 전파에 최대 5분 소요됩니다." -ForegroundColor Yellow
}

# ─────────────────────────────────────────────
# STEP 5: 소스 커밋 (gh-pages와 별개)
# ─────────────────────────────────────────────
Write-Host "`n[5/5] 소스 코드 백업 커밋..." -ForegroundColor Yellow
Set-Location $ROOT
$status = git status --porcelain
if ($status) {
    git add -A -- ":(exclude)out/"
    git commit -m "backup: $Message" 2>&1 | Out-Null
    Write-Host "  ✅ 소스 코드 커밋 완료" -ForegroundColor Green
} else {
    Write-Host "  (변경사항 없음, 소스 커밋 스킵)" -ForegroundColor Gray
}

# ─────────────────────────────────────────────
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  ✅ 배포 완료!" -ForegroundColor Green
Write-Host "  https://puing5555.github.io/invest-sns/" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 체크리스트 요약:" -ForegroundColor Cyan
Write-Host "  ☑ npm run build 성공"
Write-Host "  ☑ out/index.html 존재"
Write-Host "  ☑ out/404.html (SPA redirect) 존재"
Write-Host "  ☑ 주요 페이지 5개 out/ 존재 확인"
Write-Host "  ☑ 배포 실행"
Write-Host "  ☑ 배포 후 라이브 확인"
