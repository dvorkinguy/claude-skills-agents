-- Example RLS Policies for Multi-Tenant SaaS

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;

-- ============================================
-- USERS TABLE
-- ============================================

-- Users can view their own profile
CREATE POLICY "Users view own profile"
ON users FOR SELECT
TO authenticated
USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users update own profile"
ON users FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- ============================================
-- PROJECTS TABLE
-- ============================================

-- Users can view projects in their teams
CREATE POLICY "Team members view projects"
ON projects FOR SELECT
TO authenticated
USING (
  team_id IN (
    SELECT team_id FROM team_members
    WHERE user_id = auth.uid()
  )
);

-- Users can insert projects in teams they're members of
CREATE POLICY "Team members insert projects"
ON projects FOR INSERT
TO authenticated
WITH CHECK (
  team_id IN (
    SELECT team_id FROM team_members
    WHERE user_id = auth.uid()
  )
);

-- Users can update projects in teams they're members of
CREATE POLICY "Team members update projects"
ON projects FOR UPDATE
TO authenticated
USING (
  team_id IN (
    SELECT team_id FROM team_members
    WHERE user_id = auth.uid()
  )
)
WITH CHECK (
  team_id IN (
    SELECT team_id FROM team_members
    WHERE user_id = auth.uid()
  )
);

-- Only team admins can delete projects
CREATE POLICY "Team admins delete projects"
ON projects FOR DELETE
TO authenticated
USING (
  team_id IN (
    SELECT team_id FROM team_members
    WHERE user_id = auth.uid()
    AND role = 'admin'
  )
);

-- ============================================
-- TEAMS TABLE
-- ============================================

-- Users can view teams they're members of
CREATE POLICY "Members view teams"
ON teams FOR SELECT
TO authenticated
USING (
  id IN (
    SELECT team_id FROM team_members
    WHERE user_id = auth.uid()
  )
);

-- Only team owners can update team details
CREATE POLICY "Owners update teams"
ON teams FOR UPDATE
TO authenticated
USING (owner_id = auth.uid())
WITH CHECK (owner_id = auth.uid());

-- Only owners can delete teams
CREATE POLICY "Owners delete teams"
ON teams FOR DELETE
TO authenticated
USING (owner_id = auth.uid());

-- ============================================
-- TEAM_MEMBERS TABLE
-- ============================================

-- Users can view members of their teams
CREATE POLICY "Team members view members"
ON team_members FOR SELECT
TO authenticated
USING (
  team_id IN (
    SELECT team_id FROM team_members
    WHERE user_id = auth.uid()
  )
);

-- Only team admins can add members
CREATE POLICY "Admins add members"
ON team_members FOR INSERT
TO authenticated
WITH CHECK (
  team_id IN (
    SELECT team_id FROM team_members
    WHERE user_id = auth.uid()
    AND role IN ('admin', 'owner')
  )
);

-- Only team admins can remove members
CREATE POLICY "Admins remove members"
ON team_members FOR DELETE
TO authenticated
USING (
  team_id IN (
    SELECT team_id FROM team_members
    WHERE user_id = auth.uid()
    AND role IN ('admin', 'owner')
  )
);

-- Users can leave teams themselves
CREATE POLICY "Users can leave teams"
ON team_members FOR DELETE
TO authenticated
USING (user_id = auth.uid());
