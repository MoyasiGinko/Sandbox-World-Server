# WorldServer

Minimal Django API implementing the TinyBox Worlds database contract.

## Setup

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt

# create local environment file
copy .env.example .env
```

## Running

```bash
./.venv/Scripts/python.exe manage.py runserver 0.0.0.0:8000
```

## Deploy Note (SQLite)

- If your host runs release jobs on a read-only app directory, set `DJANGO_DB_PATH=/tmp/worldserver.sqlite3`.
- The app now auto-falls back to `DJANGO_DB_FALLBACK_PATH` (default `/tmp/worldserver.sqlite3`) when the configured DB file is not writable.

## Runtime Config Management

- Dynamic client-facing URLs/config are served from `GET /api/client-config`.
- Values are managed in Django Admin via `RuntimeConfig` records.
- If a key is not set in the table, the API falls back to values from `.env`.

## API

- `GET /` — list worlds.
- `GET /?id=X` — download TBW for world X; increments download count.
- `GET /?report=X` — report world X; increments report count.
- `POST /` — upload world. JSON body `{name, tbw, featured?, version?, author?, image?}`.
- `PUT/PATCH /?id=X` — update world fields.
- `DELETE /?id=X` — delete world.
