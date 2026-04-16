# VigorousONE AI PMO – Project Intelligence & Task Orchestration Platform

Production-oriented MVP implementing a multi-tenant, AI-enabled PMO control tower.

## Delivered in this implementation
- Multi-tenant domain model (organizations, projects, workstreams, source inputs, tasks, audit logs, notifications).
- Configurable role model with six PMO-oriented roles and permission map.
- AI ingestion pipeline (meeting/document/email text input in MVP) with extraction prompt template and structured outputs.
- AI-generated Minutes of Meeting persisted as AI outputs.
- Task orchestration APIs with status lifecycle, dependencies, assignment/reassignment, and audit logging.
- Monitoring/escalation engine for overdue tasks with auto-generated reminder notifications.
- Control tower dashboard API with KPI and risk rollups.
- React control-tower frontend with KPI cards, owner chart, and one-click AI extraction workflow.
- Dockerized backend/frontend/PostgreSQL stack.

## Architecture
- **Frontend:** React + Vite (`frontend/`)
- **Backend:** FastAPI + SQLAlchemy (`backend/`)
- **Database:** PostgreSQL in docker-compose (SQLite fallback for local quickstart)
- **AI services:** prompt-based extraction engine with mock mode + production integration seam

## Local run (backend)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Local run (frontend)
```bash
cd frontend
npm install
npm run dev
```

## Tests
```bash
cd backend
pytest
```

## Next production steps
1. Replace header auth with full JWT/OIDC and fine-grained policy engine.
2. Add binary upload + Whisper STT + OCR parser workers.
3. Add pgvector indexing + retrieval endpoints for Ask AI.
4. Add async job queue (Celery/RQ) and outbound email provider integration.
5. Add Alembic migrations and comprehensive integration test matrix.
