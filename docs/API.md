# MarkFlow Backend API Reference

## Base URLs

Local development:

```text
http://127.0.0.1:8000
```

Hosted demo:

```text
https://<username>.pythonanywhere.com
```

All request and response bodies use JSON unless an image upload explicitly uses `multipart/form-data`.

## Authentication

Private endpoints require:

```http
Authorization: Bearer <access-token>
```

### Obtain access and refresh tokens

```http
POST /api/auth/token/
Content-Type: application/json
```

```json
{
  "email": "demo@markflow.app",
  "password": "MarkFlow123!"
}
```

Successful response — `200 OK`:

```json
{
  "refresh": "<refresh-token>",
  "access": "<access-token>"
}
```

Invalid credentials return `401 Unauthorized`.

### Refresh an access token

```http
POST /api/auth/token/refresh/
Content-Type: application/json
```

```json
{
  "refresh": "<refresh-token>"
}
```

Successful response — `200 OK`:

```json
{
  "access": "<new-access-token>"
}
```

### Read current user

```http
GET /api/auth/me/
Authorization: Bearer <access-token>
```

Successful response — `200 OK`:

```json
{
  "id": 1,
  "email": "demo@markflow.app",
  "first_name": "Demo",
  "last_name": "User"
}
```

### Logout

```http
POST /api/auth/logout/
Authorization: Bearer <access-token>
Content-Type: application/json
```

```json
{
  "refresh": "<refresh-token>"
}
```

Successful response — `204 No Content`. The supplied refresh token is blacklisted.

## Tasks

Status values:

```text
todo
in_progress
done
```

Priority values:

```text
low
medium
high
```

### List tasks

```http
GET /api/tasks/
Authorization: Bearer <access-token>
```

Filter one board date:

```http
GET /api/tasks/?date=2026-07-12
Authorization: Bearer <access-token>
```

The date must use `YYYY-MM-DD`.

Example response — `200 OK`:

```json
[
  {
    "id": 14,
    "title": "Design annotation toolbar",
    "description": "Prepare the first toolbar iteration.",
    "status": "todo",
    "priority": "high",
    "task_date": "2026-07-12",
    "due_date": "2026-07-13",
    "position": 0,
    "tags": [
      {
        "id": 3,
        "name": "Design",
        "color": "#FF8A00"
      }
    ],
    "created_at": "2026-07-12T10:00:00Z",
    "updated_at": "2026-07-12T10:00:00Z"
  }
]
```

### Create a task

```http
POST /api/tasks/
Authorization: Bearer <access-token>
Content-Type: application/json
```

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

`tag_names` are trimmed, deduplicated case-insensitively, and created for the current user when missing. The API assigns the next position in the selected date and status column.

Successful response — `201 Created`.

### Read, edit, or delete one task

```http
GET /api/tasks/{id}/
PATCH /api/tasks/{id}/
DELETE /api/tasks/{id}/
Authorization: Bearer <access-token>
```

Example partial update:

```json
{
  "priority": "medium",
  "tag_names": ["Frontend"]
}
```

Delete success — `204 No Content`.

A due date earlier than the task date is rejected with `400 Bad Request`.

### Reorder a task

```http
POST /api/tasks/reorder/
Authorization: Bearer <access-token>
Content-Type: application/json
```

```json
{
  "task_id": 14,
  "status": "in_progress",
  "position": 1
}
```

`position` is zero-based. Positions larger than the destination column are clamped to its end. The move and both affected columns are normalized inside one database transaction.

Successful response — `200 OK` with the moved task.

## Images

Upload limits:

- JPG, PNG, or WEBP;
- maximum 5 MB per file;
- maximum 20 stored images per user.

### List images

```http
GET /api/images/
Authorization: Bearer <access-token>
```

Example response:

```json
[
  {
    "id": 7,
    "image": "http://127.0.0.1:8000/media/uploads/user_1/abc123.png",
    "original_name": "product.png",
    "width": 1600,
    "height": 1200,
    "file_size": 482019,
    "uploaded_at": "2026-07-12T10:30:00Z",
    "updated_at": "2026-07-12T10:30:00Z",
    "polygon_count": 2
  }
]
```

### Upload one or more images

```http
POST /api/images/upload/
Authorization: Bearer <access-token>
Content-Type: multipart/form-data
```

Use the repeated field name `files`.

```bash
curl -X POST "http://127.0.0.1:8000/api/images/upload/" \
  -H "Authorization: Bearer <access-token>" \
  -F "files=@/path/first.png" \
  -F "files=@/path/second.jpg"
```

Successful response — `201 Created` with an array of created image objects.

When a batch contains valid and invalid files, valid files are saved and validation messages are returned in the `X-Upload-Warnings` response header. When none are valid, the request returns `400 Bad Request`.

### Read or delete an image

```http
GET /api/images/{id}/
DELETE /api/images/{id}/
Authorization: Bearer <access-token>
```

Deleting an image removes its database record, stored file, and related polygons. Delete success — `204 No Content`.

## Polygon annotations

Points use normalized image coordinates. `0,0` is the top-left corner and `1,1` is the bottom-right corner.

Validation:

- at least three distinct points;
- no more than 200 points;
- each `x` and `y` value is numeric and between `0` and `1`;
- label cannot be empty;
- color must be a six-digit hexadecimal value.

### List polygons for an image

```http
GET /api/images/{image_id}/polygons/
Authorization: Bearer <access-token>
```

### Create a polygon

```http
POST /api/images/{image_id}/polygons/
Authorization: Bearer <access-token>
Content-Type: application/json
```

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

Successful response — `201 Created`:

```json
{
  "id": 22,
  "image": 7,
  "label": "Product",
  "color": "#FF8A00",
  "points": [
    {"x": 0.12, "y": 0.18},
    {"x": 0.74, "y": 0.2},
    {"x": 0.58, "y": 0.82}
  ],
  "created_at": "2026-07-12T10:40:00Z",
  "updated_at": "2026-07-12T10:40:00Z"
}
```

### Read, edit, or delete a polygon

```http
GET /api/polygons/{id}/
PATCH /api/polygons/{id}/
DELETE /api/polygons/{id}/
Authorization: Bearer <access-token>
```

Example partial update:

```json
{
  "label": "Updated region",
  "color": "#22C982"
}
```

Delete success — `204 No Content`.

## Health check

```http
GET /api/health/
```

This endpoint is public and can be used by deployment checks.

```json
{
  "status": "ok",
  "service": "markflow-backend"
}
```

## Common errors

### Missing or expired access token

```json
{
  "detail": "Authentication credentials were not provided."
}
```

Status: `401 Unauthorized`.

### Resource owned by another user

The API returns `404 Not Found` rather than revealing that another user's resource exists.

### Validation errors

Django REST Framework returns field-level messages, for example:

```json
{
  "due_date": [
    "Due date cannot be before the task date."
  ]
}
```
