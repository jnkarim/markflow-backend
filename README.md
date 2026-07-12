# MarkFlow Backend

Backend API for **MarkFlow**, a two-in-one productivity application combining date-based Kanban task management with polygon image annotation.

## Current capabilities

- Django and Django REST Framework foundation
- Custom email-based user model
- JWT access and refresh tokens
- Authenticated current-user endpoint
- Date-based task creation, reading, editing, and deletion
- User-owned tags attached through simple tag names
- Task filtering by selected date
- Priority, status, due-date, and board-position fields
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
| `GET` | `/api/tasks/?date=YYYY-MM-DD` | List the authenticated user's tasks for a date |
| `POST` | `/api/tasks/` | Create a task |
| `GET` | `/api/tasks/{id}/` | Read one owned task |
| `PATCH` | `/api/tasks/{id}/` | Edit one owned task |
| `DELETE` | `/api/tasks/{id}/` | Delete one owned task |

Example task request:

```json
{
  "title": "Design annotation toolbar",
  "description": "Prepare the first toolbar iteration.",
  "status": "todo",
  "priority": "high",
  "task_date": "2026-07-12",
  "due_date": "2026-07-13",
  "tag_names": ["Design", "Frontend"]
}
```

Task ordering is stored through the `position` field. The dedicated drag-and-drop reorder operation is added in the next focused branch.

## Tests

Run the authentication and task tests:

```bash
python manage.py test apps.accounts apps.tasks
```

## Development workflow

The project is developed through focused branches and pull requests. Task reordering, image uploads, polygon annotations, broader tests, and deployment documentation are added separately.

## License

Licensed under the MIT License.
