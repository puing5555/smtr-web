-- research_invest_platforms 테이블 생성
-- Supabase Dashboard > SQL Editor에서 실행

CREATE TABLE IF NOT EXISTS research_invest_platforms (
  id SERIAL PRIMARY KEY,
  company_name TEXT NOT NULL,
  country TEXT,
  category TEXT,  -- A~H
  url TEXT,
  target_customer TEXT,
  revenue_model TEXT,
  pricing TEXT,
  key_features TEXT,
  strengths TEXT,
  weaknesses TEXT,
  our_takeaway TEXT,
  applicable_phase TEXT,  -- 1/2/3/4
  priority TEXT,  -- P0/P1/P2/P3
  benchmark_score INTEGER CHECK (benchmark_score >= 1 AND benchmark_score <= 5),
  one_liner TEXT,
  full_report TEXT,
  researched_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS 활성화
ALTER TABLE research_invest_platforms ENABLE ROW LEVEL SECURITY;

-- anon 읽기 허용
CREATE POLICY "research_invest_platforms_read" ON research_invest_platforms
  FOR SELECT USING (true);

-- service_role 전체 권한
CREATE POLICY "research_invest_platforms_all" ON research_invest_platforms
  FOR ALL USING (auth.role() = 'service_role');
