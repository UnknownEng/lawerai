# LawerAI / Qanoon Sahayak (قانون معاون)

> **MANDATORY LEGAL DISCLAIMER:**  
> **LawerAI / Qanoon Sahayak is an educational and legal information platform grounded in Pakistani statutory law. It is NOT a replacement for a qualified advocate and does NOT provide formal legal representation, advocacy, or attorney-client privileged counsel. The platform does not predict court outcomes or guarantee legal relief. For formal legal filings, drafting, or representation in Pakistani courts, you must consult an advocate enrolled with the relevant Provincial Bar Council or Pakistan Bar Council.**

---

## 1. Overview & Vision

**LawerAI (Qanoon Sahayak)** is an open-source, production-grade legal intake and statutory reasoning platform built specifically for the legal system of Pakistan.

Navigating Pakistan's legal system is intimidating and opaque for ordinary citizens facing crises — whether it is an illegal tenant eviction, a bounced cheque, police refusal to register an FIR, harassment, or a property dispute. LawerAI bridges this gap by providing an initial legal consultation that:
1. Explains rights, remedies, and procedures in **plain, jargon-free everyday language** (in English, Urdu اردو, or Roman Urdu).
2. Grounds every assertion in **verified Pakistani statutes** (PPC, CrPC, CPC, QSO, Specific Relief Act, Family Laws, Rent Laws, PECA).
3. Enforces **zero tolerance for hallucinated citations** — refusing to invent or misapply unrelated laws when a matter falls outside statutory scope.
4. Distinguishes between **aggrieved and accused parties** through directional role awareness.
5. Employs a **one-question-at-a-time conversational intake** that incrementally builds a live structured Case Summary and downloadable dossier.
6. Intercepts life-threatening emergencies (domestic violence, self-harm) immediately with verified Pakistani crisis helplines (15, 1043, 1098, Madadgar, Umang).

---

## 2. System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│             Vercel Frontend (React 18 + Tailwind CSS + Vite)           │
│  - Persistent BETA Review Warning Banner                               │
│  - Beta Gate Modal (Shared Invite-Code Authorization)                  │
│  - Assistant Response Feedback (Sound / Citation / Reasoning / Notes)  │
│  - Live Structured Case Summary Panel & HTML Dossier Export            │
│  - Trilingual Support: Urdu (RTL) / English / Roman Urdu               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTPS (Strict CORS Origins)
┌───────────────────────────────────▼────────────────────────────────────┐
│              Render / Fly.io Backend (FastAPI, Python 3.12)            │
│  - Rate Limiting Engine (SlowAPI: Chat, Uploads, Auth endpoints)       │
│  - Production Config Validator (Refuses boot on default secrets)       │
│  - Emergency Safety Interceptor (Helpline triage before LLM)           │
│  - Legal Reasoning Engine (Multi-issue segmentation & role awareness)  │
│  - Plain-Language Generation Pipeline (Friend-like explanations)       │
│  - Document OCR Service (Poppler + Tesseract for FIRs & cheques)       │
└──────────────────┬─────────────────┬───────────────────┬───────────────┘
                   │                 │                   │
