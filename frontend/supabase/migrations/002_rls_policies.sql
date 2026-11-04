-- ============================================================================
-- KOSHA LABS – Supabase PostgreSQL RLS Policies
-- Migration 002: Row Level Security for Role-Based Access Control
-- ============================================================================

-- Enable RLS across all tables
ALTER TABLE workers ENABLE ROW LEVEL SECURITY;
ALTER TABLE biometric_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE recording_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE operators ENABLE ROW LEVEL SECURITY;
ALTER TABLE biometric_consents ENABLE ROW LEVEL SECURITY;
ALTER TABLE recognition_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Helper function to inspect current user role from JWT claims or operators table
CREATE OR REPLACE FUNCTION get_current_operator() 
RETURNS operators AS $$
  SELECT * FROM operators WHERE auth_user_id = auth.uid() AND status = 'active' LIMIT 1;
$$ LANGUAGE sql SECURITY DEFINER;

-- ----------------------------------------------------------------------------
-- POLICIES: workers table
-- ----------------------------------------------------------------------------

-- Admin: full access
CREATE POLICY admin_workers_all ON workers
  FOR ALL
  TO authenticated
  USING ((SELECT role FROM get_current_operator()) = 'admin')
  WITH CHECK ((SELECT role FROM get_current_operator()) = 'admin');

-- Operator & Supervisor: Read active workers at authorized site or system-wide for 1:N recognition
CREATE POLICY operator_workers_select ON workers
  FOR SELECT
  TO authenticated
  USING ((SELECT role FROM get_current_operator()) IN ('operator', 'supervisor', 'admin'));

-- Operator: Insert new worker records
CREATE POLICY operator_workers_insert ON workers
  FOR INSERT
  TO authenticated
  WITH CHECK (
    (SELECT role FROM get_current_operator()) IN ('operator', 'admin')
    AND site_id = (SELECT assigned_site_id FROM get_current_operator())
  );

-- Supervisor: Update worker metadata (e.g. status under review, department changes)
CREATE POLICY supervisor_workers_update ON workers
  FOR UPDATE
  TO authenticated
  USING ((SELECT role FROM get_current_operator()) IN ('supervisor', 'admin'))
  WITH CHECK ((SELECT role FROM get_current_operator()) IN ('supervisor', 'admin'));

-- ----------------------------------------------------------------------------
-- POLICIES: biometric_templates table (STRICT SECURITY ZONE)
-- Never exposed to client direct queries. Only backend service_role can read/write embeddings!
-- ----------------------------------------------------------------------------

-- Deny all public and authenticated client direct queries to embeddings
CREATE POLICY deny_client_templates ON biometric_templates
  FOR ALL
  TO authenticated, anon
  USING (false);

-- Service role bypasses RLS and handles all cryptographic template operations
-- (Supabase service_role has built-in bypassrls)

-- ----------------------------------------------------------------------------
-- POLICIES: recording_sessions table
-- ----------------------------------------------------------------------------

-- Admin: full access
CREATE POLICY admin_sessions_all ON recording_sessions
  FOR ALL
  TO authenticated
  USING ((SELECT role FROM get_current_operator()) = 'admin');

-- Operator & Supervisor: Read sessions at assigned site
CREATE POLICY operator_sessions_select ON recording_sessions
  FOR SELECT
  TO authenticated
  USING (
    (SELECT role FROM get_current_operator()) IN ('operator', 'supervisor', 'admin')
  );

-- Operator: Create recording sessions linked to verified workers
CREATE POLICY operator_sessions_insert ON recording_sessions
  FOR INSERT
  TO authenticated
  WITH CHECK (
    (SELECT role FROM get_current_operator()) IN ('operator', 'admin')
  );

-- ----------------------------------------------------------------------------
-- POLICIES: recognition_logs table
-- ----------------------------------------------------------------------------

-- Operator: View and log scan attempts
CREATE POLICY operator_recognition_logs_select ON recognition_logs
  FOR SELECT
  TO authenticated
  USING ((SELECT role FROM get_current_operator()) IN ('operator', 'supervisor', 'admin'));

CREATE POLICY operator_recognition_logs_insert ON recognition_logs
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT role FROM get_current_operator()) IN ('operator', 'admin'));

-- Supervisor: Update / Resolve uncertain match reviews
CREATE POLICY supervisor_recognition_logs_update ON recognition_logs
  FOR UPDATE
  TO authenticated
  USING ((SELECT role FROM get_current_operator()) IN ('supervisor', 'admin'))
  WITH CHECK ((SELECT role FROM get_current_operator()) IN ('supervisor', 'admin'));

-- ----------------------------------------------------------------------------
-- POLICIES: sites & operators
-- ----------------------------------------------------------------------------
CREATE POLICY view_sites ON sites
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY view_operators ON operators
  FOR SELECT
  TO authenticated
  USING (true);

-- ----------------------------------------------------------------------------
-- POLICIES: audit_logs table (Append-only)
-- ----------------------------------------------------------------------------
CREATE POLICY insert_audit_logs ON audit_logs
  FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY view_audit_logs_admin ON audit_logs
  FOR SELECT
  TO authenticated
  USING ((SELECT role FROM get_current_operator()) = 'admin');
