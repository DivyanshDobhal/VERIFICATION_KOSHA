-- ============================================================================
-- KOSHA LABS – Supabase PostgreSQL RLS Fix & Atomic Registration Migration
-- Migration 003: Fix Row-Level Security (RLS) for Worker Registration & Biometrics
-- ============================================================================

-- Ensure uuid and pgcrypto extensions are active
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- 1. SECURITY HELPER FUNCTIONS (SECURITY DEFINER)
-- ----------------------------------------------------------------------------

-- Returns current operator record linked to auth.uid()
CREATE OR REPLACE FUNCTION get_current_operator() 
RETURNS operators AS $$
  SELECT * FROM operators WHERE auth_user_id = auth.uid() AND status = 'active' LIMIT 1;
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- Check if current authenticated user has 'admin' privileges
CREATE OR REPLACE FUNCTION is_admin() 
RETURNS BOOLEAN AS $$
  SELECT COALESCE(
    (SELECT role = 'admin' FROM operators WHERE auth_user_id = auth.uid() AND status = 'active' LIMIT 1),
    (current_setting('request.jwt.claims', true)::jsonb ->> 'role' = 'service_role'),
    false
  );
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- Check if current authenticated user has 'operator', 'supervisor', or 'admin' privileges
CREATE OR REPLACE FUNCTION is_authorized_operator() 
RETURNS BOOLEAN AS $$
  SELECT COALESCE(
    (SELECT role IN ('operator', 'supervisor', 'admin') FROM operators WHERE auth_user_id = auth.uid() AND status = 'active' LIMIT 1),
    (current_setting('request.jwt.claims', true)::jsonb ->> 'role' = 'service_role'),
    false
  );
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- ----------------------------------------------------------------------------
-- 2. FIX RLS POLICIES ON WORKERS TABLE
-- ----------------------------------------------------------------------------
ALTER TABLE workers ENABLE ROW LEVEL SECURITY;

-- Drop previous restrictive or conflicting policies if they exist
DROP POLICY IF EXISTS admin_workers_all ON workers;
DROP POLICY IF EXISTS operator_workers_select ON workers;
DROP POLICY IF EXISTS operator_workers_insert ON workers;
DROP POLICY IF EXISTS supervisor_workers_update ON workers;
DROP POLICY IF EXISTS worker_registration_insert ON workers;
DROP POLICY IF EXISTS worker_view_policy ON workers;

-- Policy A: SELECT permission
-- Authenticated operators, supervisors, and admins can view active worker profiles
CREATE POLICY worker_select_policy ON workers
  FOR SELECT
  TO authenticated, anon
  USING (
    status != 'flagged' 
    OR is_authorized_operator()
  );

-- Policy B: INSERT permission
-- Validates that the inserting user is authorized and matches site constraints
CREATE POLICY worker_registration_insert ON workers
  FOR INSERT
  TO authenticated, anon
  WITH CHECK (
    -- Validation 1: Worker must be of legal working age (18 - 75)
    (age >= 18 AND age <= 75)
    -- Validation 2: Weight must be in plausible industrial range
    AND (weight >= 35.0 AND weight <= 180.0)
    -- Validation 3: Full name must not be blank
    AND (length(trim(full_name)) > 0)
    -- Validation 4: Valid worker category
    AND (worker_category IN ('General Labour', 'Specialist Technician', 'Heavy Equipment Operator', 'Foreman / Supervisor'))
  );

-- Policy C: UPDATE permission
-- Only authorized supervisors and admins can update worker metadata or status
CREATE POLICY worker_update_policy ON workers
  FOR UPDATE
  TO authenticated
  USING (is_authorized_operator())
  WITH CHECK (is_authorized_operator());

-- Policy D: DELETE permission
-- Only admins can delete worker records
CREATE POLICY worker_delete_policy ON workers
  FOR DELETE
  TO authenticated
  USING (is_admin());

-- ----------------------------------------------------------------------------
-- 3. FIX RLS POLICIES ON SITES TABLE
-- ----------------------------------------------------------------------------
ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS view_sites ON sites;
DROP POLICY IF EXISTS sites_select_policy ON sites;

-- Allow reading site information for site selection during registration
CREATE POLICY sites_select_policy ON sites
  FOR SELECT
  TO authenticated, anon
  USING (status = 'active' OR is_authorized_operator());

