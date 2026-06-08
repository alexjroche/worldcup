-- ============================================================
-- Migration: Head-to-head, reactions, leaderboard movers
-- Run in Supabase SQL Editor after previous migrations
-- ============================================================

-- 1. Rank tracking on scores table
ALTER TABLE public.scores
    ADD COLUMN IF NOT EXISTS rank      int,
    ADD COLUMN IF NOT EXISTS prev_rank int;


-- 2. Hot take reactions
CREATE TABLE IF NOT EXISTS public.hot_take_reactions (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    hot_take_id uuid REFERENCES public.hot_takes(id) ON DELETE CASCADE NOT NULL,
    emoji       text NOT NULL CHECK (emoji IN ('🔥','😂','🤦','👏')),
    created_at  timestamptz DEFAULT now(),
    UNIQUE (user_id, hot_take_id, emoji)
);

ALTER TABLE public.hot_take_reactions ENABLE ROW LEVEL SECURITY;

-- Anyone can read reactions; authenticated users write their own
CREATE POLICY "reactions_select" ON public.hot_take_reactions FOR SELECT USING (true);
CREATE POLICY "reactions_insert" ON public.hot_take_reactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "reactions_delete" ON public.hot_take_reactions
    FOR DELETE USING (auth.uid() = user_id);
