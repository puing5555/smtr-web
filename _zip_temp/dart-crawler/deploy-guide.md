# DART 크롤링 파이프라인 배포 가이드

## 📁 파일 구성
```
dart-crawler/
├── dart-crawler.ts       ← 메인 크롤링 코드 (로컬 + Edge Function 겸용)
├── migration.sql         ← DB 스키마 확장 SQL
├── deploy-guide.md       ← 이 파일
└── bot-commands.md       ← 봇 명령문
```

## 🔧 Step 1: DB 마이그레이션

Supabase 대시보드 → SQL Editor → New Query → `migration.sql` 내용 전체 붙여넣기 → Run

## 🔧 Step 2: Supabase Edge Function 배포

### 방법 A: Supabase CLI (추천)

```bash
# Supabase CLI 설치
npm install -g supabase

# 로그인
supabase login

# 프로젝트 연결
supabase link --project-ref arypzhotxflimroprmdk

# Edge Function 생성
supabase functions new dart-crawler

# dart-crawler.ts를 supabase/functions/dart-crawler/index.ts로 복사
cp dart-crawler.ts supabase/functions/dart-crawler/index.ts

# 배포
supabase functions deploy dart-crawler --no-verify-jwt
```

### 방법 B: 로컬에서 직접 실행 (테스트용)

```bash
# Deno 설치
curl -fsSL https://deno.land/install.sh | sh

# 실행
deno run --allow-net dart-crawler.ts
```

### 방법 C: Node.js 로컬 실행

```bash
# TypeScript 실행
npx tsx dart-crawler.ts
```

## 🔧 Step 3: Cron 설정 (자동 실행)

### Supabase pg_cron (무료)
```sql
-- Supabase SQL Editor에서 실행
-- 10분마다 실시간 크롤링
SELECT cron.schedule(
  'dart-crawl-recent',
  '*/10 * * * *',
  $$
  SELECT net.http_post(
    url := 'https://arypzhotxflimroprmdk.supabase.co/functions/v1/dart-crawler?mode=recent',
    headers := '{"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"}'::jsonb
  );
  $$
);

-- 매일 새벽 3시에 백데이터 크롤링 (90일 전 ~ 2일 전)
SELECT cron.schedule(
  'dart-crawl-backfill',
  '0 3 * * *',
  $$
  SELECT net.http_post(
    url := 'https://arypzhotxflimroprmdk.supabase.co/functions/v1/dart-crawler?mode=backfill',
    headers := '{"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"}'::jsonb
  );
  $$
);
```

## 🧪 테스트

Edge Function 배포 후 브라우저에서:
```
# 실시간 크롤링 (어제~오늘)
https://arypzhotxflimroprmdk.supabase.co/functions/v1/dart-crawler?mode=recent

# 백데이터 (특정 기간)
https://arypzhotxflimroprmdk.supabase.co/functions/v1/dart-crawler?mode=backfill&bgn=20250101&end=20250131
```

## 📊 API 한도 계산

```
하루 총 한도: 10,000건

실시간 (10분마다):
- 하루 공시 ~300건 → 각 조회에 ~3~5 API 호출
- 하루 총: 144회 × 3~5 = ~600건

백데이터 (매일 새벽):
- 남은 한도: ~9,000건
- 3개월치(~15,000건) → 페이지당 100건 → ~150 API 호출
- 하루에 3개월치 충분히 가능

→ 1년치: 약 4일
→ 3년치: 약 12일
```

## 🔍 등급 분류 기준

| 등급 | 기준 | 예시 |
|------|------|------|
| A | 주가 즉시 영향 | 공급계약, 자사주, 배당, 실적, M&A, 유상증자, 임원매매, CB/BW |
| B | 참고할 만한 정보 | 정기보고서, 소송, 임원변동, 주요사항보고 |
| C | 일반 공시 | 기타 모든 공시 |
