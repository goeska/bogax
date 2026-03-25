# BogaX

Stack: **Django** (REST API + JWT), **Vue 3** (Vite), **PostgreSQL**.

## Backup & restore

Full steps for backing up this project, PostgreSQL, and Cursor/OS-level editor settings (format machine, new laptop, OS upgrade): see **[docs/BACKUP_RESTORE.md](docs/BACKUP_RESTORE.md)**.

## Prerequisites

- Python 3.12+ (`.venv` is already used in this project)
- Node.js 20+ and npm
- Local PostgreSQL with database `bogax` and credentials matching `backend/.env`

## Run Backend

```bash
cd backend
source ../.venv/bin/activate
python manage.py runserver 8000
```

- API: `http://127.0.0.1:8000/api/`
- Django Admin: `http://127.0.0.1:8000/admin/`  
  Example superuser (created during setup): `admin@bogax.local` / `adminbogax123`.  
  Change it in admin, or create another one with `createsuperuser`.

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to `http://127.0.0.1:8000`.

## Database Configuration

This app uses PostgreSQL database **`bogax`** only.  
Any other `DB_NAME` value will fail startup by design.

Variables in `backend/.env` (default local setup):

- `DB_HOST=localhost`
- `DB_USER=goeska`
- `DB_PASSWORD=1`
- `DB_NAME=bogax`

For production, set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, and `CORS_ALLOWED_ORIGINS`.
