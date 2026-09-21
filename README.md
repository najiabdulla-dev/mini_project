# Skill Swap

A mobile marketplace app connecting people who offer skills with clients who want to hire them. Built with **Flutter** (frontend) and **Django REST Framework** (backend).

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Flutter (MVVM, repository pattern) |
| **Backend** | Django 5.1 + Django REST Framework |
| **Database** | PostgreSQL 16 |
| **Auth** | JWT (SimpleJWT) with email OTP verification |
| **Image Storage** | Cloudinary (with local fallback) |
| **Cache/Rate Limiting** | Redis 7 |
| **API Docs** | Swagger/ReDoc via drf-spectacular |
| **Deployment** | Docker, Nginx, Gunicorn |

## Quick Start (Development)

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Redis 7+ (optional for dev — uses in-memory cache)

### Backend Setup

```bash
# 1. Clone and enter the project
cd skill-swap

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Configure environment
cp ../.env.example ../.env
# Edit .env with your database credentials

# 5. Run migrations
python manage.py migrate

# 6. Create superuser (admin)
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver
```

### API Endpoints

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Django Admin**: http://localhost:8000/admin/

### Docker Setup (Full Stack)

```bash
# From project root
docker-compose up --build
```

Services will be available at:
- **API**: http://localhost/api/
- **Swagger**: http://localhost/api/docs/
- **Admin**: http://localhost/admin/

## Project Structure

```
skill-swap/
├── backend/
│   ├── apps/
│   │   ├── authentication/   # User model, JWT auth, OTP
│   │   ├── skills/            # Categories & Skills
│   │   ├── profiles/          # UserSkill, Experience, Education, etc.
│   │   ├── hiring/            # Hire requests
│   │   ├── messaging/         # 1:1 messages
│   │   ├── notifications/     # In-app notifications
│   │   ├── reviews/           # Ratings & reviews
│   │   ├── bookmarks/         # Saved profiles
│   │   ├── reports/           # User/content reports
│   │   └── admin_panel/       # Platform settings
│   ├── config/                # Django settings & URL config
│   └── utils/                 # Shared utilities
├── frontend/                  # Flutter app (Phase 5)
├── nginx/                     # Nginx config
├── docker-compose.yml
└── .env.example
```

## Auth Flow

1. **Register** → `POST /api/auth/register/` (sends OTP to email)
2. **Verify Email** → `POST /api/auth/verify-otp/`
3. **Login** → `POST /api/auth/login/` (returns JWT tokens + user data)
4. **Access APIs** → Include `Authorization: Bearer <access_token>` header
5. **Refresh Token** → `POST /api/auth/refresh/`
6. **Logout** → `POST /api/auth/logout/` (blacklists refresh token)

## Running Tests

```bash
cd backend
python manage.py test apps.authentication -v2
```

## License

MIT
