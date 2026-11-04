# KOSHA LABS – Industrial Worker Identity Management System
## Backend Architecture, Supabase Migrations & Biometric REST API

This repository contains the backend architecture for the **KOSHA LABS Intelligent Worker Identity Management System**.

### Core Business Rule
- **ONE WORKER = ONE PERMANENT WORKER ID**
- **ONE WORKER = MULTIPLE FINGERPRINT TEMPLATES**
- **ONE WORKER = MULTIPLE RECORDING SESSIONS**
- **NEVER CREATE A DUPLICATE WORKER RECORD WHEN AN EXISTING WORKER RETURNS.**

---

## 1. Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application & middleware
│   │   ├── config.py            # Pydantic environment configuration
│   │   ├── database.py          # Async SQLAlchemy engine
│   │   ├── dependencies.py      # Dependency injections
│   │   ├── models/              # SQLAlchemy ORM models (8 tables)
│   │   │   ├── worker.py
│   │   │   ├── biometric.py
│   │   │   ├── session.py
│   │   │   ├── site.py
│   │   │   ├── operator.py
│   │   │   ├── consent.py
│   │   │   ├── recognition.py
│   │   │   └── audit.py
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── routers/             # API routes (/api/workers, /api/biometrics, etc.)
│   │   ├── services/            # Business logic, deduplication & AES-256
│   │   ├── security/            # JWT authentication & RBAC
│   │   ├── ml/                  # Preprocessing, Siamese CNN & 1:N matcher
│   │   └── tests/               # Pytest suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── supabase/
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   └── 002_rls_policies.sql
│   └── seed.sql
├── server.ts                    # Full-stack Express + Vite dev server
└── src/                         # React 19 + TypeScript Mobile Frontend
```

---

## 2. Supabase Database Setup

Run the migrations in your Supabase project dashboard SQL editor or via the Supabase CLI:

```bash
# Apply initial schema (Tables 1-8, sequences, constraints, triggers)
supabase db push --file supabase/migrations/001_initial_schema.sql

# Apply Row Level Security policies
supabase db push --file supabase/migrations/002_rls_policies.sql

# Seed initial construction megaproject data
supabase db push --file supabase/seed.sql
```

---

## 3. Running the Python FastAPI Backend

### Prerequisites
- Python 3.10+
- PostgreSQL database

### Local Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your PostgreSQL credentials

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Docker Deployment
```bash
cd backend
docker build -t kosha-labs-backend .
docker run -p 8000:8000 --env-file .env kosha-labs-backend
```

---

## 4. Running the Full-Stack React + Node Server

The applet includes an integrated full-stack server (`server.ts`) that serves both the API routes (`/api/*`) and mounts the Vite mobile frontend on port 3000:

```bash
npm install
npm run dev
```

Visit `http://localhost:3000` to interact with the mobile application.

---

## 5. Machine Learning Siamese CNN Model

- **Embedding Dimension**: 128-dimensional unit normalized vectors.
- **Calibrated Matching Threshold**: $\ge 0.85$ (Instant Match), $0.60 \le s < 0.85$ (Supervisor Review).
- **Model File Placement**: Place trained model weights at `backend/app/ml/weights/siamese_cnn_socofing_v1.h5`.
- **Model Guarantee**: If weights are missing, the system strictly returns `MODEL_NOT_CONFIGURED` without fabricating artificial embeddings.

---

## 6. Running Automated Tests

```bash
cd backend
pytest app/tests/ -v
```
