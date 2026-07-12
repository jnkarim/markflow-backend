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
- Normalized polygon annotation creation, listing, editing, and deletion
- User-isolated annotation access through parent image ownership
- SQLite development database
- Public health-check endpoint


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

## Polygon annotation endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/images/{image_id}/polygons/` | List polygons saved on one owned image |
| `POST` | `/api/images/{image_id}/polygons/` | Save a polygon on one owned image |
| `GET` | `/api/polygons/{id}/` | Retrieve one owned polygon |
| `PATCH` | `/api/polygons/{id}/` | Update one owned polygon |
| `DELETE` | `/api/polygons/{id}/` | Delete one owned polygon |

Polygon points are stored as normalized values between `0` and `1`, allowing the frontend canvas to resize without moving annotations away from their intended image regions.

Example request:

```json
{
  "label": "Product",
  "color": "#FF8A00",
  "points": [
    {"x": 0.12, "y": 0.18},
    {"x": 0.74, "y": 0.20},
    {"x": 0.58, "y": 0.82}
  ]
}
```

Validation rules:

- At least three distinct points
- Maximum 200 points per polygon
- Every coordinate must be between `0` and `1`
- Colors must use six-digit hexadecimal format
- Images and polygons are available only to their owning user

## Tests

Run the current backend suite:

```bash
python manage.py test apps.accounts apps.tasks apps.annotations
```

The current suite covers authentication, task CRUD and reordering, image validation, multiple uploads, polygon validation and persistence, user isolation, and protected deletion.

## Development workflow

The project is developed through focused branches and pull requests. Broader integration tests and deployment documentation are added in later focused branches.

## License

Licensed under the MIT License.
