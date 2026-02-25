# 텔레그램 봇 명령문: DART 크롤링 파이프라인 설정

---

## 명령 1: DB 마이그레이션

Supabase SQL Editor에서 이 SQL을 실행해줘:

```sql
-- disclosures 테이블에 크롤러용 컬럼 추가
ALTER TABLE public.disclosures 
  ADD COLUMN IF NOT EXISTS stock_code TEXT,
  ADD COLUMN IF NOT EXISTS grade TEXT,
  ADD COLUMN IF NOT EXISTS sentiment TEXT,
  ADD COLUMN IF NOT EXISTS ai_one_liner TEXT,
  ADD COLUMN IF NOT EXISTS corp_cls TEXT;

-- 크롤러가 데이터 넣을 수 있도록 RLS 정책 추가
CREATE POLICY "Allow insert for anon" ON public.disclosures
  FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update for anon" ON public.disclosures
  FOR UPDATE USING (true);

-- disclosure_analysis RLS
ALTER TABLE public.disclosure_analysis ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Disclosure analysis is public" ON public.disclosure_analysis FOR SELECT USING (true);
CREATE POLICY "Allow insert disclosure analysis" ON public.disclosure_analysis FOR INSERT WITH CHECK (true);

-- 크롤링 로그 테이블
CREATE TABLE IF NOT EXISTS public.crawl_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  crawl_type TEXT NOT NULL,
  date_range TEXT NOT NULL,
  total_fetched INT DEFAULT 0,
  total_saved INT DEFAULT 0,
  a_grade INT DEFAULT 0,
  b_grade INT DEFAULT 0,
  c_grade INT DEFAULT 0,
  status TEXT DEFAULT 'running',
  error_message TEXT,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

ALTER TABLE public.crawl_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Crawl logs are public" ON public.crawl_logs FOR SELECT USING (true);
CREATE POLICY "Allow insert crawl logs" ON public.crawl_logs FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update crawl logs" ON public.crawl_logs FOR UPDATE USING (true);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_disclosures_stock_code ON public.disclosures(stock_code);
CREATE INDEX IF NOT EXISTS idx_disclosures_grade ON public.disclosures(grade);
CREATE INDEX IF NOT EXISTS idx_disclosures_submitted ON public.disclosures(submitted_at DESC);
```

---

## 명령 2: Edge Function 배포

프로젝트 루트에서 실행:

```bash
# Supabase CLI 설치 (없으면)
npm install -g supabase

# 프로젝트 연결
supabase link --project-ref arypzhotxflimroprmdk

# Edge Function 생성
supabase functions new dart-crawler

# supabase/functions/dart-crawler/index.ts에 아래 dart-crawler.ts 내용을 넣어줘
# 그 다음 배포
supabase functions deploy dart-crawler --no-verify-jwt
```

dart-crawler.ts 내용은 별도 파일로 제공할게.

---

## 명령 3: 프론트엔드에서 공시 표시

공시 대시보드 페이지(/disclosure)에서 실제 Supabase 데이터를 불러오도록 수정해줘.

```typescript
// lib/supabase.ts에 이미 클라이언트가 있을 것
import { supabase } from '@/lib/supabase';

// 공시 목록 조회
async function fetchDisclosures(grade?: string, limit = 30) {
  let query = supabase
    .from('disclosures')
    .select('*')
    .order('submitted_at', { ascending: false })
    .limit(limit);
  
  if (grade) {
    query = query.eq('grade', grade);
  }

  const { data, error } = await query;
  return data;
}

// A등급만 조회
const aGradeDisclosures = await fetchDisclosures('A');

// 전체 최신 30건
const allDisclosures = await fetchDisclosures();
```

공시 카드에 표시할 데이터:
- grade: A/B/C 배지
- corp_name: 기업명
- title: 공시 제목
- ai_one_liner: AI 한줄 분석
- sentiment: positive(초록)/negative(빨강)/neutral(회색)
- submitted_at: 공시 시간
- report_url: DART 원문 링크

---

이건 내(Claude PM)가 직접 만든 코드야. 에러 나면 말해줘 같이 디버깅하자.
