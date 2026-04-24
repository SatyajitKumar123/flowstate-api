# FlowState API

Production-grade Task Management & Workflow Automation Backend.  
Built with Django 6.0, PostgreSQL 17, Redis 7, Celery 6, and Django Channels.

![Python 3.13](https://img.shields.io/badge/Python-3.13-blue)
![Django 6.0](https://img.shields.io/badge/Django-6.0-092E20)
![PostgreSQL 17](https://img.shields.io/badge/PostgreSQL-17-336791)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Overview
FlowState is a multi-tenant workflow API that combines project/task management with real-time sync and event-driven integrations. Designed to demonstrate senior backend patterns: explicit tenant isolation, async resilience, secure external integrations, and reproducible DevOps.

## 🏗 Architecture
```
[Client] ──HTTP/WS──▶ [Django 6.0 / ASGI] ──▶ PostgreSQL 17
                         │
                         ▼
                  [Redis 7] ◀── Celery 6 Worker
                         │
                         ▼
               [SMTP / Webhooks / Events]
```

## 🛠 Tech Stack
| Layer | Stack |
|-------|-------|
| **Runtime** | Python 3.13, Django 6.0, DRF 3.15+ |
| **Database** | PostgreSQL 17 (explicit indexes, composite constraints) |
| **Cache/Broker** | Redis 7 (sessions, blacklist, Celery, Channels) |
| **Async** | Celery 6+, `acks_late=True`, exponential backoff |
| **Real-time** | Django Channels 4, `daphne`, JWT-over-WS |
| **DevOps** | Docker Compose, `uv` (Rust-based deps), `pydantic-settings`, Ruff + MyPy |

## ✨ Features
- 🔐 **JWT Auth**: Access/refresh tokens, rotation, Redis blacklist, secure password reset
- 🏢 **Multi-Tenant RBAC**: Workspace → Project → Task hierarchy. `Admin`/`Member`/`Viewer` roles with explicit query scoping
- ⚡ **Async Notifications**: Celery workers send emails on status changes. Non-blocking API responses <50ms
- 🌐 **Real-time Sync**: WebSocket broadcasts on task mutations. Workspace-scoped channel groups
- 📡 **Outgoing Webhooks**: HMAC-SHA256 payload verification, retry queues, event filtering
- 📊 **Audit Trail**: Immutable `TaskHistory` tracking status/assignee/due_date changes
- 🔍 **Query Optimized**: `select_related`, composite indexes, `distinct()` to prevent N+1 & duplicate rows
- 🐳 **Reproducible Env**: Multi-stage Docker, `uv.lock`, split-settings, healthchecks

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- `uv` (optional, for host-side lockfile management)

### Run
```bash
git clone https://github.com/SatyajitKumar123/flowstate-api.git
cd flowstate-api
cp .env.example .env
docker compose up -d --build
```

### Verify
```bash
# Health check
curl http://localhost:8000/api/health/

# Create superuser
docker compose exec web uv run python manage.py createsuperuser

# Apply migrations (auto-runs on first boot)
docker compose exec web uv run python manage.py migrate
```

## 🔐 Environment Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `DJANGO_SETTINGS_MODULE` | `config.settings` | Django config entrypoint |
| `DATABASE_URL` | `postgres://dev:devpassword@db:5432/flowstate` | PostgreSQL connection |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Celery message broker |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/1` | Celery task results |
| `CHANNEL_REDIS_URL` | `redis://redis:6379/2` | WebSocket channel layer |
| `SECRET_KEY` | (required) | Django cryptographic signing |
| `DEBUG` | `True` | Dev mode toggle |

## 📡 API Reference
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/register/` | `POST` | ❌ | Create user |
| `/api/auth/login/` | `POST` | ❌ | Get JWT tokens |
| `/api/v1/workspaces/` | `GET/POST` | ✅ | Tenant CRUD (role-scoped) |
| `/api/v1/projects/` | `GET/POST` | ✅ | Workspace projects |
| `/api/v1/tasks/` | `GET/POST/PATCH` | ✅ | Task CRUD + audit |
| `/api/v1/tasks/{id}/history/` | `GET` | ✅ | Immutable change log |
| `/api/v1/webhooks/` | `GET/POST` | ✅ | Outgoing webhook management |
| `ws://localhost:8000/ws/tasks/?token=<jwt>` | WS | ✅ | Real-time task updates |

## 🧪 Testing & Validation
```bash
# Lint & Type
docker compose exec web uv run ruff check .
docker compose exec web uv run mypy . --ignore-missing-imports

# Run system checks
docker compose exec web uv run python manage.py check

# Postman workflow:
# 1. POST /api/auth/login/ → save access token
# 2. POST /api/v1/workspaces/ → get workspace UUID
# 3. POST /api/v1/tasks/ → create task
# 4. PATCH /api/v1/tasks/{id}/ → trigger async + WS broadcast
# 5. GET /api/v1/tasks/{id}/history/ → verify audit trail
```

## 📐 Key Design Decisions
| Decision | Rationale |
|----------|-----------|
| Explicit tenant filtering in views | Prevents accidental cross-tenant leaks in workers, admin, and shell |
| `select_related` at query layer | Keeps P95 latency flat as tables scale; avoids ORM N+1 traps |
| `acks_late=True` + retry backoff | Guarantees delivery during worker crashes without duplicate spam |
| HMAC-SHA256 for webhooks | Industry standard for payload authenticity & replay protection |
| `?token=` for WS handshake | Browsers block custom WS headers; secure over WSS in prod |
