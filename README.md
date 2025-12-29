# WorldServer

Minimal Django API implementing the TinyBox Worlds database contract.

## Setup

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
```

## Running

```bash
./.venv/Scripts/python.exe manage.py runserver 0.0.0.0:8000
```

## API

- `GET /` — list worlds.
- `GET /?id=X` — download TBW for world X; increments download count.
- `GET /?report=X` — report world X; increments report count.
- `POST /` — upload world. JSON body `{name, tbw, featured?, version?, author?, image?}`.
- `PUT/PATCH /?id=X` — update world fields.
- `DELETE /?id=X` — delete world.
