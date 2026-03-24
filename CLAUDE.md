# Matrix — Competency Matrix Platform

## Project Overview

Matrix is an internal web application for managing employee competency matrices.
It is built for the Dynamic Infrastructure Portal support division at Sber (private cloud for internal Sber users).

The division has 5 departments with ~10-50 employees total. The product tracks competencies,
enables 360° assessments, visualizes skill gaps, and supports career path planning across departments.

## Repository Structure

```
docs/
  business/           # Business documents (RU)
    product-vision.md
    market-requirements.md
    business-requirements.md
    business-plan.md
  product/            # Product documents (RU)
    roadmap.md
    product-requirements.md
    product-backlog.md
  technical/          # Technical documents (EN)
    technical-specification.md
    risk-register.md
  process/            # Process documents (EN)
    release-policy.md
src/                  # Application source code (when development begins)
tests/                # Test suite
```

## Tech Stack (planned)

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy, Alembic
- **Frontend**: React + TypeScript, Vite
- **Database**: PostgreSQL
- **Cache**: Redis
- **Notifications**: Telegram Bot API
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Package management**: uv (Python), pnpm (JS)

## Branching Strategy

See `docs/process/release-policy.md` for full details.

- `main` — production-ready, protected
- `develop` — integration branch
- `feature/*` — new features
- `bugfix/*` — bug fixes
- `hotfix/*` — production hotfixes
- `docs/*` — documentation changes
- `release/*` — release preparation

## Development Commands

```bash
# Backend
cd src/backend
uv sync
uv run uvicorn app.main:app --reload

# Frontend
cd src/frontend
pnpm install
pnpm dev

# Tests
uv run pytest tests/ -q

# Docker
docker compose up -d
```

## Code Conventions

- Python: no comments in source files, no docstrings required
- Follow PEP 8, use ruff for linting
- TypeScript: strict mode, ESLint + Prettier
- All PRs require at least one review
- Commits follow Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Key Domain Concepts

### Departments (5)
1. **First Line Support** (Первая линия) — basic portal support, quotas, known bugs
2. **Duty Shift** (Дежурная смена) — deeper troubleshooting, Ansible, vCloud Director, networking, incidents
3. **Business Logic** (Бизнес-логика) — portal business logic verification, resource provisioning
4. **Second Line Support** (Вторая линия) — SRE/DevOps, logs, metrics, code changes, DB operations
5. **Jenkins CDP Support** (Сопровождение Jenkins CDP) — Jenkins automation

### Competency Categories
- **Hard Skills** — technical skills (Linux, networking, K8s, cloud, scripting, etc.)
- **Soft Skills** — communication, teamwork, leadership
- **Processes** — ITIL, incident management, change management
- **Domain Knowledge** — portal product knowledge, internal systems, business processes

### Proficiency Levels (5)
0. None (Нет знаний)
1. Novice (Новичок)
2. Basic (Базовый)
3. Advanced (Продвинутый)
4. Expert (Эксперт)

### User Roles
- **Admin** — full system management
- **Department Head** (Руководитель управления) — sees all departments
- **Team Lead** — manages their specific team within a department
- **HR** — access to reports and analytics
- **Employee** (Сотрудник) — views own profile, self-assessment

### Assessment Process
- 360° assessment: self + peers + team lead + department head
- Frequency: twice per year
- Full history tracking with growth dynamics

### Key Features (MVP)
- Competency catalog with learning resources
- Employee profiles with department/role assignment
- Target competency profiles for roles (gap analysis)
- Individual development plans (IDP)
- 360° assessment workflow
- Radar charts + heatmaps + Excel/PDF export
- Career path visualization (cross-department transitions)
- CSV/Excel import for employees and competencies
- Telegram notifications
- Assessment history and growth tracking
