-- ============================================================
-- Migration: Round-by-round knockout predictions
-- Run this in the Supabase SQL Editor AFTER supabase_setup.sql
-- ============================================================

-- Step 1: Add round_points to scores and rebuild total_points
ALTER TABLE public.scores ADD COLUMN IF NOT EXISTS round_points int NOT NULL DEFAULT 0;
ALTER TABLE public.scores DROP COLUMN IF EXISTS total_points;
ALTER TABLE public.scores ADD COLUMN total_points int GENERATED ALWAYS AS (
    group_points + winner_points + finalist_points + semi_points + golden_boot_pts + round_points
) STORED;


-- Step 2: Round lifecycle table (one row per round, admin-controlled)
CREATE TABLE IF NOT EXISTS public.knockout_rounds (
    round      text PRIMARY KEY
                   CHECK (round IN ('R32','R16','QF','SF','Final')),
    status     text NOT NULL DEFAULT 'pending'
                   CHECK (status IN ('pending','open','closed')),
    opened_at  timestamptz,
    closed_at  timestamptz
);

INSERT INTO public.knockout_rounds (round)
VALUES ('R32'),('R16'),('QF'),('SF'),('Final')
ON CONFLICT (round) DO NOTHING;


-- Step 3: Individual match table
CREATE TABLE IF NOT EXISTS public.knockout_matches (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    round        text NOT NULL REFERENCES public.knockout_rounds(round),
    match_number int  NOT NULL,
    team_a       text NOT NULL,
    team_b       text NOT NULL,
    winner       text,
    created_at   timestamptz DEFAULT now(),
    updated_at   timestamptz DEFAULT now(),
    UNIQUE (round, match_number)
);


-- Step 4: User picks per match
CREATE TABLE IF NOT EXISTS public.knockout_match_predictions (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    match_id   uuid REFERENCES public.knockout_matches(id) ON DELETE CASCADE NOT NULL,
    pick       text NOT NULL,
    updated_at timestamptz DEFAULT now(),
    UNIQUE (user_id, match_id)
);


-- Step 5: RLS
ALTER TABLE public.knockout_rounds ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knockout_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knockout_match_predictions ENABLE ROW LEVEL SECURITY;

-- Rounds and matches: public read (status drives UI), service-role writes only
CREATE POLICY "ko_rounds_select" ON public.knockout_rounds FOR SELECT USING (true);
CREATE POLICY "ko_matches_select" ON public.knockout_matches FOR SELECT USING (true);

-- User picks: own rows for write; own rows always readable + anyone can read closed rounds
CREATE POLICY "ko_match_pred_insert"
    ON public.knockout_match_predictions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "ko_match_pred_update"
    ON public.knockout_match_predictions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "ko_match_pred_select"
    ON public.knockout_match_predictions
    FOR SELECT USING (
        auth.uid() = user_id
        OR EXISTS (
            SELECT 1 FROM public.knockout_rounds kr
            JOIN public.knockout_matches km ON km.round = kr.round
            WHERE km.id = match_id AND kr.status = 'closed'
        )
    );
