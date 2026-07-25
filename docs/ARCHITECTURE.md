# Architecture Overview

OncoNexus AI follows **Clean Architecture** principles across both backend
and frontend, keeping business logic independent of frameworks, UI, and
infrastructure details.

## Backend layering (`backend/app/`)

```
api/            -> Presentation layer: FastAPI routers, request/response wiring
  v1/endpoints/ -> Versioned route handlers (thin — delegate to services)
services/       -> Application/business logic layer
repositories/   -> Data-access layer (abstracts SQLAlchemy queries from services)
models/         -> SQLAlchemy ORM models (persistence layer)
schemas/        -> Pydantic request/response contracts (validation layer)
agents/         -> LangGraph/LangChain multi-agent orchestration
ml/             -> Scikit-learn / XGBoost / SHAP risk-assessment models
rag/            -> Retrieval-augmented generation (FAISS + Sentence Transformers)
ocr/            -> PaddleOCR / Tesseract report digitization
auth/           -> JWT authentication & authorization
core/           -> Cross-cutting config, logging, startup wiring
middleware/     -> Request/response middleware (logging, correlation IDs)
exceptions/     -> Exception hierarchy + global handlers
common/         -> Shared constants and response envelopes
utils/          -> Stateless helper functions
```

**Dependency rule:** inner layers (models, schemas) never import from outer
layers (api, services). Routers depend on services; services depend on
repositories; repositories depend on models. This keeps each layer testable
in isolation and swappable (e.g. repositories could move to a different ORM
without touching services or routers).

## Frontend layering (`frontend/src/`)

```
pages/       -> Route-level components (composition only)
layouts/     -> Shared page chrome (header/sidebar/footer)
components/  -> Reusable, presentation-focused UI building blocks
  ui/        -> shadcn/ui primitives
  common/    -> App-specific shared components
hooks/       -> Reusable stateful logic
contexts/    -> React context providers (auth, theme, etc.)
services/    -> API clients and data-fetching functions (axios + TanStack Query)
routes/      -> Route table (react-router-dom)
types/       -> Shared TypeScript contracts (mirrors backend schemas)
utils/       -> Stateless helper functions
```

## Cross-cutting concerns

- **API versioning:** all routes are mounted under `/api/v1`, allowing
  `/api/v2` to be introduced later without breaking existing clients.
- **Global exception handling:** every error — validation, HTTP, or
  unexpected — is normalized into the same `ErrorResponse` JSON contract.
- **Structured logging:** every request is logged with a correlation ID
  (`X-Request-ID`) for traceability across services.
- **Configuration:** all environment-driven values flow through a single
  `Settings` class (`app/core/config`); nothing reads `os.environ` directly.
- **Containerization:** both apps ship multi-stage Dockerfiles (development
  vs. production targets) orchestrated by `docker-compose.yml`.

## Planned modules (not yet implemented)

- `auth/` — JWT login/refresh, role-based access control
- `agents/` — LangGraph multi-agent workflows (triage, report Q&A, guidance)
- `ml/` — risk-assessment models with SHAP explainability
- `rag/` — FAISS-backed retrieval over medical knowledge base
- `ocr/` — medical report digitization pipeline
