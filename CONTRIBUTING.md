# Contributing to LawerAI (Qanoon Sahayak)

Thank you for your interest in contributing to **LawerAI / Qanoon Sahayak** (قانون معاون), an open-source, grounded legal intake and statutory reasoning platform for Pakistani law.

The platform is designed to make Pakistani legal procedures accessible to ordinary citizens while maintaining strict, zero-hallucination statutory grounding, directional fidelity, and ethical safety standards.

---

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [Prerequisites & System Dependencies](#prerequisites--system-dependencies)
3. [Local Development Setup](#local-development-setup)
4. [Project Architecture](#project-architecture)
5. [Development Standards & Guidelines](#development-standards--guidelines)
6. [Testing & The 30-Case Hard-Mode Evaluation Harness](#testing--the-30-case-hard-mode-evaluation-harness)
7. [Contributing Statutory Corpus Data](#contributing-statutory-corpus-data)
8. [Submitting Pull Requests](#submitting-pull-requests)
9. [Reporting Security Issues](#reporting-security-issues)

---

## Code of Conduct
We are committed to providing a welcoming, inclusive, and professional environment. Treat all contributors, maintainers, and community members with respect and courtesy.

---

## Prerequisites & System Dependencies

- **Python**: 3.12+
- **Node.js**: 18+ (Node 20+ recommended)
- **Tesseract OCR**: Required for OCR extraction on uploaded legal documents (FIRs, cheques, contracts).
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-urd`
  - macOS: `brew install tesseract tesseract-lang`
- **Poppler Utilities**: Required for PDF document processing (`pdftotext`).
  - Ubuntu/Debian: `sudo apt-get install poppler-utils`
  - macOS: `brew install poppler`

---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/lawerai.git
cd lawerai
```

### 2. Configure Environment
Copy the example environment file:
```bash
cp .env.example .env
```
For local development, SQLite and local storage work out of the box with zero external configuration. If you wish to test with Google Gemini or OpenAI, fill in your API key in `.env`.

### 3. Backend Setup
Create and activate a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

Run database migrations:
```bash
alembic upgrade head
```

Start the FastAPI development server:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
API Documentation will be available at: `http://localhost:8000/docs`

### 4. Frontend Setup
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
The React frontend will be accessible at: `http://localhost:5173`

---

## Project Architecture

```
lawerai/
├── backend/                  # FastAPI Application
│   ├── config.py             # Typed Pydantic Settings & Secret Validator
│   ├── database.py           # SQLAlchemy Async Engine, Models & Encryption
│   ├── encryption.py         # Fernet + PBKDF2 Key Derivation (AES-128-CBC)
│   ├── storage_service.py    # Local & S3/R2 Object Storage Service
│   ├── rate_limiter.py       # SlowAPI In-Memory / Redis Rate Limiter
│   ├── reasoning_engine.py   # Multi-Issue Legal Segmentation & Fact Extraction
│   ├── llm_service.py        # Plain-Language LLM Generator (Gemini/Claude/GPT)
│   ├── ocr_service.py        # Tesseract + PyPDF Document Parser
│   ├── safety.py             # Emergency Helpline Interception & Safeguards
│   ├── routers/              # Auth, Chat, Lawyer Directory, Corpus, Feedback
│   └── tests/                # Comprehensive Pytest Suite (90+ Tests)
├── data/
│   ├── legal_corpus/         # Curated Pakistani Statutes (PPC, CrPC, CPC, etc.)
│   └── lawyer_directory.json # Verified Legal Aid & Advocate Directory
├── evaluation/               # Autonomous Evaluation & Grading Harness
│   ├── scenario_generator.py # 30 Adversarial Trap Scenarios Generator
│   ├── runner.py             # Async Evaluation Pipeline Execution
│   ├── grader.py             # Hallucination, Direction & Plain-Language Grader
│   └── run_eval.py           # CLI Entrypoint (--hard-mode, --categories)
├── frontend/                 # Vite + React 18 + Tailwind CSS SPA
│   ├── src/components/       # UI Components (ChatArea, Feedback, BetaGate)
│   └── vercel.json           # Vercel SPA Routing & Security Headers
├── alembic/                  # Database Migration Scripts
├── Dockerfile                # Production Multi-Stage Container Definition
└── .env.example              # Sanitized Environment Variable Template
```

---

## Development Standards & Guidelines

### 1. Plain-Language Requirement
- **No Unexplained Legal Jargon**: Never output archaic Latin maxims or complex terms like *jurisdiction*, *decree*, *ad-interim restraining order*, *prima facie*, *balance of convenience*, or *rendition of accounts* without immediate, plain-English/Urdu explanations.
- **Explain Like Talking to a Friend**: An individual with no formal legal education should understand exactly what occurred and what concrete steps to take next.
- **Never Repeat Legal Disclaimers in Chat Turns**: The legal disclaimer is delivered once in the initial greeting and rendered persistently in the top banner.

### 2. Zero-Tolerance for Hallucinated Citations
- Any citation returned **must** exist in the curated statutory corpus.
- If a user inquiry falls outside Pakistani statutory coverage (e.g., admiralty salvage, cryptocurrency disputes, foreign immigration), the engine **must gracefully decline** to cite unrelated laws. Never substitute unrelated statutes (e.g., NEPRA electricity laws or MFLO divorce procedures for land disputes).

### 3. Directional & Role Fidelity
- Distinguish aggrieved parties from accused parties. E.g., a tenant locked out by a landlord must be directed toward recovery under Specific Relief Act Section 9, not landlord eviction under rent ordinances.

---

## Testing & The 30-Case Hard-Mode Evaluation Harness

### Running Unit & Integration Tests
Before submitting any changes, ensure all unit tests pass:
```bash
PYTHONPATH=. pytest backend/tests/ -v
```

### Running the 30-Case Adversarial Evaluation Harness
The project includes a 30-case "Hard Mode" evaluation suite spanning 6 adversarial categories:
1. Cross-domain traps (e.g., dower vs. contract gift)
2. Directional / misleading framing (e.g., false theft FIRs)
3. Genuine legal gaps (e.g., cryptocurrency recovery, unstatuted modern disputes)
4. Multi-layered issues (3+ combined civil/criminal facts)
5. Novel statutes & procedural traps (confessions under duress, limitation periods)
6. Mixed Roman Urdu & colloquial dialect queries

To run the full adversarial evaluation:
```bash
PYTHONPATH=. python -m evaluation.run_eval --hard-mode --batch-size 30 --export hard_mode_results.json
```

All 30 scenarios must achieve a **PASS** verdict with 0 hallucinated citations and 0 directional inversions.

---

## Contributing Statutory Corpus Data
Statutes reside in `data/legal_corpus/*.json`. When contributing or updating acts:
1. Provide the official Act Name, Year, and Province/Federal jurisdiction.
2. Structure each section with:
   - `id`: Unique identifier (e.g., `ppc_sec_420`)
   - `act_code`: Standard legal abbreviation (e.g., `PPC 1860`)
   - `section_number`: e.g., `420`
   - `title`: Section title
   - `content`: Verbatim statutory text
   - `summary_plain`: Plain-language explanation for non-lawyers
   - `keywords`: Practical search terms

---

## Submitting Pull Requests
1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Commit your changes with clear, descriptive commit messages.
3. Verify all tests pass (`pytest backend/tests/`).
4. Push to your fork and submit a Pull Request to `main`.
5. Clearly describe the problem solved, testing methodology, and any changes made to reasoning or corpus data.

---

## Reporting Security Issues
Do not file public GitHub issues for security vulnerabilities, secret exposures, or safety risks. Please email the core maintainers directly or use GitHub's private vulnerability reporting feature.