┌──────────────────▼────────┐ ┌──────▼─────────────┐ ┌───▼───────────────┐
│ Cloudflare R2 / S3 Storage│ │ Managed PostgreSQL │ │ Hybrid Vector Store │
│ - Encrypted Case Evidence │ │ (Neon / Supabase)  │ │ - BM25 Lexical +    │
│ - Signed Expiring URLs    │ │ - Alembic Migrated │ │   Dense Embeddings  │
│ - Zero Public Mounts      │ │ - AES-128 Encrypted│ │ - Curated Statutes  │
└───────────────────────────┘ └────────────────────┘ └─────────────────────┘
```

---

## 3. Core Features

### 🛡️ Production Hardened & Security Focused
- **Zero Insecure Defaults**: The application strictly refuses to start in production if `JWT_SECRET_KEY` or `CASE_DATA_ENCRYPTION_KEY` match placeholder values.
- **Strong Key Derivation**: Uses PBKDF2-HMAC-SHA256 with 100,000 iterations and domain salt to derive 32-byte AES-128-CBC Fernet keys.
- **Encrypted at Rest**: All citizen messages, uploaded extracted text, and confidential feedback notes are encrypted at rest.
- **Secure Non-Public Storage**: Evidentiary files are uploaded to S3/Cloudflare R2; downloads require authenticated, short-lived presigned URLs.
- **Rate Limiting**: Defends endpoints against denial-of-service and credit exhaustion via SlowAPI (20 msgs/min, 10 uploads/min, 5 auth/min).
- **Strict CORS**: Enforces an explicit allowlist in production, rejecting wildcards.

### 🧪 Closed Lawyer-Review Beta Features
- **Invite-Code Gate**: Requires a shared secret code (`BETA_ACCESS_CODE`, e.g. `QANOON-BETA-2026`) to create accounts or initiate intake consultations, safeguarding LLM credits.
- **Persistent Beta Banner**: Unmissable amber warning across the entire interface reminding testers that output is under legal review.
- **In-UI Response Feedback**: Every assistant message card contains quick feedback actions:
  - 👍 **Sound**: Marks the analysis as legally accurate.
  - ⚠️ **Citation wrong**: Flags inapplicable or hallucinated sections.
  - ⚠️ **Reasoning wrong**: Flags flawed logic or inverted fact roles.
  - 💬 **Lawyer Notes**: Allows advocates to submit encrypted free-text comments logged to the database for model refinement.

### 🏛️ Grounded Statutory Knowledge Base
Every citation is anchored in primary Pakistani statutes:
- **Criminal & Procedural**: Pakistan Penal Code (PPC 1860), Code of Criminal Procedure (CrPC 1898), Qanun-e-Shahadat Order (QSO 1984).
- **Civil & Commercial**: Code of Civil Procedure (CPC 1908), Contract Act (1872), Specific Relief Act (1877), Motor Vehicles Ordinance (1965), Limitation Act (1908).
- **Family & Children**: Muslim Family Laws Ordinance (MFLO 1961), Family Courts Act (1964), Guardian and Wards Act (1890).
- **Property & Tenancy**: Punjab Rented Premises Act (2009), Sindh Rented Premises Ordinance (1979), Islamabad Rent Restriction Ordinance (2001), Illegal Dispossession Act (2005).
- **Cyber & Special**: Prevention of Electronic Crimes Act (PECA 2016), NEPRA Act (1997).

---

## 4. The 30-Case Adversarial "Hard Mode" Evaluation Harness

To prevent self-grading blind spots, hallucinated citations, and directional errors, LawerAI features a dedicated automated evaluation harness (`evaluation/run_eval.py`).

### 6 Evaluation Categories (5 Cases Each = 30 Cases)
1. **Cross-Domain Traps**: Questions that appear to belong to one area but legally belong to another (e.g., wedding gift dower vs. contract gift; regulatory inspection vs. anti-corruption).
2. **Directional & Role Traps**: Cases where surface reading suggests one party is the wrongdoer, but legally they are the aggrieved party (e.g., tenant locked out by landlord; false FIR threats).
3. **Genuine Legal Gaps**: Unstatuted modern disputes (cryptocurrency scams, freelance gig-work non-payment, Airbnb subletting). The model must acknowledge legal gaps and refuse to cite unrelated laws.
4. **Multi-Layered Issues**: Fact patterns containing 3+ simultaneous issues (e.g., unpaid salary + defamation + recovered company laptop) ensuring no issues are silently dropped.
5. **Procedural Traps & Novel Statutes**: Nuanced evidentiary and limitation rules (confessions under duress, single-witness blasphemy standards, limitation on land possession).
6. **Mixed Dialect & Roman Urdu**: Colloquial phrasing and idioms tested for legal parity with formal English.

### Run the Evaluation
```bash
# Run unit and integration tests (92 tests)
PYTHONPATH=. pytest backend/tests/ -v

