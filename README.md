# OpenSpends NG

Track Nigerian government budget allocation & spending — by arm, ministry, project, and location.

## Quick Start

### Prerequisites
- Docker + Docker Compose
- Node.js 18+ (frontend)
- Python 3.12 + (backend)

### 1. Clone & Configure
```bash
git clone https://github.com/k1ng0mar/openspends-ng.git
cd openspends-ng

# Backend env
cp backend/.env.example backend/.env
# Edit DATABASE_URL, MAPBOX_TOKEN, etc.
```

### 2. Start Database + Redis
```bash
docker compose up -d db redis
```

### 3. Seed Data
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed.py --db-url postgresql+psycopg://postgres:postgres@localhost:5432/openspends
```

### 4. Run Backend
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
# API: http://localhost:8000/docs
```

### 5. Run Frontend
```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
```

## Project Structure
```
openspends-ng/
├── backend/          # FastAPI app
│   ├── app/
│   │   ├── api/v1/  # Route handlers
│   │   ├── models/  # SQLAlchemy ORM
│   │   ├── schemas/ # Pydantic models
│   │   ├── core/    # Config, DB
│   │   └── services/ # PDF parser, scrapers
│   ├── alembic/     # DB migrations
│   └── scripts/     # Seed data
├── frontend/         # React + Vite + Tailwind
└── data/            # Sample scraped data
```

## License
MIT
