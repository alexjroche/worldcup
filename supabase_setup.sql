-- ============================================================
-- World Cup 2026 Predictions App — Supabase Setup Script
-- Run this in the Supabase SQL Editor (one block at a time
-- if needed, or all at once).
-- ============================================================

-- 1. profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id               uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name     text NOT NULL,
    favourite_player text,
    is_admin         boolean DEFAULT false,
    created_at       timestamptz DEFAULT now()
);

-- Auto-create a profile row when a new user registers
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
    INSERT INTO public.profiles (id, display_name, favourite_player)
    VALUES (NEW.id, '', '')
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- 2. group_predictions
CREATE TABLE IF NOT EXISTS public.group_predictions (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    group_name   text NOT NULL,
    position_1   text NOT NULL,
    position_2   text NOT NULL,
    position_3   text NOT NULL,
    position_4   text NOT NULL,
    updated_at   timestamptz DEFAULT now(),
    UNIQUE (user_id, group_name)
);


-- 3. knockout_predictions
CREATE TABLE IF NOT EXISTS public.knockout_predictions (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL UNIQUE,
    winner       text NOT NULL,
    finalist     text NOT NULL,
    semi_1       text NOT NULL,
    semi_2       text NOT NULL,
    golden_boot  text,
    updated_at   timestamptz DEFAULT now()
);


-- 4. group_results (admin-entered)
CREATE TABLE IF NOT EXISTS public.group_results (
    group_name   text PRIMARY KEY,
    position_1   text NOT NULL,
    position_2   text NOT NULL,
    position_3   text NOT NULL,
    position_4   text NOT NULL,
    entered_at   timestamptz DEFAULT now()
);


-- 5. knockout_results (admin-entered, single row)
CREATE TABLE IF NOT EXISTS public.knockout_results (
    id           int PRIMARY KEY DEFAULT 1,
    winner       text,
    finalist     text,
    semi_1       text,
    semi_2       text,
    golden_boot  text,
    entered_at   timestamptz DEFAULT now(),
    CONSTRAINT single_row CHECK (id = 1)
);


-- 6. scores (calculated, cached)
CREATE TABLE IF NOT EXISTS public.scores (
    user_id           uuid PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
    group_points      int DEFAULT 0,
    winner_points     int DEFAULT 0,
    finalist_points   int DEFAULT 0,
    semi_points       int DEFAULT 0,
    golden_boot_pts   int DEFAULT 0,
    total_points      int GENERATED ALWAYS AS (
        group_points + winner_points + finalist_points + semi_points + golden_boot_pts
    ) STORED,
    bold_pick         boolean DEFAULT false,
    last_calculated   timestamptz DEFAULT now()
);


-- ============================================================
-- Row Level Security
-- ============================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.group_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knockout_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.group_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knockout_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scores ENABLE ROW LEVEL SECURITY;


-- profiles: everyone can read; only own row for writes
CREATE POLICY "profiles_select" ON public.profiles FOR SELECT USING (true);
CREATE POLICY "profiles_insert" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "profiles_update" ON public.profiles FOR UPDATE USING (auth.uid() = id);


-- group_predictions:
--   INSERT/UPDATE own rows only
--   SELECT: own rows always; others' rows only after lock (2026-06-11 18:00 UTC)
CREATE POLICY "group_pred_insert" ON public.group_predictions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "group_pred_update" ON public.group_predictions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "group_pred_select" ON public.group_predictions
    FOR SELECT USING (
        auth.uid() = user_id
        OR now() >= TIMESTAMPTZ '2026-06-11 18:00:00+00'
    );


-- knockout_predictions: same visibility rules
CREATE POLICY "ko_pred_insert" ON public.knockout_predictions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "ko_pred_update" ON public.knockout_predictions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "ko_pred_select" ON public.knockout_predictions
    FOR SELECT USING (
        auth.uid() = user_id
        OR now() >= TIMESTAMPTZ '2026-06-11 18:00:00+00'
    );


-- results: readable by everyone (no secrets here); writable only via service role
CREATE POLICY "group_results_select" ON public.group_results FOR SELECT USING (true);
CREATE POLICY "ko_results_select" ON public.knockout_results FOR SELECT USING (true);
CREATE POLICY "scores_select" ON public.scores FOR SELECT USING (true);


-- ============================================================
-- To make yourself an admin, run:
--   UPDATE public.profiles SET is_admin = true
--   WHERE id = '<your-user-uuid>';
-- Find your UUID in Supabase Auth → Users.
-- ============================================================
