# Stock Sentiment Analyzer

Real-time stock sentiment analysis platform: scrapes Reddit discussion (r/wallstreetbets, r/stocks,
r/investing, r/stockmarket), scores ticker mentions with VADER sentiment, computes rolling weighted
sentiment trends, and surfaces it through a React dashboard with price overlay.

## Stack

- **Backend:** FastAPI, SQLAlchemy, Alembic, Celery + Redis, PRAW, VADER, yfinance
- **Frontend:** React + TypeScript, Recharts, Tailwind
- **Infra:** Docker Compose (local), GitHub Actions CI, pytest, Ruff

## Local development

1. Copy `backend/.env.example` to `backend/.env` and fill in Reddit API credentials
   (register an app at https://www.reddit.com/prefs/apps, type "script").
2. `docker compose up --build`
3. API: http://localhost:8000/api/health · Frontend: http://localhost:5173

## Tests

```bash
cd backend
pip install -r requirements.txt
pytest --cov=app --cov-report=term-missing
ruff check .
```

## Project structure

See `backend/app/` for the service layout (`api/routes`, `services`, `tasks`, `models`, `schemas`)
and `backend/tests/` for unit vs. integration tests.
