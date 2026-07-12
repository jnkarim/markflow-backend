# MarkFlow Backend

Django REST API for **MarkFlow** — a two-in-one productivity application that combines date-based Kanban task management with polygon image annotation.

> **Tagline:** Plan the work. Mark the details.

## Repository links

Add these after deployment:

- Frontend repository: `https://github.com/<username>/markflow-frontend`
- Backend repository: `https://github.com/<username>/markflow-backend`
- Hosted frontend: `https://<project>.vercel.app`
- Hosted backend: `https://<username>.pythonanywhere.com`

## Features

### Authentication

- Custom Django user model with email as the login identifier
- JWT access and refresh tokens
- Authenticated current-user endpoint
- Refresh-token blacklisting on logout
- Seed command for the recruiter demo account

### Date-based Kanban tasks

- `To Do`, `In Progress`, and `Done` states
- Separate task date and due date
- Priority, description, tags, and column position
- Date-filtered task listing
- User-owned task and tag data
- Transaction-safe same-column and cross-column reordering

### Image annotation

- Multiple JPG, PNG, and WEBP uploads
- Image metadata stored through Django ORM
- User-isolated image listing and deletion
- Polygon creation, listing, editing, and deletion
- Normalized coordinates that survive responsive canvas resizing
- Validation for image size, format, point count, coordinates, label, and color

## Technology and runtime versions

| Area | Technology |
|---|---|
| Backend runtime | Python 3.11 |
| Framework | Django 5.2 LTS |
| API toolkit | Django REST Framework 3.17 |
| Authentication | Simple JWT 5.5 |
| Image processing | Pillow 11.3 |
| Database | SQLite through Django ORM |
| Static files | WhiteNoise |
| CI | GitHub Actions |
| Companion frontend runtime | Node.js 20 LTS or newer |

The backend itself does not require Node.js. Node is listed because the assignment also contains a Next.js frontend in a separate repository.

## Project structure

```text
markflow-backend/
├── apps/
│   ├── accounts/       # Email user model, JWT profile/logout, demo user
│   ├── tasks/          # Tasks, tags, date filtering, board reordering
│   └── annotations/    # Image uploads and polygon annotations
├── config/             # Django settings, URL routing, WSGI and ASGI
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── CHALLENGES.md
│   └── DEPLOYMENT.md
├── .github/workflows/  # Automated backend checks
├── .env.example
├── manage.py
└── requirements.txt
```

## Local setup

### 1. Clone and enter the repository

```bash
git clone https://github.com/<username>/markflow-backend.git
cd markflow-backend
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set environment variables

MarkFlow reads **process environment variables**. `.env.example` is a template; Django does not load it automatically.

Windows PowerShell:

```powershell
$env:DJANGO_SECRET_KEY = "replace-with-a-long-random-development-secret"
$env:DJANGO_DEBUG = "True"
$env:DJANGO_ALLOWED_HOSTS = "127.0.0.1,localhost"
$env:CORS_ALLOWED_ORIGINS = "http://localhost:3000"
$env:CSRF_TRUSTED_ORIGINS = "http://localhost:3000"
```

macOS or Linux:

```bash
export DJANGO_SECRET_KEY="replace-with-a-long-random-development-secret"
export DJANGO_DEBUG=True
export DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost"
export CORS_ALLOWED_ORIGINS="http://localhost:3000"
export CSRF_TRUSTED_ORIGINS="http://localhost:3000"
```

Generate a random key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### 5. Prepare the database and demo account

```bash
python manage.py migrate
python manage.py seed_demo
```

Demo credentials:

```text
Email: demo@markflow.app
Password: MarkFlow123!
```

The credentials are intended only for the public assignment demo. Use different credentials for any real application.

### 6. Run the API

```bash
python manage.py runserver
```

Check:

```text
http://127.0.0.1:8000/api/health/
```

Expected response:

```json
{
  "status": "ok",
  "service": "markflow-backend"
}
```

## Environment variables

| Variable | Development example | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | long random value | Django and JWT signing secret |
| `DJANGO_DEBUG` | `True` | Enables development diagnostics |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | Comma-separated API hosts |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000` | Exact comma-separated frontend origins |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:3000` | Trusted browser origins |

Do not add a trailing slash to an origin. Never commit a real secret or a local `.env` file.

## API overview

All private endpoints require:

```text
Authorization: Bearer <access-token>
```

| Area | Main endpoints |
|---|---|
| Health | `GET /api/health/` |
| Authentication | `/api/auth/token/`, `/api/auth/token/refresh/`, `/api/auth/me/`, `/api/auth/logout/` |
| Tasks | `/api/tasks/`, `/api/tasks/{id}/`, `/api/tasks/reorder/` |
| Images | `/api/images/`, `/api/images/upload/`, `/api/images/{id}/` |
| Polygons | `/api/images/{image_id}/polygons/`, `/api/polygons/{id}/` |

See [docs/API.md](docs/API.md) for request and response examples.

## Tests and quality checks

Run the same checks used by CI:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test apps.accounts apps.tasks apps.annotations
```

The current suite contains **49 tests** covering authentication, access control, task validation and reordering, image upload limits and cleanup, polygon validation, and user isolation.

GitHub Actions runs these checks on every pull request and every push to `main`.

## Deployment

The assignment can be hosted on a free PythonAnywhere web app with SQLite and local media storage. Follow [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the exact WSGI, environment, static, media, migration, and CORS steps.

SQLite and filesystem uploads are appropriate for this small recruiter demo. A larger production system should use a managed relational database and durable object storage.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the request flow, application boundaries, data relationships, ordering transaction, annotation coordinate strategy, and security model.

## Difficulties — the villains faced

The main engineering challenges were:

- introducing an email-first custom user model before application migrations;
- keeping Kanban positions contiguous after drag-and-drop operations;
- separating a task's board date from its deadline;
- preserving polygon alignment across responsive image sizes;
- validating uploaded image contents rather than trusting extensions;
- enforcing ownership at every queryset boundary;
- fitting image persistence into a free-tier deployment.

The decisions and trade-offs are documented in [docs/CHALLENGES.md](docs/CHALLENGES.md).

## License

Released under the [MIT License](LICENSE).
