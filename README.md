# MarkFlow Backend

Backend API for **MarkFlow**, a two-in-one productivity application combining date-based Kanban task management with image annotation.

## Current capabilities

- Django and Django REST Framework foundation
- Custom email-based user model
- JWT access and refresh tokens
- Date-based task CRUD with user-owned tags
- Transaction-safe task reordering within and between Kanban columns
- Authenticated multiple-image uploads
- JPG, PNG, and WEBP validation
- User-isolated image listing, retrieval, and deletion
- Image metadata persistence through Django ORM
- SQLite development database
- Public health-check endpoint

Polygon drawing data is intentionally added in the next focused branch.

## Stack

- Python 3.11+
- Django 5.2 LTS
- Django REST Framework
- Simple JWT
- Pillow
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

Apply migrations, create the demo user, and start the server:

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

Authenticated requests use:

```text
Authorization: Bearer <access-token>
```

## Task endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/tasks/?date=YYYY-MM-DD` | List tasks for a selected date |
| `POST` | `/api/tasks/` | Create a task |
| `GET` | `/api/tasks/{id}/` | Read one owned task |
| `PATCH` | `/api/tasks/{id}/` | Edit one owned task |
| `DELETE` | `/api/tasks/{id}/` | Delete one owned task |
| `POST` | `/api/tasks/reorder/` | Move a task within or between columns |

## Image endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/images/` | List the authenticated user's images |
| `POST` | `/api/images/upload/` | Upload one or more images using `files` |
| `GET` | `/api/images/{id}/` | Read one owned image |
| `DELETE` | `/api/images/{id}/` | Delete one owned image and its stored file |

Upload rules for the free-tier demo:

- Accepted formats: JPG, PNG, and WEBP
- Maximum file size: 5 MB per image
- Maximum stored images: 20 per account
- Files are verified with Pillow before persistence
- Stored names are randomized while original names remain in the database

Example PowerShell upload request after obtaining an access token:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/images/upload/" `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" `
  -F "files=@C:\path\first.png" `
  -F "files=@C:\path\second.jpg"
```

## Tests

Run the current backend suite:

```bash
python manage.py test apps.accounts apps.tasks apps.annotations
```

The current suite covers authentication, task CRUD and reordering, image validation, multiple uploads, user isolation, and protected deletion.

## Development workflow

The project is developed through focused branches and pull requests. Polygon annotation persistence, broader tests, and deployment documentation are added separately.

## License

Licensed under the MIT License.
