# KOSHA LABS – Intelligent Worker Identity Management System
> **One Worker. One Identity. Multiple Sessions.**
> Built for Mobile (Android & iOS) via React, TypeScript, Tailwind CSS & Capacitor.
> Backed by Supabase PostgreSQL and Python FastAPI Siamese CNN Biometric Engine.

---

## 🏗️ Architecture & Philosophy

In industrial workforce management (infrastructure, tunneling, heavy construction, mining, maritime ports), duplicate worker registrations lead to ghost workers, double payouts, safety violations, and compliance audit failures.

**Kosha Labs enforces zero duplicate registrations**:
1. **One Permanent Worker ID (`WK-XXXX`)**: Minted transactionally at initial enrollment and immutable for life.
2. **Multiple Biometric Templates**: Enrolls multiple fingers (e.g., Right Thumb, Right Index, Left Thumb) with optical 500 DPI minutiae ridge extraction and 128-dimensional Siamese CNN embeddings.
3. **Multiple Recording Sessions (`SES-XXXX`)**: Every shift, daily clock-in, or gate passage creates a new recording session tied back to the worker's single permanent ID.
4. **Automated Re-identification**: Returning workers place their finger on the terminal scanner; the system performs 1:N biometric search and pulls up existing worker records instantly without re-registration.
5. **Supervisor Verification Queue**: Borderline scans (60%–85% confidence) are automatically routed to a manual verification queue for human authorization.

---

## 🚀 Quick Start (Full-Stack Dev Server)

### 1. Prerequisites
- Node.js 18+ (Node 20+ recommended)
- Python 3.10+ (for ML recognition service)

### 2. Install Frontend & Full-Stack Server Dependencies
```bash
npm install
```

### 3. Run Development Server (Port 3000)
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.
Use the built-in device switcher in the top bar to preview on **iPhone 16 Pro**, **Google Pixel 8**, **iPad Mini**, or responsive full-screen.

---

## 🗄️ Supabase PostgreSQL Setup

The project is pre-configured for your Supabase Cloud instance:
- **Project URL**: `https://bhnrrosrjednzctdirkn.supabase.co`
- **Project Ref**: `bhnrrosrjednzctdirkn`

### Initializing Tables via SQL Editor
1. Log into your Supabase Dashboard: [https://supabase.com/dashboard/project/bhnrrosrjednzctdirkn/sql/new](https://supabase.com/dashboard/project/bhnrrosrjednzctdirkn/sql/new)
2. Copy the migration file contents from `supabase/migrations/001_initial_schema.sql` (or click **"Copy Schema SQL"** in the mobile app under the **Profile > Supabase Database** section).
3. Paste into the Supabase SQL Editor and click **Run**.
4. (Optional) Run `supabase/migrations/002_rls_policies.sql` to activate Row Level Security.
5. (Optional) Run `supabase/seed.sql` to populate sample construction site records.

### Environment Variables (`.env`)
```env
VITE_SUPABASE_URL="https://bhnrrosrjednzctdirkn.supabase.co"
VITE_SUPABASE_ANON_KEY="sb_publishable_UEgdn1EB40terFHDApHIYQ_tr3ZQATH"
SUPABASE_URL="https://bhnrrosrjednzctdirkn.supabase.co"
SUPABASE_ANON_KEY="sb_publishable_UEgdn1EB40terFHDApHIYQ_tr3ZQATH"
SUPABASE_SECRET_KEY="YOUR_SUPABASE_SECRET_KEY"
SUPABASE_JWKS_URL="https://bhnrrosrjednzctdirkn.supabase.co/auth/v1/.well-known/jwks.json"
```

---

## 🧠 Python FastAPI Siamese CNN Recognition Engine

The standalone biometric recognition microservice is located in `/backend`.

### Run Python API
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📱 Mobile Packaging (Android & iOS with Capacitor)

This repository is built with a Capacitor-ready architecture:

### 1. Build Web Assets
```bash
npm run build
```

### 2. Install Capacitor CLI (if not already installed)
```bash
npm install -g @capacitor/cli @capacitor/core
```

### 3. Initialize & Add Mobile Platforms
```bash
npx cap init "Kosha Labs" "com.koshalabs.workerid" --web-dir "dist"
npm install @capacitor/android @capacitor/ios
npx cap add android
npx cap add ios
```

### 4. Open in Android Studio or Xcode
```bash
# For Android:
npx cap open android

# For iOS:
npx cap open ios
```

---

## 📄 License
Proprietary & Confidential · Kosha Labs Inc.
