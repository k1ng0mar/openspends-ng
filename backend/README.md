# OpenSpends NG — Backend (FastAPI)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DATABASE_URL, MAPBOX_TOKEN, etc.

# Run migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload --port 8000
```

## Environment Variables
See `.env.example` for full list.

## API Docs
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
