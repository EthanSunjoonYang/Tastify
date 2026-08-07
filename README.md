# Spotify Taste Comparator

Spotify Blend tells you the number. This tells you the story.

Two users authenticate with Spotify; the backend pulls their listening data, computes
compatibility via cosine similarity (genres), Jaccard index (artists), and inverted Euclidean
distance (audio features), and surfaces a full analytical breakdown — genre-by-genre comparison,
an audio feature radar chart, shared/unique artists, taste gaps, and a cohesion-scored shared
playlist exported back to Spotify.

## Stack

- **Backend:** FastAPI, SQLAlchemy, Alembic, Spotipy, scikit-learn
- **Frontend:** React + TypeScript, Recharts, Tailwind
- **Infra:** Docker Compose (local), GitHub Actions CI, pytest, Ruff

## Local development

1. Register a Spotify app at https://developer.spotify.com/dashboard (redirect URI:
   `http://127.0.0.1:8000/api/auth/callback` -- Spotify rejects `localhost` as insecure).
2. Copy `backend/.env.example` to `backend/.env` and fill in `SPOTIFY_CLIENT_ID`,
   `SPOTIFY_CLIENT_SECRET`, and `TOKEN_ENCRYPTION_KEY` (generate with
   `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`).
3. `docker compose up --build`
4. API: http://localhost:8000/api/health · Frontend: http://localhost:5173
5. To test login, visit http://127.0.0.1:8000/api/auth/login (must be `127.0.0.1`, matching the
   registered redirect URI -- `localhost` will fail Spotify's redirect_uri check).

## Tests

```bash
cd backend
pip install -r requirements.txt
pytest --cov=app --cov-report=term-missing
ruff check .
```

## Project structure

See `backend/app/` for the service layout (`api/routes`, `services`, `models`, `schemas`) and
`backend/tests/` for the test suite. `backend/alembic/` holds database migrations.
