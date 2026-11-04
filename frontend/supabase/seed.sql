-- ============================================================================
-- KOSHA LABS – Supabase PostgreSQL Initial Seed Data
-- ============================================================================

-- 1. Insert Sites
INSERT INTO sites (id, site_id, site_name, location, contractor, status) VALUES
  ('a1b2c3d4-0001-4000-8000-000000000001', 'SITE-M4', 'Metro Line 4 Underground Expansion', 'Central Corridor, Sector 12', 'L&T Infrastructure Corp', 'active'),
  ('a1b2c3d4-0002-4000-8000-000000000002', 'SITE-T3', 'Terminal 3 Cargo & Logistics Bay', 'Aerocity Access Spine', 'GMR MegaProjects JV', 'active'),
  ('a1b2c3d4-0003-4000-8000-000000000003', 'SITE-HR', 'Harbor Rail Freight Flyover', 'Port Terminal Gate 5', 'Afcons Railtech Ltd', 'active')
ON CONFLICT (site_id) DO NOTHING;

-- 2. Insert Operators
INSERT INTO operators (id, full_name, email, role, assigned_site_id, badge_number, status) VALUES
  ('b1b2c3d4-0001-4000-8000-000000000001', 'Vikram Sethi', 'v.sethi@koshalabs.internal', 'operator', 'a1b2c3d4-0001-4000-8000-000000000001', 'KOSHA-OP-892', 'active'),
  ('b1b2c3d4-0002-4000-8000-000000000002', 'Pooja Deshmukh', 'p.deshmukh@koshalabs.internal', 'supervisor', 'a1b2c3d4-0001-4000-8000-000000000001', 'KOSHA-SUP-104', 'active'),
  ('b1b2c3d4-0003-4000-8000-000000000003', 'Admin Office', 'admin@koshalabs.internal', 'admin', NULL, 'KOSHA-ADM-001', 'active')
ON CONFLICT (email) DO NOTHING;

-- 3. Insert Workers with Permanent IDs
INSERT INTO workers (id, worker_id, full_name, age, weight, gender, contact_number, emergency_contact, blood_group, site_id, department, worker_category, additional_metadata, registration_date, status) VALUES
  ('c1b2c3d4-0001-4000-8000-000000000001', 'WK-1001', 'Rameshwar Prasad Gurjar', 38, 71.0, 'Male', '+91 98210 44812', 'Sunita Gurjar (+91 94140 12890)', 'B+', 'a1b2c3d4-0001-4000-8000-000000000001', 'Structural Rigging', 'Heavy Equipment Operator', '{"certifications": ["Boom Lift Level 3", "Overhead Rigging"]}'::jsonb, '2026-10-14', 'active'),
  ('c1b2c3d4-0002-4000-8000-000000000002', 'WK-1002', 'Dilip Kumar Mondal', 29, 64.0, 'Male', '+91 97340 55198', 'Bro (+91 89100 23145)', 'O+', 'a1b2c3d4-0001-4000-8000-000000000001', 'Tunneling Excavation', 'Specialist Technician', '{"certifications": ["TBM Cutter Ring"]}'::jsonb, '2026-10-18', 'active'),
  ('c1b2c3d4-0003-4000-8000-000000000003', 'WK-1003', 'Anjali Devi Soren', 32, 56.0, 'Female', '+91 96120 78234', 'Family (+91 96120 78999)', 'A+', 'a1b2c3d4-0002-4000-8000-000000000002', 'Electrical Systems & MEP', 'Specialist Technician', '{"certifications": ["High Voltage Panel"]}'::jsonb, '2026-10-22', 'active'),
  ('c1b2c3d4-0004-4000-8000-000000000004', 'WK-1004', 'Mohammed Zubair Khan', 44, 78.0, 'Male', '+91 98450 11982', 'Arshad Khan (+91 98450 11999)', 'AB+', 'a1b2c3d4-0001-4000-8000-000000000001', 'Safety & Scaffolding', 'Foreman / Supervisor', '{"certifications": ["Toolbox Compliance Lead"]}'::jsonb, '2026-10-25', 'active')
ON CONFLICT (worker_id) DO NOTHING;

-- 4. Insert Biometric Consents
INSERT INTO biometric_consents (id, worker_id, consent_status, consent_version, purpose) VALUES
  ('d1b2c3d4-0001-4000-8000-000000000001', 'c1b2c3d4-0001-4000-8000-000000000001', true, 'v2.4', 'Industrial deduplication & attendance authentication'),
  ('d1b2c3d4-0002-4000-8000-000000000002', 'c1b2c3d4-0002-4000-8000-000000000002', true, 'v2.4', 'Industrial deduplication & attendance authentication')
ON CONFLICT DO NOTHING;

-- 5. Insert Biometric Templates (Encrypted bytea representations)
INSERT INTO biometric_templates (id, worker_id, finger_type, encrypted_embedding, embedding_dimension, template_hash, quality_score, model_version) VALUES
  ('e1b2c3d4-0001-4000-8000-000000000001', 'c1b2c3d4-0001-4000-8000-000000000001', 'Right Thumb', decode('30820120300d06092a864886f70d01010105000382010f00', 'hex'), 128, 'HASH_RT_WK1001_A98F', 96.0, 'kosha-siamese-v1.4'),
  ('e1b2c3d4-0002-4000-8000-000000000002', 'c1b2c3d4-0001-4000-8000-000000000001', 'Right Index', decode('30820120300d06092a864886f70d01010105000382010f01', 'hex'), 128, 'HASH_RI_WK1001_B412', 92.0, 'kosha-siamese-v1.4'),
  ('e1b2c3d4-0003-4000-8000-000000000003', 'c1b2c3d4-0002-4000-8000-000000000002', 'Right Thumb', decode('30820120300d06092a864886f70d01010105000382010f02', 'hex'), 128, 'HASH_RT_WK1002_C899', 94.0, 'kosha-siamese-v1.4')
ON CONFLICT (template_hash) DO NOTHING;

-- 6. Insert Multiple Recording Sessions for WK-1001 proving: ONE WORKER = MULTIPLE SESSIONS!
INSERT INTO recording_sessions (id, session_id, worker_id, site_id, operator_id, session_date, session_time, recognition_method, session_metadata, idempotency_key, status) VALUES
  ('f1b2c3d4-0001-4000-8000-000000000001', 'SES-001', 'c1b2c3d4-0001-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001', 'b1b2c3d4-0001-4000-8000-000000000001', '2026-11-01', '06:10:00', 'Fingerprint Biometric - Optical 500DPI', '{"gate": "North Gate Turnstile 2", "score": 97.2}'::jsonb, 'IDEMP-SES-001-20261101', 'Completed'),
  ('f1b2c3d4-0002-4000-8000-000000000002', 'SES-002', 'c1b2c3d4-0001-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001', 'b1b2c3d4-0001-4000-8000-000000000001', '2026-11-02', '06:12:00', 'Fingerprint Biometric - Optical 500DPI', '{"gate": "North Gate Turnstile 2", "score": 96.8}'::jsonb, 'IDEMP-SES-002-20261102', 'Completed'),
  ('f1b2c3d4-0003-4000-8000-000000000003', 'SES-003', 'c1b2c3d4-0001-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001', 'b1b2c3d4-0001-4000-8000-000000000001', '2026-11-03', '06:15:00', 'Fingerprint Biometric - Optical 500DPI', '{"gate": "Shaft 4 Access Bay", "score": 98.4}'::jsonb, 'IDEMP-SES-003-20261103', 'Verified & Active')
ON CONFLICT (session_id) DO NOTHING;
