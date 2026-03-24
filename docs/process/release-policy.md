# Release Policy and Pipeline

**Project:** Matrix -- Competency Matrix Web Application
**Division:** Dynamic Infrastructure Portal Support, Sber
**Last updated:** 2026-03-24

---

## Table of Contents

1. [Branching Strategy](#1-branching-strategy)
2. [Versioning](#2-versioning)
3. [Commit Convention](#3-commit-convention)
4. [Pull Request Process](#4-pull-request-process)
5. [CI/CD Pipeline](#5-cicd-pipeline)
6. [Environments](#6-environments)
7. [Release Process](#7-release-process)
8. [Hotfix Process](#8-hotfix-process)
9. [Database Migrations](#9-database-migrations)
10. [Rollback Strategy](#10-rollback-strategy)

---

## 1. Branching Strategy

The project follows a **Git Flow** branching model.

### Branch Types

| Branch | Purpose | Branches from | Merges into | Deploys to |
|---|---|---|---|---|
| `main` | Production-ready code | -- | -- | Production |
| `develop` | Integration branch | `main` (initial) | -- | Staging |
| `feature/*` | New features | `develop` | `develop` | -- |
| `bugfix/*` | Bug fixes | `develop` | `develop` | -- |
| `hotfix/*` | Critical production fixes | `main` | `main` + `develop` | Production |
| `release/*` | Release preparation | `develop` | `main` + `develop` | Staging |
| `docs/*` | Documentation-only changes | `develop` | `develop` | -- |

### Branch Protection Rules

- **`main`** -- protected. Direct pushes are forbidden. Changes only via approved PRs. Requires passing CI checks.
- **`develop`** -- protected. Direct pushes are forbidden. Changes only via PRs. Requires passing CI checks.

### Branching Flow Diagram

```
main        ──●────────────────────●──────────────●──────────────●──→
              │                    ↑              ↑              ↑
              │              merge + tag    merge + tag    hotfix merge
              │                    │              │              │
release/*     │              ●──●──┘              │              │
              │              ↑                    │              │
              │              │                    │              │
develop     ──●──●──●──●──●──●──●──●──●──●──●──●──●──●──●──●──●──→
              │  ↑  │  ↑     ↑        │  ↑                 ↑
              │  │  │  │     │        │  │                 │
feature/*     ●──┘  │  │     │        ●──┘                 │
                    │  │     │                             │
bugfix/*            ●──┘     │                             │
                             │                             │
hotfix/*                     │                       main──●──→main
                             │                             │
docs/*                       ●─────────────────────────────┘
```

**Reading the diagram:**

- Arrows (`→`) indicate the direction of time.
- `●` marks a commit or branch point.
- `↑` indicates a merge back into the parent branch.
- `feature/*` and `bugfix/*` branches are short-lived and merge back into `develop`.
- `release/*` branches are created from `develop`, finalized, then merged into both `main` and `develop`.
- `hotfix/*` branches are created from `main`, and after the fix is merged into both `main` and `develop`.

---

## 2. Versioning

The project uses **Semantic Versioning 2.0.0** (`MAJOR.MINOR.PATCH`).

| Component | When to increment | Example |
|---|---|---|
| **MAJOR** | Breaking changes to the API, data model, or user-facing contracts | `1.0.0` → `2.0.0` |
| **MINOR** | New features that are backwards compatible | `1.0.0` → `1.1.0` |
| **PATCH** | Bug fixes, minor corrections, no feature changes | `1.1.0` → `1.1.1` |

### Pre-release Versions

During release preparation, pre-release tags may be used:

- `1.2.0-rc.1` -- release candidate 1
- `1.2.0-rc.2` -- release candidate 2

### Version Sources

- Git tags are the single source of truth for versioning.
- Tags follow the format: `v{MAJOR}.{MINOR}.{PATCH}` (e.g., `v1.3.0`).

---

## 3. Commit Convention

All commits must follow the **Conventional Commits** specification (v1.0.0).

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation-only changes |
| `refactor` | Code refactoring (no feature or fix) |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks (dependencies, configs) |
| `ci` | CI/CD pipeline changes |
| `perf` | Performance improvements |

### Scopes

Use scopes to indicate the affected area of the codebase:

- `feat(api):` -- backend API changes
- `fix(ui):` -- frontend/UI bug fix
- `refactor(models):` -- data model refactoring
- `ci(docker):` -- Docker-related CI changes
- `docs(process):` -- process documentation updates

### Examples

```
feat(api): add competency level calculation endpoint
fix(ui): correct alignment of skill matrix table headers
refactor(models): extract base competency class
ci: add staging deployment workflow
chore: update FastAPI to 0.111.0
```

### Breaking Changes

Breaking changes must include `BREAKING CHANGE:` in the commit footer or append `!` after the type/scope:

```
feat(api)!: redesign competency evaluation response schema

BREAKING CHANGE: The response payload for /api/v1/evaluations has changed.
The `score` field is now nested under `result.score`.
```

---

## 4. Pull Request Process

### General Rules

- **All changes** reach `develop` and `main` exclusively through pull requests.
- No direct pushes to protected branches.
- Every PR must pass all CI checks before merging.

### PR Template

Every pull request must include the following sections:

```markdown
## Summary
Brief description of what this PR does and why.

## Type of Change
- [ ] New feature (feat)
- [ ] Bug fix (fix)
- [ ] Refactoring (refactor)
- [ ] Documentation (docs)
- [ ] CI/CD (ci)
- [ ] Other (describe)

## Testing
- Describe how the changes were tested.
- List any new or modified tests.

## Checklist
- [ ] Code follows the project style guidelines
- [ ] Self-review of the code has been performed
- [ ] New and existing tests pass locally
- [ ] Database migrations are included (if applicable)
- [ ] Documentation has been updated (if applicable)
- [ ] No secrets or credentials are included
```

### Review Requirements

| Scenario | Requirement |
|---|---|
| Team of 2+ developers | At least 1 reviewer approval required |
| Solo developer | Self-review with the full checklist completed |

### Merge Strategy

| Branch type | Merge method | Rationale |
|---|---|---|
| `feature/*` → `develop` | **Squash merge** | Clean, single-commit history on develop |
| `bugfix/*` → `develop` | **Squash merge** | Clean, single-commit history on develop |
| `docs/*` → `develop` | **Squash merge** | Clean, single-commit history on develop |
| `release/*` → `main` | **Merge commit** | Preserve release context |
| `hotfix/*` → `main` | **Merge commit** | Preserve hotfix context |
| `main` → `develop` (back-merge) | **Merge commit** | Sync production state |

---

## 5. CI/CD Pipeline

The CI/CD pipeline is implemented with **GitHub Actions**.

### Pipeline Stages

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   Lint   │───→│   Test   │───→│  Build   │───→│  Deploy  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### Trigger Matrix

| Event | Lint | Type Check | Unit Tests | Build | Deploy |
|---|---|---|---|---|---|
| PR opened/updated | Yes | Yes | Yes | Yes | -- |
| Merge to `develop` | Yes | Yes | Yes | Yes | Staging |
| Merge to `main` | Yes | Yes | Yes | Yes | Production |

### Stage Details

#### Lint
- **Tool:** Ruff
- **Checks:** Code style, import ordering, unused imports, common errors
- **Fails fast:** Yes -- subsequent stages are skipped on failure

#### Type Check
- **Tool:** mypy
- **Config:** Strict mode enabled
- **Fails fast:** Yes

#### Unit Tests
- **Tool:** pytest
- **Coverage:** Minimum threshold enforced (configurable, recommended 80%)
- **Reports:** Coverage report uploaded as artifact

#### Build
- **Action:** Build Docker image
- **Tags:** `sha-{commit}`, `latest` (for develop), `v{version}` (for main)
- **Registry:** Container registry (GitHub Container Registry or internal)

#### Deploy
- **Staging:** Triggered automatically on merge to `develop`
- **Production:** Triggered automatically on merge to `main`, also creates a GitHub Release

### Workflow Files

```
.github/
  workflows/
    ci.yml          # Lint + type check + tests (on all PRs)
    build.yml       # Docker image build
    deploy-staging.yml    # Deploy to staging
    deploy-production.yml # Deploy to production + GitHub Release
```

---

## 6. Environments

| Environment | Source | Trigger | URL | Purpose |
|---|---|---|---|---|
| **Development** | Local machine | Manual | `localhost` | Developer workstation |
| **Staging** | `develop` branch | Auto on merge | Cloud URL (staging) | Integration testing, QA |
| **Production** | `main` branch | Auto on merge | Cloud URL (prod) | Live application |

### Development (Local)

- Run via **Docker Compose**: `docker compose up`
- Hot-reload enabled for backend and frontend
- Local database with seed data
- All services run in containers for environment parity

### Staging

- Deployed to cloud infrastructure from the `develop` branch
- Uses a staging database (separate from production)
- Mirrors production configuration as closely as possible
- Used for final QA before releases

### Production

- Deployed to cloud infrastructure from the `main` branch
- Production database with real data
- Monitoring and alerting enabled
- Access restricted and audited

---

## 7. Release Process

### Step-by-step

1. **Create a release branch** from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/1.2.0
   ```

2. **Bump the version** in the project configuration files.

3. **Update the changelog** (`CHANGELOG.md`) with all changes since the last release.

4. **Push the release branch** and deploy to staging for final QA:
   ```bash
   git push origin release/1.2.0
   ```

5. **Perform final QA** on the staging environment.
   - Run the full regression test suite.
   - Verify all acceptance criteria for the release.
   - Fix any issues directly on the release branch.

6. **Create a PR** from `release/1.2.0` to `main`.
   - Ensure all CI checks pass.
   - Get approval (or perform self-review).

7. **Merge to main** using a merge commit.

8. **Tag the release** on `main`:
   ```bash
   git checkout main
   git pull origin main
   git tag -a v1.2.0 -m "Release v1.2.0"
   git push origin v1.2.0
   ```

9. **Create a GitHub Release** from the tag, including:
   - Release title: `v1.2.0`
   - Release notes / changelog excerpt
   - Any relevant migration instructions

10. **Merge `main` back into `develop`** to sync any release-branch fixes:
    ```bash
    git checkout develop
    git pull origin develop
    git merge main
    git push origin develop
    ```

11. **Delete the release branch**:
    ```bash
    git branch -d release/1.2.0
    git push origin --delete release/1.2.0
    ```

---

## 8. Hotfix Process

Hotfixes are for critical production issues that cannot wait for the next scheduled release.

### Step-by-step

1. **Create a hotfix branch** from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/1.2.1
   ```

2. **Apply the fix** and commit using conventional commits:
   ```bash
   git commit -m "fix(api): correct null pointer in evaluation endpoint"
   ```

3. **Push the hotfix branch** and open a PR to `main`:
   ```bash
   git push origin hotfix/1.2.1
   ```

4. **Ensure CI passes**, review the PR, and merge to `main` using a merge commit.

5. **Tag with a patch version** on `main`:
   ```bash
   git checkout main
   git pull origin main
   git tag -a v1.2.1 -m "Hotfix v1.2.1"
   git push origin v1.2.1
   ```

6. **Create a GitHub Release** from the hotfix tag.

7. **Merge `main` back into `develop`**:
   ```bash
   git checkout develop
   git pull origin develop
   git merge main
   git push origin develop
   ```

8. **Delete the hotfix branch**:
   ```bash
   git branch -d hotfix/1.2.1
   git push origin --delete hotfix/1.2.1
   ```

---

## 9. Database Migrations

### Tools

- **Alembic** is used for all database schema migrations.
- Migration scripts live in `alembic/versions/`.

### Rules

1. **Every schema change** must have a corresponding Alembic migration.
2. **Migrations are reviewed as part of the PR** -- never applied without review.
3. **Each migration must include both `upgrade()` and `downgrade()`** functions.
4. **Naming convention:** Alembic auto-generates a revision ID. The migration message must be descriptive:
   ```bash
   alembic revision --autogenerate -m "add competency_level column to employees"
   ```
5. **Testing:** Migrations are tested in CI against a clean database (upgrade from scratch) and against the current schema (incremental upgrade).
6. **Production rollback plan:** Every PR that includes a migration must document the rollback procedure in the PR description. This includes:
   - The Alembic downgrade command
   - Any data considerations (e.g., data loss on column removal)
   - Whether the migration is reversible or destructive

### Migration Deployment Order

1. **Run migrations before deploying new application code** if the new code depends on schema changes.
2. **Deploy new application code before running migrations** if the migration removes columns or tables that old code depends on (blue-green compatible approach).
3. For complex changes, use a **multi-phase migration** strategy:
   - Phase 1: Add new columns/tables (backwards compatible)
   - Phase 2: Deploy new code that uses the new schema
   - Phase 3: Remove old columns/tables (cleanup migration)

---

## 10. Rollback Strategy

### Application Rollback

If a production deployment introduces a critical issue:

1. **Identify the previous stable image tag** (e.g., `v1.1.0` or a specific commit SHA).
2. **Redeploy the previous container image**:
   ```bash
   # Example: revert to previous version
   docker pull registry/matrix-app:v1.1.0
   # Redeploy using orchestration tool
   ```
3. **Verify** the application is functioning correctly on the rolled-back version.
4. **Investigate** the root cause and create a `hotfix/*` or `bugfix/*` branch.

### Database Rollback

If the issue is caused by a database migration:

1. **Run Alembic downgrade** to the previous revision:
   ```bash
   alembic downgrade -1    # Downgrade one revision
   # or
   alembic downgrade <revision_id>  # Downgrade to a specific revision
   ```
2. **Verify** data integrity after the downgrade.
3. **Redeploy** the previous application version if needed.

### Rollback Decision Matrix

| Scenario | Action |
|---|---|
| Application bug, no migration involved | Redeploy previous container image |
| Application bug + reversible migration | Alembic downgrade + redeploy previous image |
| Application bug + irreversible migration | Assess data impact, consider forward-fix via hotfix |
| Performance degradation | Redeploy previous image, investigate |
| Infrastructure issue | Escalate to infrastructure team |

### Rollback SLA

- **Detection:** Monitoring and alerting should detect issues within 5 minutes.
- **Decision:** Rollback decision should be made within 15 minutes of detection.
- **Execution:** Rollback should be completed within 30 minutes of the decision.

---

## Summary of Key Policies

| Policy | Value |
|---|---|
| Branching model | Git Flow |
| Versioning | Semantic Versioning (MAJOR.MINOR.PATCH) |
| Commit format | Conventional Commits |
| Merge strategy (features) | Squash merge |
| Merge strategy (releases/hotfixes) | Merge commit |
| Minimum reviewers | 1 (self-review with checklist for solo dev) |
| CI stages | Lint, Type Check, Test, Build, Deploy |
| Migration tool | Alembic |
| Rollback method | Previous container image + Alembic downgrade |