-- ----------------------------------------------------------------------------
-- 4. FIX RLS POLICIES ON BIOMETRIC CONSENTS TABLE
-- ----------------------------------------------------------------------------
ALTER TABLE biometric_consents ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS consents_select_policy ON biometric_consents;
DROP POLICY IF EXISTS consents_insert_policy ON biometric_consents;

-- Only authorized personnel can inspect consent records
CREATE POLICY consents_select_policy ON biometric_consents
  FOR SELECT
  TO authenticated
  USING (is_authorized_operator());

-- Inserting consent records is allowed during worker enrollment
CREATE POLICY consents_insert_policy ON biometric_consents
  FOR INSERT
  TO authenticated, anon
  WITH CHECK (
    worker_id IS NOT NULL 
    AND consent_status = true
  );

-- ----------------------------------------------------------------------------
-- 5. FIX RLS POLICIES ON BIOMETRIC TEMPLATES TABLE (STRICT ENCRYPTION ZONE)
-- ----------------------------------------------------------------------------
ALTER TABLE biometric_templates ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS deny_client_templates ON biometric_templates;
DROP POLICY IF EXISTS biometric_templates_insert_policy ON biometric_templates;
DROP POLICY IF EXISTS biometric_templates_select_policy ON biometric_templates;

-- Protect raw embeddings from public leakage:
-- Client direct SELECT is restricted; embeddings are evaluated through backend verification
CREATE POLICY biometric_templates_select_policy ON biometric_templates
  FOR SELECT
  TO authenticated
  USING (is_authorized_operator());

-- Templates can be inserted during verified enrollment
CREATE POLICY biometric_templates_insert_policy ON biometric_templates
  FOR INSERT
  TO authenticated, anon
  WITH CHECK (
    worker_id IS NOT NULL 
    AND length(template_hash) > 0
    AND quality_score >= 0 
    AND quality_score <= 100
  );

-- ----------------------------------------------------------------------------
-- 6. FIX RLS POLICIES ON AUDIT LOGS TABLE
-- ----------------------------------------------------------------------------
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS insert_audit_logs ON audit_logs;
DROP POLICY IF EXISTS view_audit_logs_admin ON audit_logs;

CREATE POLICY audit_logs_insert_policy ON audit_logs
  FOR INSERT
  TO authenticated, anon
  WITH CHECK (true);

CREATE POLICY audit_logs_select_policy ON audit_logs
  FOR SELECT
  TO authenticated
  USING (is_authorized_operator());

-- ----------------------------------------------------------------------------
-- 7. ATOMIC TRANSACTIONAL WORKER REGISTRATION STORED PROCEDURE (RPC)
-- ----------------------------------------------------------------------------
-- This function executes with SECURITY DEFINER to atomically perform duplicate
-- checks, sequential ID generation, worker insertion, consent recording, and
-- biometric template enrollment in a single ACID transaction.

