-- ============================================================
-- Wager opt-in migration
-- Run this in the Supabase SQL editor
-- ============================================================

ALTER TABLE league_members
    ADD COLUMN IF NOT EXISTS wager_in boolean DEFAULT false;
