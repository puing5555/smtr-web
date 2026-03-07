-- 4. 알림설정
CREATE TABLE IF NOT EXISTS public.user_notification_settings (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  enabled BOOLEAN DEFAULT true,
  portfolio_alerts BOOLEAN DEFAULT true, watchlist_alerts BOOLEAN DEFAULT true,
  price_alerts BOOLEAN DEFAULT true, analyst_reports BOOLEAN DEFAULT true,
  market_summary BOOLEAN DEFAULT false, ai_insights BOOLEAN DEFAULT true,
  email_enabled BOOLEAN DEFAULT false, push_enabled BOOLEAN DEFAULT true,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.user_notification_settings ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "users_own_notification_settings" ON public.user_notification_settings;
CREATE POLICY "users_own_notification_settings" ON public.user_notification_settings FOR ALL USING (auth.uid() = user_id);
DROP TRIGGER IF EXISTS update_user_notification_settings_updated_at ON public.user_notification_settings;
CREATE TRIGGER update_user_notification_settings_updated_at BEFORE UPDATE ON public.user_notification_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 5. 알림기록
CREATE TABLE IF NOT EXISTS public.user_notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('signal','price_target','analyst_report','market_summary','ai_insight','portfolio_alert')),
  title TEXT NOT NULL, message TEXT NOT NULL, stock_code TEXT,
  is_read BOOLEAN DEFAULT false, created_at TIMESTAMPTZ DEFAULT NOW(),
  read_at TIMESTAMPTZ, metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id ON public.user_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_notifications_unread ON public.user_notifications(user_id, created_at DESC) WHERE is_read = false;
ALTER TABLE public.user_notifications ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "users_own_notifications" ON public.user_notifications;
CREATE POLICY "users_own_notifications" ON public.user_notifications FOR ALL USING (auth.uid() = user_id);

-- 회원가입 자동 생성
CREATE OR REPLACE FUNCTION create_user_profile()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, email, display_name)
  VALUES (NEW.id, NEW.email, COALESCE(NEW.raw_user_meta_data->>'display_name', split_part(NEW.email, '@', 1)));
  INSERT INTO public.user_notification_settings (user_id)
  VALUES (NEW.id);
  RETURN NEW;
END;
$$ language 'plpgsql' security definer;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created AFTER INSERT ON auth.users FOR EACH ROW EXECUTE FUNCTION create_user_profile();

SELECT '5개 테이블 전부 완료!' as result;
