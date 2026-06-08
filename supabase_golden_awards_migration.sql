-- ============================================================
-- Golden Ball & Golden Glove migration
-- Run this in the Supabase SQL editor
-- ============================================================

-- 1. Add new award columns to knockout_predictions
ALTER TABLE knockout_predictions
    ADD COLUMN IF NOT EXISTS golden_ball  text,
    ADD COLUMN IF NOT EXISTS golden_glove text;

-- 2. Add new award columns to knockout_results
ALTER TABLE knockout_results
    ADD COLUMN IF NOT EXISTS golden_ball  text,
    ADD COLUMN IF NOT EXISTS golden_glove text;

-- 3. Add point columns to scores
ALTER TABLE scores
    ADD COLUMN IF NOT EXISTS golden_ball_pts  int DEFAULT 0,
    ADD COLUMN IF NOT EXISTS golden_glove_pts int DEFAULT 0;

-- 4. Rebuild total_points generated column to include new fields
--    (GENERATED ALWAYS AS columns can only be changed by drop+re-add)
ALTER TABLE scores DROP COLUMN IF EXISTS total_points;
ALTER TABLE scores ADD COLUMN total_points int GENERATED ALWAYS AS (
    group_points + winner_points + finalist_points + semi_points +
    golden_boot_pts + golden_ball_pts + golden_glove_pts + round_points
) STORED;
