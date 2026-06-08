-- ============================================================
-- Migration: Score timeline, badges, hot takes
-- Run in Supabase SQL Editor after previous migrations
-- ============================================================

-- 1. Score snapshots (for timeline chart)
CREATE TABLE IF NOT EXISTS public.score_snapshots (
    id             bigserial PRIMARY KEY,
    snapshot_label text NOT NULL,
    user_id        uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    total_points   int NOT NULL DEFAULT 0,
    created_at     timestamptz DEFAULT now()
);

ALTER TABLE public.score_snapshots ENABLE ROW LEVEL SECURITY;
CREATE POLICY "snapshots_select" ON public.score_snapshots FOR SELECT USING (true);


-- 2. Badge columns on scores table
ALTER TABLE public.scores
    ADD COLUMN IF NOT EXISTS badge_perfect_groups  int     NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS badge_oracle          boolean NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS badge_golden_boot_win boolean NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS badge_top_of_table    boolean NOT NULL DEFAULT false;


-- 3. Hot takes (one per user, pre-lock)
CREATE TABLE IF NOT EXISTS public.hot_takes (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL UNIQUE,
    take       text NOT NULL,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

ALTER TABLE public.hot_takes ENABLE ROW LEVEL SECURITY;

-- Anyone can read (but only post-lock in the UI layer)
CREATE POLICY "hot_takes_select" ON public.hot_takes FOR SELECT USING (true);
CREATE POLICY "hot_takes_insert" ON public.hot_takes FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "hot_takes_update" ON public.hot_takes FOR UPDATE USING (auth.uid() = user_id);