# Run the 30-case adversarial evaluation
PYTHONPATH=. python -m evaluation.run_eval --hard-mode --batch-size 30 --export hard_mode_results.json
```

---

## 5. Deployment Guide

### Architecture at a Glance
| Component | Recommended Host | Cost (20–50 Beta Testers) |
| :--- | :--- | :--- |
| **Frontend SPA** | [Vercel](https://vercel.com) | **$0 / mo** (Hobby Tier) |
| **Python Backend** | [Render](https://render.com) or [Fly.io](https://fly.io) | **$7 / mo** (Starter 512MB–1GB RAM) |
| **Database** | [Neon](https://neon.tech) or [Supabase](https://supabase.com) | **$0 / mo** (Free Tier PostgreSQL) |
| **Object Storage** | [Cloudflare R2](https://www.cloudflare.com/developer-platform/r2/) | **$0 / mo** (First 10GB free, zero egress) |
| **LLM Inference** | [Google AI Studio (Gemini 2.5 Flash)](https://ai.google.dev/) | **~$2–$5 / mo** (or free tier) |
| **Total Estimated Cost** | | **~$7 – $12 / month** |

### Step 1: Provision Managed PostgreSQL (Neon / Supabase)
1. Sign up at [Neon](https://neon.tech).
2. Create a new project (e.g., `lawerai-production`).
3. Copy the pooled connection string. Ensure it uses the asyncpg driver prefix:
   ```
   postgresql+asyncpg://<USER>:<PASSWORD>@<HOST>/<DBNAME>?sslmode=require
   ```

### Step 2: Provision Cloudflare R2 for File Uploads
1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com) and navigate to **R2**.
2. Create a bucket named `lawerai-evidence-uploads`.
3. In **R2 > Manage API Tokens**, create a token with `Object Read & Write` permissions.
4. Record your `S3_ENDPOINT_URL`, `S3_ACCESS_KEY_ID`, and `S3_SECRET_ACCESS_KEY`.

### Step 3: Deploy Backend on Render or Fly.io
#### Deploying on Render:
1. Create a **New Web Service** connected to your repository.
2. Select **Docker** as the runtime (it will automatically use the root `Dockerfile`).
3. Set Environment Variables:
   - `ENVIRONMENT`: `production`
   - `DATABASE_URL`: Your Neon async PostgreSQL URL
   - `JWT_SECRET_KEY`: Generated via `openssl rand -hex 32`
   - `CASE_DATA_ENCRYPTION_KEY`: Generated via `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
   - `STORAGE_BACKEND`: `s3`
   - `S3_ENDPOINT_URL`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME`
   - `ALLOWED_ORIGINS`: `https://your-frontend.vercel.app`
   - `REQUIRE_BETA_CODE`: `true`
   - `BETA_ACCESS_CODE`: `QANOON-BETA-2026`
   - `GEMINI_API_KEY`: Your Google Gemini API key
4. Add a **Pre-Deploy Command** (or run manually):
   ```bash
   alembic upgrade head
   ```

### Step 4: Deploy Frontend on Vercel
1. Sign up at [Vercel](https://vercel.com) and click **Add New Project**.
2. Select the repository and set **Root Directory** to `frontend`.
3. Framework Preset: **Vite**.
4. Set Environment Variable:
   - `VITE_API_URL`: `https://your-backend.onrender.com`
5. Deploy. The `frontend/vercel.json` file ensures proper SPA client-side routing and security headers.

---

## 6. Local Quickstart

```bash
# 1. Clone & enter
git clone https://github.com/your-username/lawerai.git
cd lawerai

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 3. Environment file
cp .env.example .env

# 4. Run migrations
alembic upgrade head

# 5. Start backend
uvicorn backend.main:app --reload --port 8000

# 6. Start frontend
cd frontend
npm install
npm run dev
```

---

## 7. Open Source License & Liability Defense

This project is licensed under the **Apache License, Version 2.0**.

### Why Apache 2.0 Was Chosen Over MIT
Given the legal sensitivity of an AI providing procedural information in Pakistan:
- **Section 8 (Limitation of Liability)**: Expressly disclaims any liability for direct, indirect, special, or consequential damages under any legal theory, including negligence.
- **Section 9 (Indemnification)**: Protects original authors by obligating anyone who redistributes or provides commercial warranties on the software to indemnify and hold harmless the original contributors.
- **Section 3 (Patent Retaliation)**: Provides explicit protection against patent claims, terminating the license of anyone who files patent litigation against the software.
- **Section 6 (Trademarks)**: Explicitly protects the names "LawerAI" and "Qanoon Sahayak" from unauthorized commercial appropriation.

See [LICENSE](file:///home/kali/lawerai/LICENSE) for complete terms.
