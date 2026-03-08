# Labour  Backend 🔨

> **Worker-first job platform for informal laborers in India.**  
> Workers set their own rates. Employers post jobs. No middleman.

---

## What is Nakka?

Nakka connects informal laborers — electricians, plumbers, carpenters, drivers, cooks and more — directly with employers in their city. Unlike traditional platforms, **workers control their own pricing**. Employers post what they need, workers apply with their rates, and employers choose who to hire.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (Python 3.11) |
| Database | PostgreSQL (async via SQLAlchemy + asyncpg) |
| Cache / OTP | Redis |
| Auth | Phone OTP + JWT (access + refresh tokens) |
| Push Notifications | Firebase Cloud Messaging (FCM) |
| File Storage | Local disk → AWS S3 (production) |
| Migrations | Alembic |
| Containerization | Docker + Docker Compose |

---

## Architecture

```
HTTP Request
    ↓
Middleware (LoggingMiddleware → AuthMiddleware)
    ↓
API Layer  →  routes only, no business logic
    ↓
Service Layer  →  all business logic lives here
    ↓
Repository Layer  →  all DB queries live here
    ↓
Models (SQLAlchemy)  →  PostgreSQL
```

---

## Project Structure

```
nakka-backend/
├── app/
│   ├── api/v1/               # Route handlers
│   │   ├── auth.py           # OTP login, token refresh
│   │   ├── users.py          # Account management
│   │   ├── workers.py        # Worker profiles, search
│   │   ├── employers.py      # Employer profiles
│   │   ├── jobs.py           # Post jobs, apply, hire, complete
│   │   ├── ratings.py        # Rate workers and employers
│   │   ├── notifications.py  # In-app notifications
│   │   └── chat.py           # WebSocket chat (coming soon)
│   ├── services/             # Business logic
│   ├── repositories/         # DB queries
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── core/                 # Config, DB, Redis, Security, Logging
│   ├── middleware/           # Logging + Auth middleware
│   └── utils/                # Constants, exceptions, helpers
├── migrations/               # Alembic migrations
├── docker/                   # Dockerfile + docker-compose
├── tests/                    # Unit + integration tests
├── .env.example              # Environment variable template
└── requirements.txt
```

---

## API Overview

```
POST   /api/v1/auth/send-otp              Request OTP
POST   /api/v1/auth/verify-otp            Verify OTP → get tokens
POST   /api/v1/auth/refresh-token         Refresh access token
GET    /api/v1/auth/me                    Current user info

GET    /api/v1/users/me                   Get account
DELETE /api/v1/users/me                   Deactivate account
PATCH  /api/v1/users/me/fcm-token         Update push notification token

POST   /api/v1/workers/                   Create worker profile
GET    /api/v1/workers/me                 Get my profile
GET    /api/v1/workers/{id}               View any worker
PUT    /api/v1/workers/me                 Update profile
PATCH  /api/v1/workers/me/availability    Toggle available/busy/on_leave
GET    /api/v1/workers/search/skill       Search workers by skill
GET    /api/v1/workers/search/nearby      Nearby workers by skill + city

POST   /api/v1/employers/                 Create employer profile
GET    /api/v1/employers/me               Get my profile
GET    /api/v1/employers/{id}             View any employer (with ratings)
PUT    /api/v1/employers/me               Update profile

POST   /api/v1/jobs/                      Post a job
GET    /api/v1/jobs/{id}                  Get job details
GET    /api/v1/jobs/search/nearby         Nearby open jobs by skill + city
POST   /api/v1/jobs/{id}/apply            Worker applies to job
POST   /api/v1/jobs/{id}/hire/{app_id}    Employer hires a worker
POST   /api/v1/jobs/{id}/complete         Mark job as completed

POST   /api/v1/ratings/                   Submit rating (worker ↔ employer)
GET    /api/v1/ratings/worker/{id}        Worker rating summary
GET    /api/v1/ratings/employer/{id}      Employer rating summary

GET    /api/v1/notifications/             Get all notifications
GET    /api/v1/notifications/unread-count Unread badge count
PATCH  /api/v1/notifications/read         Mark selected as read
PATCH  /api/v1/notifications/read-all     Mark all as read
```

---

## Quick Start (Local with Supabase)

### 1. Clone and set up environment

```bash
git clone https://github.com/yourname/nakka-backend.git
cd nakka-backend

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up Supabase (free hosted PostgreSQL)

1. Create account at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to **Settings → Database → Connection string → URI**
4. Copy the connection URL

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres.xxxxx:PASSWORD@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key-min-32-chars
APP_NAME=Nakka
DEBUG=True
SMS_PROVIDER=MOCK
```

