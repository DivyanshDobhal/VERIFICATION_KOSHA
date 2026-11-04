-- ============================================================================
-- KOSHA LABS – Supabase PostgreSQL Initial Migration
-- Migration 001: Core Worker Identity, Biometrics, Sessions & Audit Schema
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- SEQUENCES: Secure transactional sequential identifiers
-- ----------------------------------------------------------------------------
CREATE SEQUENCE IF NOT EXISTS worker_id_seq START WITH 1001 INCREMENT BY 1;
CREATE SEQUENCE IF NOT EXISTS session_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE IF NOT EXISTS review_id_seq START WITH 301 INCREMENT BY 1;

-- Functions to generate formatted permanent identifiers
CREATE OR REPLACE FUNCTION generate_worker_id() RETURNS TEXT AS $$
BEGIN
  RETURN 'WK-' || LPAD(nextval('worker_id_seq')::TEXT, 4, '0');
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_session_id() RETURNS TEXT AS $$
BEGIN
  RETURN 'SES-' || LPAD(nextval('session_id_seq')::TEXT, 3, '0');
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_review_id() RETURNS TEXT AS $$
BEGIN
  RETURN 'REV-' || LPAD(nextval('review_id_seq')::TEXT, 3, '0');
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- TABLE 4: sites (Infrastructure projects & turnstile gates)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id TEXT UNIQUE NOT NULL, -- e.g. 'SITE-M4'
  site_name TEXT NOT NULL,
  location TEXT NOT NULL,
  contractor TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- TABLE 5: operators (Field biometrics operators, supervisors, admins)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS operators (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_user_id UUID UNIQUE, -- Foreign key to auth.users in Supabase Auth
  full_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin', 'operator', 'supervisor')),
  assigned_site_id UUID REFERENCES sites(id) ON DELETE SET NULL,
  badge_number TEXT UNIQUE NOT NULL,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- TABLE 1: workers (Permanent worker identity records)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS workers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  worker_id TEXT UNIQUE NOT NULL DEFAULT generate_worker_id(),
  full_name TEXT NOT NULL,
  age INTEGER NOT NULL CHECK (age >= 18 AND age <= 75),
  weight NUMERIC(5, 2) NOT NULL CHECK (weight >= 35.0 AND weight <= 180.0),
  gender TEXT CHECK (gender IN ('Male', 'Female', 'Other', 'Prefer not to say')),
  contact_number TEXT,
  emergency_contact TEXT,
  blood_group TEXT,
  site_id UUID REFERENCES sites(id) ON DELETE SET NULL,
  department TEXT NOT NULL,
  worker_category TEXT NOT NULL CHECK (worker_category IN ('General Labour', 'Specialist Technician', 'Heavy Equipment Operator', 'Foreman / Supervisor')),
  additional_metadata JSONB DEFAULT '{}'::jsonb,
  registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'under_review', 'flagged')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workers_worker_id ON workers(worker_id);
CREATE INDEX IF NOT EXISTS idx_workers_full_name ON workers(full_name);
CREATE INDEX IF NOT EXISTS idx_workers_site_id ON workers(site_id);
CREATE INDEX IF NOT EXISTS idx_workers_status ON workers(status);

-- ----------------------------------------------------------------------------
-- TABLE 6: biometric_consents (Legal GDPR / workforce biometric consents)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS biometric_consents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
  consent_status BOOLEAN NOT NULL DEFAULT true,
  consent_version TEXT NOT NULL DEFAULT 'v2.4',
  consent_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  purpose TEXT NOT NULL DEFAULT 'Industrial deduplication & attendance authentication',
  withdrawal_timestamp TIMESTAMPTZ,
  recorded_by_operator_id UUID REFERENCES operators(id)
);

CREATE INDEX IF NOT EXISTS idx_biometric_consents_worker ON biometric_consents(worker_id);

