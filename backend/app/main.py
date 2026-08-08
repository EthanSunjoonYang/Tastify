from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOauthError

from app.api.routes import auth, compare, health, playlist, profile
from app.config import get_settings

app = FastAPI(title="Spotify Taste Comparator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(compare.router, prefix="/api")
app.include_router(playlist.router, prefix="/api")


@app.exception_handler(SpotifyOauthError)
def handle_spotify_oauth_error(request: Request, exc: SpotifyOauthError) -> JSONResponse:
    # Raised when a refresh token has been revoked or expired -- the user
    # needs to log in again, not something a retry can fix.
    return JSONResponse(
        status_code=401,
        content={"detail": "Your Spotify session has expired. Please log in again."},
    )


@app.exception_handler(SpotifyException)
def handle_spotify_exception(request: Request, exc: SpotifyException) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={"detail": "Spotify API error. Please try again in a moment."},
    )