### 4. Start Redis locally

```bash
# Mac
brew install redis && brew services start redis

# Ubuntu
sudo apt install redis-server && sudo service redis start
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for Swagger UI.

---

## Quick Start (Full Docker)

```bash
# Copy env file
cp .env.example .env

# Start everything (PostgreSQL + Redis + App + Migrations)
docker-compose -f docker/docker-compose.yml up --build
```

---

## Auth Flow

```
1. POST /auth/send-otp   { phone: "+919876543210", role: "worker" }
        ↓
   OTP generated → stored in Redis (10 min expiry) → sent via SMS (or logged in dev)

2. POST /auth/verify-otp { phone: "+919876543210", otp: "482910" }
        ↓
   OTP verified → user created/fetched → JWT tokens issued
   Response: { access_token, refresh_token, role, is_new_user }
   
   is_new_user = true  → frontend shows profile setup screen
   is_new_user = false → frontend goes to home screen

3. All subsequent requests:
   Header: Authorization: Bearer <access_token>

4. POST /auth/refresh-token { refresh_token: "..." }
        ↓
   New access_token + refresh_token issued
```

---

## Job Flow

```
Employer posts job (POST /jobs/)
        ↓
Workers see it in nearby feed (GET /jobs/search/nearby)
        ↓
Worker applies (POST /jobs/{id}/apply)
        ↓
Employer sees applications, hires one (POST /jobs/{id}/hire/{app_id})
        ↓
Chat room opens automatically between worker and employer
        ↓
Job done → Employer marks complete (POST /jobs/{id}/complete)
        ↓
Both get notified to rate each other
        ↓
Worker gets trusted badge if: total_jobs ≥ 10 AND avg_rating ≥ 4.0
```

---

## Notification Flow

Every event triggers **two things simultaneously**:
1. Saved to DB → visible in notification list
2. Firebase push → phone notification (if user has FCM token)

| Event | Who Gets Notified |
|---|---|
| Worker applies to job | Employer |
| Worker is hired | Worker |
| Worker is rejected | Worker |
| Job completed | Both worker and employer |
| New rating received | Rated person |
| New chat message | Receiver (if offline) |

---

## Database Schema

```
users
├── workers          (one-to-one)
│   └── job_applications
│       └── chat_rooms
│           └── chat_messages
└── employers
    └── jobs
        ├── job_applications
        └── ratings
notifications        (belongs to users)
ratings              (worker_id OR employer_id — one always null)
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | — | PostgreSQL connection URL |
| `REDIS_URL` | ✅ | — | Redis connection URL |
| `SECRET_KEY` | ✅ | — | JWT signing key (min 32 chars) |
| `APP_NAME` | ❌ | Nakka | Application name |
| `DEBUG` | ❌ | False | Enable Swagger UI + debug mode |
| `SMS_PROVIDER` | ❌ | MOCK | MOCK \| MSG91 \| FAST2SMS |
| `OTP_LENGTH` | ❌ | 6 | OTP digit length |
| `OTP_EXPIRE_MINUTES` | ❌ | 10 | OTP expiry time |
| `OTP_MAX_ATTEMPTS` | ❌ | 3 | Max wrong OTP attempts |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | 60 | JWT access token expiry |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ❌ | 30 | JWT refresh token expiry |
| `TRUSTED_WORKER_MIN_JOBS` | ❌ | 10 | Jobs needed for trusted badge |
| `TRUSTED_WORKER_MIN_RATING` | ❌ | 4.0 | Rating needed for trusted badge |
| `FIREBASE_PROJECT_ID` | ❌ | — | Firebase project ID for push |
| `FIREBASE_CREDENTIALS_PATH` | ❌ | — | Path to firebase-credentials.json |

---

## Migrations

```bash
# Generate migration after model changes
alembic revision --autogenerate -m "describe your change"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Roll back everything
alembic downgrade base

# Check current state
alembic current

# View history
alembic history
```

---

## Skills Supported

```
electrician  plumber     carpenter   painter
mason        welder      driver      cook
cleaner      helper      gardener    security
```

---

## Roadmap

- [x] Phone OTP authentication
- [x] Worker + Employer profiles
- [x] Job posting and applications
- [x] Two-way rating system
- [x] Trusted worker badge
- [x] In-app notifications
- [x] Firebase push notifications
- [ ] WebSocket chat
- [ ] File upload (profile photos, work photos)
- [ ] SMS OTP (MSG91 / Fast2SMS)
- [ ] Geolocation-based search
- [ ] Admin panel
- [ ] AWS S3 file storage

---

## License

MIT
