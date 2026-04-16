# VigorousONE AI PMO API (MVP)

## Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/token`

## Project & Workstream
- `POST /api/v1/projects`
- `GET /api/v1/projects`

## Task Workflow
- `POST /api/v1/tasks`
- `PATCH /api/v1/tasks/{task_id}`

## AI Ingestion
- `POST /api/v1/inputs/upload` (meeting/document/email text input for MVP)

## Monitoring & Escalation
- `POST /api/v1/monitoring/run`

## Dashboards
- `GET /api/v1/dashboards/control-tower`

## Security model
MVP uses header-based identity (`x-user-email`) for local development. Replace with OAuth2/JWT middleware for production.
