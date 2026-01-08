# Project Structure

이 프로젝트는 백엔드와 프론트엔드가 명확히 분리된 구조입니다.

## Directory Structure

```
OnlineJudge/
├── backend/              # Django Backend
│   ├── account/         # User authentication & management
│   ├── announcement/    # Announcements
│   ├── conf/            # Configuration
│   ├── contest/         # Contest management
│   ├── judge/           # Judge server integration
│   ├── oj/              # Django project settings
│   ├── options/         # System options
│   ├── problem/         # Problem management
│   ├── submission/      # Code submissions
│   ├── utils/           # Utility functions
│   ├── data/            # Runtime data (logs, uploads, etc.)
│   ├── deploy/          # Deployment configurations
│   ├── manage.py        # Django management script
│   ├── Dockerfile       # Backend Docker image
│   └── ...
│
├── frontend/            # Vue.js Frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── admin/  # Admin panel
│   │   │   └── oj/     # User-facing pages
│   │   └── ...
│   ├── build/           # Build configurations
│   ├── config/          # Frontend configs
│   ├── Dockerfile.dev   # Frontend dev Docker image
│   └── ...
│
├── docker-compose.dev.yml  # Development environment
├── .gitignore
└── README.md

```

## Running the Project

### Development Mode

```bash
# Start all services
docker compose -f docker-compose.dev.yml up -d

# View logs
docker logs oj-backend-dev
docker logs oj-frontend-dev

# Stop all services
docker compose -f docker-compose.dev.yml down
```

### Access Points

- **Frontend (User)**: http://localhost:8080
- **Frontend (Admin)**: http://localhost:8080/admin
- **Backend API**: http://localhost:8000/api
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Default Admin Credentials

- Username: `root`
- Password: `rootroot`

## Security Features

### User Approval System

New users must be approved by an admin before accessing problems:

1. User registers at `/register`
2. Admin logs into `/admin`
3. Admin navigates to **User** management
4. Admin toggles **Is Approved** switch for the user
5. User can now access problems and submit solutions

### API Protection

- All problem/contest/submission APIs require login
- Unapproved users cannot access protected resources
- Admin users bypass approval checks

## Development

### Backend (Django)

```bash
# Enter backend directory
cd backend

# Run migrations
docker exec oj-backend-dev python manage.py migrate

# Create superuser
docker exec -it oj-backend-dev python manage.py createsuperuser

# Django shell
docker exec -it oj-backend-dev python manage.py shell
```

### Frontend (Vue.js)

```bash
# Frontend has hot-reload enabled
# Edit files in frontend/src/ and changes will auto-reload
```

## Modified Files for Security

### Backend
- `backend/account/models.py` - Added `is_approved` field
- `backend/account/views/oj.py` - Login/register approval checks
- `backend/account/views/admin.py` - Admin user creation
- `backend/account/serializers.py` - Added approval to serializers
- `backend/problem/views/oj.py` - Problem access control
- `backend/submission/views/oj.py` - Submission access control
- `backend/contest/views/oj.py` - Contest access control

### Frontend
- `frontend/src/pages/admin/views/general/User.vue` - Added approval UI

### Database
- Migration: `backend/account/migrations/0013_user_is_approved.py`
- Data migration: `backend/account/migrations/0014_approve_existing_admins.py`
