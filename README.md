# OncoNexus AI

**A Multi-Agent Intelligent Cancer Care Platform for Risk Assessment, Medical
Report Understanding, Personalized Guidance, Rehabilitation, and Patient
Support Using Large Language Models.**

> Status: **Project foundation stage.** No product features (auth, ML, OCR,
> agents, dashboards) are implemented yet. This repository currently contains
> a production-grade, modular scaffold that all future modules will build on.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Local Setup (without Docker)](#local-setup-without-docker)
- [Running with Docker](#running-with-docker)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Next Implementation Steps](#next-implementation-steps)

---

## Tech Stack

| Layer      | Technologies |
|------------|--------------|
| Frontend   | React 19, Vite, TypeScript, TailwindCSS, shadcn/ui, React Router, TanStack Query, Axios, React Hook Form, Zod, Framer Motion, Recharts |
| Backend    | FastAPI, Python 3.12, SQLAlchemy 2.x, Alembic, PostgreSQL, JWT |
| AI         | LangChain, LangGraph, Sentence Transformers, FAISS |
| ML         | Scikit-learn, XGBoost, SHAP |
| OCR        | PaddleOCR, Tesseract OCR |
| Deployment | Docker, Docker Compose |

## Project Structure

```
OncoNexusAI/
├── frontend/            # React 19 + Vite + TypeScript SPA
├── backend/              # FastAPI application (Clean Architecture)
├── docs/                 # Architecture & onboarding documentation
├── datasets/             # Training/reference datasets (gitignored contents)
├── trained_models/       # Serialized ML model artifacts (gitignored contents)
├── research/             # Notebooks, papers, experiment notes
├── docker/               # Shared/root-level Docker assets
├── .github/workflows/    # CI pipelines
├── docker-compose.yml           # Development orchestration
├── docker-compose.prod.yml      # Production overrides
├── README.md
└── LICENSE
```

### Backend (`backend/app/`)

```
api/v1/endpoints/   # Versioned route handlers
core/config/        # Centralized settings (pydantic-settings)
core/logging.py     # Logging configuration
database/           # SQLAlchemy async engine, session, declarative base
models/              # ORM models (base mixins for now)
schemas/             # Pydantic request/response contracts
services/            # Business logic layer (empty — future modules)
repositories/        # Data-access layer (empty — future modules)
agents/              # LangGraph multi-agent orchestration (empty)
ml/                  # Risk-assessment ML models (empty)
rag/                 # Retrieval-augmented generation (empty)
ocr/                 # Medical report OCR pipeline (empty)
auth/                # JWT authentication (empty)
middleware/          # Request logging middleware
exceptions/          # Exception hierarchy + global handlers
common/              # Shared constants & response envelopes
utils/               # Stateless helpers
```

### Frontend (`frontend/src/`)

```
components/{ui,common}/  # Reusable UI building blocks
pages/                    # Route-level components
layouts/                  # Shared page chrome
hooks/                    # Reusable stateful logic
contexts/                 # React context providers (empty — future modules)
services/                 # Axios client + TanStack Query wiring
routes/                   # Route table
types/                    # Shared TypeScript contracts
utils/                    # Stateless helpers
assets/, styles/          # Static assets & global CSS
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full architectural
rationale and the dependency rules between layers.

## Prerequisites

- Python 3.12+
- Node.js 22+ and npm
- PostgreSQL 16 (or use the provided Docker service)
- Docker & Docker Compose (recommended)
- Tesseract OCR binary (only required once OCR features are implemented)

## Local Setup (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env             # then fill in real values
alembic upgrade head              # applies migrations (none yet at this stage)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend will be available at `http://localhost:5173`.

## Running with Docker

```bash
# From the repository root
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Development (hot-reload for both services)
docker compose up --build

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Services:

| Service  | Dev URL                     | Notes |
|----------|------------------------------|-------|
| frontend | http://localhost:5173        | Vite dev server (prod: served by nginx on port 80) |
| backend  | http://localhost:8000        | FastAPI + Uvicorn |
| db       | localhost:5432                | PostgreSQL 16 |

Stop everything:

```bash
docker compose down
```

Remove volumes too (⚠️ deletes the database):

```bash
docker compose down -v
```

## Environment Variables

Each app has its own `.env.example` documenting all supported variables:

- [`backend/.env.example`](backend/.env.example)
- [`frontend/.env.example`](frontend/.env.example)

Never commit real `.env` files — they are excluded via `.gitignore`.

## API Documentation

Once the backend is running:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI schema: `http://localhost:8000/openapi.json`
- Health check: `http://localhost:8000/api/v1/health`
- Readiness check (verifies DB connectivity): `http://localhost:8000/api/v1/health/readiness`

## Testing

### Backend

```bash
cd backend
pytest -v
```

### Frontend

```bash
cd frontend
npm run typecheck
npm run lint
```

## Code Quality

| Tool | Purpose | Command |
|------|---------|---------|
| Black | Python formatting | `black app` |
| isort | Python import sorting | `isort app` |
| Flake8 | Python linting | `flake8 app` |
| mypy | Python type checking | `mypy app` |
| ESLint | TS/React linting | `npm run lint` |
| Prettier | TS/React formatting | `npm run format` |
| TypeScript | Type checking | `npm run typecheck` |

CI runs lint, type-check, and tests for both apps on every push/PR — see
[`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Next Implementation Steps

This foundation is intentionally feature-free. Recommended build order for
subsequent stages:

1. **Authentication** — JWT login/refresh, password hashing, role-based
   access control (`app/auth`, `app/models/user.py`, first Alembic migration).
2. **Patient & Report domain models** — core SQLAlchemy models, repositories,
   and CRUD services for patients and uploaded medical reports.
3. **OCR pipeline** — PaddleOCR/Tesseract ingestion service (`app/ocr`) to
   digitize uploaded medical reports.
4. **RAG knowledge base** — Sentence Transformers embeddings + FAISS index
   (`app/rag`) over medical guidelines/oncology literature.
5. **Risk-assessment ML models** — Scikit-learn/XGBoost models with SHAP
   explainability (`app/ml`), exposed via a dedicated API endpoint.
6. **Multi-agent orchestration** — LangGraph agents (`app/agents`) for
   report Q&A, personalized guidance, and rehabilitation planning, composed
   on top of the RAG and ML layers.
7. **Frontend dashboards** — patient dashboard, report viewer, risk
   visualizations (Recharts), and chat-style agent interface.
8. **Observability & deployment hardening** — structured JSON logging in
   production, metrics, and CI/CD deployment pipeline.

---

Licensed under the [MIT License](LICENSE).