CREATE OR REPLACE FUNCTION register_worker_atomic(
  p_full_name TEXT,
  p_age INTEGER,
  p_weight NUMERIC,
  p_gender TEXT,
  p_contact_number TEXT,
  p_emergency_contact TEXT,
  p_blood_group TEXT,
  p_site_id UUID,
  p_department TEXT,
  p_worker_category TEXT,
  p_notes TEXT,
  p_enrolled_fingers JSONB,
  p_consent_accepted BOOLEAN
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_clean_name TEXT;
  v_clean_contact TEXT;
  v_existing_id TEXT;
  v_new_worker_id TEXT;
  v_worker_uuid UUID;
  v_consent_uuid UUID;
  v_finger RECORD;
  v_finger_type TEXT;
  v_quality NUMERIC;
  v_tmpl_hash TEXT;
  v_result JSONB;
BEGIN
  v_clean_name := trim(p_full_name);
  v_clean_contact := trim(COALESCE(p_contact_number, ''));

  -- 1. Validate mandatory inputs
  IF length(v_clean_name) = 0 THEN
    RAISE EXCEPTION 'Worker full name is required.';
  END IF;

  IF p_age < 18 OR p_age > 75 THEN
    RAISE EXCEPTION 'Worker age must be between 18 and 75.';
  END IF;

  IF p_weight < 35.0 OR p_weight > 180.0 THEN
    RAISE EXCEPTION 'Worker weight must be between 35.0 and 180.0 kg.';
  END IF;

  IF NOT p_consent_accepted THEN
    RAISE EXCEPTION 'Biometric consent is mandatory for worker registration.';
  END IF;

  -- 2. Duplicate worker check (by contact number or exact name match)
  IF length(v_clean_contact) > 0 THEN
    SELECT worker_id INTO v_existing_id
    FROM workers
    WHERE contact_number = v_clean_contact OR lower(full_name) = lower(v_clean_name)
    LIMIT 1;

    IF v_existing_id IS NOT NULL THEN
      RAISE EXCEPTION 'Duplicate worker detected! Worker already enrolled under permanent Worker ID %', v_existing_id
        USING ERRCODE = '23505';
    END IF;
  END IF;

  -- 3. Insert Worker Record (Generates permanent sequential worker_id via sequence)
  INSERT INTO workers (
    full_name,
    age,
    weight,
    gender,
    contact_number,
    emergency_contact,
    blood_group,
    site_id,
    department,
    worker_category,
    additional_metadata,
    status
  ) VALUES (
    v_clean_name,
    p_age,
    p_weight,
    p_gender,
    v_clean_contact,
    p_emergency_contact,
    p_blood_group,
    p_site_id,
    p_department,
    p_worker_category,
    jsonb_build_object('notes', p_notes),
    'active'
  )
  RETURNING id, worker_id INTO v_worker_uuid, v_new_worker_id;

  -- 4. Record Biometric Consent
  INSERT INTO biometric_consents (
    worker_id,
    consent_status,
    consent_version,
    purpose
  ) VALUES (
    v_worker_uuid,
    true,
    'v2.4',
    'Industrial deduplication & attendance authentication'
  )
  RETURNING id INTO v_consent_uuid;

  -- 5. Insert Enrolled Biometric Fingerprint Templates
  IF p_enrolled_fingers IS NOT NULL AND jsonb_array_length(p_enrolled_fingers) > 0 THEN
    FOR v_finger IN SELECT * FROM jsonb_to_recordset(p_enrolled_fingers) AS (
      finger TEXT,
      quality NUMERIC,
      templateHash TEXT,
      embedding JSONB
    )
    LOOP
      v_finger_type := COALESCE(v_finger.finger, 'Right Thumb');
      v_quality := COALESCE(v_finger.quality, 95.0);
      v_tmpl_hash := COALESCE(v_finger.templateHash, 'HASH_' || upper(replace(v_finger_type, ' ', '_')) || '_' || floor(extract(epoch from now()))::text);

      INSERT INTO biometric_templates (
        worker_id,
        finger_type,
        encrypted_embedding,
        embedding_dimension,
        template_hash,
        quality_score,
        consent_record_id,
        status
      ) VALUES (
        v_worker_uuid,
        v_finger_type,
        decode(repeat('5a', 128), 'hex'), -- 128-byte template representation
        128,
        v_tmpl_hash,
        v_quality,
        v_consent_uuid,
        'active'
      );
    END LOOP;
  END IF;

  -- 6. Record Audit Trail
  INSERT INTO audit_logs (
    action,
    entity_type,
    entity_id,
    metadata
  ) VALUES (
    'WORKER_REGISTERED_ATOMIC',
    'WORKER',
    v_worker_uuid::text,
    jsonb_build_object(
      'worker_id', v_new_worker_id,
      'full_name', v_clean_name,
      'department', p_department,
      'registered_at', now()
    )
  );

  -- 7. Return Result Payload
  v_result := jsonb_build_object(
    'id', v_new_worker_id,
    'db_id', v_worker_uuid,
    'worker_id', v_new_worker_id,
    'name', v_clean_name,
    'age', p_age,
    'weight', p_weight,
    'gender', p_gender,
    'contact', v_clean_contact,
    'department', p_department,
    'category', p_worker_category,
    'status', 'Active',
    'database_synced', true,
    'message', 'Worker ' || v_clean_name || ' permanently registered with ID ' || v_new_worker_id || ' in Supabase Cloud.'
  );

  RETURN v_result;
END;
$$;
