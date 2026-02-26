## Flask backend (architecture scaffold)

### Structure

```
backend/
  app/
    __init__.py              # create_app() factory
    extensions.py            # db, migrate singletons
    core/                    # config, logging
    api/v1/                  # versioned API blueprint
    models/                  # SQLAlchemy models
    repositories/            # database access layer
    services/                # business logic layer
    schemas/                 # request/response validation + serialization
  run.py                     # local dev entrypoint
  requirements.txt
  .env.example
```

### Quickstart (local)

From `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

### Example endpoints

- `GET /api/v1/health`
- `GET /api/v1/users?limit=50&offset=0`
- `POST /api/v1/users` with JSON:

```json
{ "email": "test@example.com" }
```

### Database (SQLite by default)

This scaffold uses Flask-Migrate/Alembic. Once you’re ready:

```bash
flask --app run db init
flask --app run db migrate -m "init"
flask --app run db upgrade
```
