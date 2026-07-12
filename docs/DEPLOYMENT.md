# Free-Tier PythonAnywhere Deployment

This guide deploys the Django backend as a traditional WSGI web app on PythonAnywhere. Replace every placeholder before running a command.

## 1. Prepare the repository

Before deployment, confirm that `main` contains:

```text
manage.py
requirements.txt
config/wsgi.py
apps/
```

Also confirm that GitHub does not contain `.env`, `db.sqlite3`, `media/`, or `staticfiles/`.

## 2. Clone from GitHub

Open a PythonAnywhere **Bash console**:

```bash
cd ~
git clone https://github.com/<github-username>/markflow-backend.git
cd markflow-backend
```

For a public repository, HTTPS cloning does not require a repository secret.

## 3. Create the virtual environment

Use the same Python version for the virtual environment and the web app:

```bash
mkvirtualenv --python=/usr/bin/python3.11 markflow-backend
pip install --upgrade pip
pip install -r requirements.txt
```

Later console sessions can reactivate it with:

```bash
workon markflow-backend
```

## 4. Generate a production secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Save the result privately. Do not add it to GitHub.

## 5. Set console environment variables

These variables are needed when running migrations and management commands in the current Bash session:

```bash
export DJANGO_SECRET_KEY='<generated-secret>'
export DJANGO_DEBUG='False'
export DJANGO_ALLOWED_HOSTS='<pythonanywhere-username>.pythonanywhere.com'
export CORS_ALLOWED_ORIGINS='https://<frontend-project>.vercel.app'
export CSRF_TRUSTED_ORIGINS='https://<frontend-project>.vercel.app'
```

Origins must include `https://` and must not include a trailing slash.

## 6. Prepare Django

```bash
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_demo
```

Run the test suite before making the app public:

```bash
python manage.py test apps.accounts apps.tasks apps.annotations
```

## 7. Create the web app

In the PythonAnywhere **Web** tab:

1. Select **Add a new web app**.
2. Choose **Manual configuration**.
3. Choose Python **3.11**, matching the virtual environment.
4. In the **Virtualenv** field, enter:

```text
/home/<pythonanywhere-username>/.virtualenvs/markflow-backend
```

## 8. Configure the WSGI file

Open the WSGI configuration file linked from the Web tab and replace its contents with the following. This file belongs to the PythonAnywhere deployment and is not the same as the repository's `config/wsgi.py`.

```python
import os
import sys

project_home = "/home/<pythonanywhere-username>/markflow-backend"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
os.environ["DJANGO_SECRET_KEY"] = "<generated-secret>"
os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_ALLOWED_HOSTS"] = "<pythonanywhere-username>.pythonanywhere.com"
os.environ["CORS_ALLOWED_ORIGINS"] = "https://<frontend-project>.vercel.app"
os.environ["CSRF_TRUSTED_ORIGINS"] = "https://<frontend-project>.vercel.app"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

Never publish the real contents of this server-side WSGI file.

## 9. Configure static and media mappings

In the Web tab, add:

| URL | Directory |
|---|---|
| `/static/` | `/home/<pythonanywhere-username>/markflow-backend/staticfiles` |
| `/media/` | `/home/<pythonanywhere-username>/markflow-backend/media` |

The media mapping is required so the frontend can display uploaded images.

## 10. Reload and verify

Select **Reload** in the Web tab, then visit:

```text
https://<pythonanywhere-username>.pythonanywhere.com/api/health/
```

Expected response:

```json
{
  "status": "ok",
  "service": "markflow-backend"
}
```

Test login with:

```text
Email: demo@markflow.app
Password: MarkFlow123!
```

## 11. Connect the frontend

Set the frontend environment variable on Vercel:

```text
NEXT_PUBLIC_API_URL=https://<pythonanywhere-username>.pythonanywhere.com
```

Do not add a trailing slash unless the frontend API helper explicitly expects one.

If the frontend URL changes, update both of these backend values in the PythonAnywhere WSGI file and reload:

```text
CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS
```

## 12. Deploy future backend updates

Open a Bash console:

```bash
workon markflow-backend
cd ~/markflow-backend
git pull origin main
pip install -r requirements.txt
```

Set the console environment variables again, then run:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check
```

Reload the web app from the Web tab.

## 13. Free-tier operational notes

- The deployment uses one SQLite file and local uploaded media.
- Keep the repository's 5 MB per-file and 20-images-per-user limits.
- Back up `db.sqlite3` and `media/` before destructive changes.
- Free account limits and renewal requirements can change; review the current account dashboard before submission.
- Keep the demo active through the review period and verify it immediately before submitting links.

## Troubleshooting

### `DisallowedHost`

Make sure `DJANGO_ALLOWED_HOSTS` contains only the hostname:

```text
<username>.pythonanywhere.com
```

Do not include `https://` there.

### Browser CORS error

Use the exact deployed frontend origin with scheme and no trailing slash:

```text
https://<project>.vercel.app
```

Reload the backend after changing the WSGI file.

### `ModuleNotFoundError: config`

Confirm the WSGI `project_home` points to the directory containing `manage.py`, and that it is inserted into `sys.path` before Django loads.

### Admin CSS is missing

Run:

```bash
python manage.py collectstatic --noinput
```

Then confirm the `/static/` mapping and reload.

### Uploaded images return 404

Confirm the `/media/` mapping points to the exact `media` directory and that files exist there.

### Database says a table does not exist

Activate the virtual environment, set the console environment variables, and run:

```bash
python manage.py migrate
```

### A deployment works in the console but not on the website

The web worker uses values defined in the PythonAnywhere WSGI configuration. Console `export` commands do not automatically configure the web worker.
