# MarkFlow Backend

Backend API for **MarkFlow**, a two-in-one productivity application combining date-based Kanban task management with polygon image annotation.

## Current capabilities

- Django and Django REST Framework foundation
- Custom email-based user model
- JWT access and refresh tokens
- Authenticated current-user endpoint
- Refresh-token blacklisting on logout
- Demo-user management command
- SQLite development database
- Public health-check endpoint

## Stack

- Python 3.11+
- Django 5.2 LTS
- Django REST Framework
- Simple JWT
- Django ORM
- SQLite for local development and the assignment demo

## Local setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> This branch introduces a custom user model. If you created `db.sqlite3` on the previous foundation branch, delete that local database before running migrations so Django can create the authentication tables cleanly.

Apply migrations, create the demo user, and run the server:

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Demo credentials:

```text
Email: demo@markflow.app
Password: MarkFlow123!
```

## Authentication endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/auth/token/` | Exchange email and password for JWT tokens |
| `POST` | `/api/auth/token/refresh/` | Refresh an access token |
| `GET` | `/api/auth/me/` | Return the authenticated user |
| `POST` | `/api/auth/logout/` | Blacklist a refresh token |
| `GET` | `/api/health/` | Public hosting health check |

Login request:

```json
{
  "email": "demo@markflow.app",
  "password": "MarkFlow123!"
}
```

Authenticated requests use:

```text
Authorization: Bearer <access-token>
```

Run the authentication tests:

```bash
python manage.py test apps.accounts
```

## Development workflow

The project is developed through focused branches and pull requests. Task APIs, image uploads, polygon annotations, broader tests, and deployment documentation are added separately.

## License

Licensed under the MIT License.
