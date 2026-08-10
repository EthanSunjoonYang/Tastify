# Spotify Taste Comparator

Spotify Blend tells you the number. This tells you the story.

Two users create a lobby, invite each other via a share link, and hit "Create Blend." The backend
pulls their listening data, computes compatibility via cosine similarity (listening era) and
Jaccard index (artists), and surfaces a full analytical breakdown — a compatibility score ring,
era-by-era comparison, an artist-overlap donut, shared/unique artists, taste gaps, and a
cohesion-scored shared playlist exported back to Spotify.

Note: Spotify deprecated the Audio Features endpoint for all apps created after November 27,
2024 (no official replacement), and separately stopped populating genre tags on artist/album
objects platform-wide, so the original three-pillar design (genre + artist + audio "vibe") was
cut back to two pillars: era cosine similarity (release-decade distribution, replacing genre) and
artist Jaccard index, reweighted proportionally (era 8/15, artist 7/15) from the original
0.4/0.35 split.

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

## Production Docker images

`docker-compose.yml` is dev-only (hot reload, bind mounts, `frontend/Dockerfile.dev`). Each
service also has a standalone production `Dockerfile`, verified locally end-to-end (migrations
run automatically, non-root user, correct SPA routing):

**Backend** -- runs `alembic upgrade head` then starts uvicorn (no `--reload`) as a non-root user.
Needs `DATABASE_URL`, `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI`,
`TOKEN_ENCRYPTION_KEY`, `FRONTEND_URL` at runtime (same as `.env.example`, minus `DATABASE_URL`'s
local port).

```bash
cd backend
docker build -t taste-comparator-backend .
docker run -p 8000:8000 --env-file .env -e DATABASE_URL=<prod-postgres-url> taste-comparator-backend
```

**Frontend** -- multi-stage build (Vite build -> nginx serving static files with SPA fallback
routing, so client-side routes like `/lobby/<id>` don't 404 on refresh). Vite bakes env vars into
the bundle at build time, so `VITE_API_BASE_URL` must be passed as a *build arg*, not a runtime
env var:

```bash
cd frontend
docker build --build-arg VITE_API_BASE_URL=https://api.yourdomain.com -t taste-comparator-frontend .
docker run -p 80:80 taste-comparator-frontend
```

Not yet done: actual cloud provisioning (hosting, managed Postgres, DNS/TLS, CI/CD push-to-deploy).
The images above are ready to hand to any container host (ECS, Fly.io, Railway, Render, etc.) once
that's decided.
