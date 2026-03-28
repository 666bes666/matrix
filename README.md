# Matrix — Competency Management Platform

Internal web application for managing employee competency matrices in the Dynamic Infrastructure Portal support division at Sber.

## Features

- **Competency Catalog** — categories, levels 0–4, learning resources
- **360° Assessments** — campaigns with self/peer/TL/dept_head scoring and weighted aggregation
- **Competency Matrix** — color-coded employee × competency grid (red=0 → blue=4)
- **Gap Analysis** — current vs target levels per role profile
- **Career Tracks** — department transition paths with readiness scoring
- **Individual Development Plans** — goals, deadlines, mandatory/desirable split
- **Analytics** — heatmap by department, Excel export, assessment history
- **RBAC** — 6 roles (admin, head, dept_head, team_lead, hr, employee)
- **CSV Import** — bulk users and competencies
- **Notifications** — in-app notification system with unread badge
- **Calibration** — auto-detect score spread ≥ 2, dept_head resolution

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0 async, Alembic, Pydantic v2 |
| Frontend | React 18+, TypeScript, Vite, Mantine UI, TanStack Query, Recharts |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Task Queue | Celery + Redis |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## Quick Start

```bash
# Copy environment variables
cp .env.example .env

# Start all services
docker compose up -d

# Apply migrations
docker compose exec backend uv run alembic upgrade head

# Seed data (add --demo for test users)
docker compose exec backend uv run python seed.py --demo

# Create superuser
docker compose exec backend uv run python -m app.cli create-superuser \
  --email admin@matrix.local --password Admin123

# Open browser
open http://localhost:3000
```

## Development

```bash
# Backend
cd src/backend
uv sync
uv run uvicorn app.main:app --reload

# Frontend
cd src/frontend
pnpm install
pnpm dev

# Tests (from src/backend/)
no_proxy="*" uv run pytest ../../tests/backend/ -q --cov=app --cov-fail-under=80
```

## Architecture

```
src/
  backend/
    app/
      api/          # FastAPI routers (thin: validate → service → return)
      core/         # config, database, redis, security, dependencies
      models/       # SQLAlchemy ORM models
      schemas/      # Pydantic request/response models
      services/     # Business logic (scope-filtered, audit-logged)
      tasks/        # Celery tasks (backups, reminders)
  frontend/
    src/
      api/          # Axios clients per domain
      components/   # Reusable UI (MatrixGrid, RadarChart, RoleBadge, ...)
      hooks/        # useAuth, usePermissions
      pages/        # Route-level page components
      stores/       # Zustand (auth state)
      types/        # TypeScript interfaces
```

## User Roles

| Role | Access |
|------|--------|
| Admin | Full system management |
| Head | All departments (read assessments), catalog management, campaigns |
| Department Head | Own department: assessments, calibration, target profiles |
| Team Lead | Own team: assessments, IDP creation |
| HR | Read-only all data, export reports, CSV import |
| Employee | Own profile, self-assessment, own IDP |

## API

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs`

## License

Internal use only — Sber Dynamic Infrastructure Portal division.