-- ----------------------------------------------------------------------------
-- TABLE 2: biometric_templates (Encrypted fingerprint templates)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS biometric_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
  finger_type TEXT NOT NULL CHECK (finger_type IN ('Right Thumb', 'Left Thumb', 'Right Index', 'Left Index', 'Right Middle', 'Left Middle')),
  encrypted_embedding BYTEA NOT NULL, -- AES-256 encrypted 128-dim vector
  embedding_dimension INTEGER NOT NULL DEFAULT 128,
  template_hash TEXT UNIQUE NOT NULL, -- SHA-256 hash for fast deduplication check
  quality_score NUMERIC(5, 2) NOT NULL CHECK (quality_score >= 0 AND quality_score <= 100),
  model_version TEXT NOT NULL DEFAULT 'kosha-siamese-v1.4',
  consent_record_id UUID REFERENCES biometric_consents(id) ON DELETE SET NULL,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'revoked')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_biometric_templates_worker ON biometric_templates(worker_id);
CREATE INDEX IF NOT EXISTS idx_biometric_templates_hash ON biometric_templates(template_hash);

-- ----------------------------------------------------------------------------
-- TABLE 3: recording_sessions (Daily check-ins linked to permanent Worker ID)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recording_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT UNIQUE NOT NULL DEFAULT generate_session_id(),
  worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE RESTRICT,
  site_id UUID NOT NULL REFERENCES sites(id) ON DELETE RESTRICT,
  operator_id UUID REFERENCES operators(id) ON DELETE SET NULL,
  session_date DATE NOT NULL DEFAULT CURRENT_DATE,
  session_time TIME NOT NULL DEFAULT CURRENT_TIME,
  recognition_method TEXT NOT NULL DEFAULT 'Fingerprint Biometric - Optical 500DPI',
  session_metadata JSONB DEFAULT '{}'::jsonb,
  idempotency_key TEXT UNIQUE NOT NULL,
  status TEXT NOT NULL DEFAULT 'Verified & Active' CHECK (status IN ('Verified & Active', 'Completed', 'Safety Flagged', 'Cancelled')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_worker_id ON recording_sessions(worker_id);
CREATE INDEX IF NOT EXISTS idx_sessions_site_id ON recording_sessions(site_id);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON recording_sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_sessions_idempotency ON recording_sessions(idempotency_key);

-- ----------------------------------------------------------------------------
-- TABLE 7: recognition_logs (Biometric matching audit & manual verification)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recognition_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  review_id TEXT UNIQUE DEFAULT generate_review_id(),
  operator_id UUID REFERENCES operators(id) ON DELETE SET NULL,
  site_id UUID REFERENCES sites(id) ON DELETE SET NULL,
  scanned_finger TEXT NOT NULL,
  recognition_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  result_status TEXT NOT NULL CHECK (result_status IN ('MATCH', 'UNCERTAIN', 'NO_MATCH', 'ERROR')),
  confidence_score NUMERIC(5, 2),
  matched_worker_id UUID REFERENCES workers(id) ON DELETE SET NULL,
  secondary_candidate_id UUID REFERENCES workers(id) ON DELETE SET NULL,
  review_status TEXT NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending', 'approved', 'rejected', 'recaptured', 'not_required')),
  model_version TEXT NOT NULL DEFAULT 'kosha-siamese-v1.4',
  review_notes TEXT,
  resolved_at TIMESTAMPTZ,
  resolved_by_operator_id UUID REFERENCES operators(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_recognition_logs_status ON recognition_logs(review_status);
CREATE INDEX IF NOT EXISTS idx_recognition_logs_site ON recognition_logs(site_id);

-- ----------------------------------------------------------------------------
-- TABLE 8: audit_logs (Immutable audit trail for compliance and security)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID, -- Actor ID
  action TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id TEXT,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);

-- ----------------------------------------------------------------------------
-- TRIGGER: Auto-update updated_at timestamp on workers
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_timestamp() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_workers_updated_at
BEFORE UPDATE ON workers
FOR EACH ROW EXECUTE FUNCTION update_timestamp();
