# MarkFlow Backend

Backend API for **MarkFlow**, a two-in-one productivity application combining date-based Kanban task management with polygon image annotation.

## Current foundation

This branch establishes the Django and Django REST Framework foundation, environment-based configuration, SQLite development database, CORS support, static-file handling, and a public health endpoint.

## Stack

- Python 3.11+
- Django 5.2 LTS
- Django REST Framework
- Django ORM
- SQLite for local development and the assignment demo

## Local setup

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The local defaults work without extra environment variables. `.env.example` documents the variables that should be configured in a hosted environment.

Apply Django's built-in migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/api/health/`. The response should be:

```json
{"status": "ok", "service": "markflow-backend"}
```

## Development workflow

The project is developed through focused branches and pull requests. Authentication, task APIs, image uploads, polygon annotations, tests, and deployment documentation are added separately.

## License

Licensed under the MIT License.
