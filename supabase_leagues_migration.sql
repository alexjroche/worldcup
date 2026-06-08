-- ============================================================
-- Leagues migration
-- Run this in the Supabase SQL editor
-- ============================================================

-- 1. leagues table
CREATE TABLE IF NOT EXISTS leagues (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name        text NOT NULL,
    invite_code text UNIQUE NOT NULL,
    created_by  uuid REFERENCES profiles(id),
    created_at  timestamptz DEFAULT now()
);

-- 2. league_members join table
CREATE TABLE IF NOT EXISTS league_members (
    league_id  uuid REFERENCES leagues(id) ON DELETE CASCADE,
    user_id    uuid REFERENCES profiles(id) ON DELETE CASCADE,
    joined_at  timestamptz DEFAULT now(),
    PRIMARY KEY (league_id, user_id)
);

-- 3. Row Level Security
ALTER TABLE leagues ENABLE ROW LEVEL SECURITY;
ALTER TABLE league_members ENABLE ROW LEVEL SECURITY;

-- leagues: anyone can read (needed to look up an invite code before joining)
DROP POLICY IF EXISTS "leagues_select_all" ON leagues;
CREATE POLICY "leagues_select_all" ON leagues
    FOR SELECT USING (true);

-- leagues: authenticated users can create their own leagues
DROP POLICY IF EXISTS "leagues_insert_own" ON leagues;
CREATE POLICY "leagues_insert_own" ON leagues
    FOR INSERT WITH CHECK (auth.uid() = created_by);

-- leagues: only creator can delete
DROP POLICY IF EXISTS "leagues_delete_own" ON leagues;
CREATE POLICY "leagues_delete_own" ON leagues
    FOR DELETE USING (auth.uid() = created_by);

-- league_members: authenticated users can see all memberships
-- (needed so the leaderboard can show other members of your league)
DROP POLICY IF EXISTS "league_members_select_authed" ON league_members;
CREATE POLICY "league_members_select_authed" ON league_members
    FOR SELECT USING (auth.role() = 'authenticated');

-- league_members: users can add themselves only
DROP POLICY IF EXISTS "league_members_insert_self" ON league_members;
CREATE POLICY "league_members_insert_self" ON league_members
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- league_members: users can remove themselves only
DROP POLICY IF EXISTS "league_members_delete_self" ON league_members;
CREATE POLICY "league_members_delete_self" ON league_members
    FOR DELETE USING (auth.uid() = user_id);
