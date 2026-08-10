from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models.user import User
from app.services.crypto import encrypt_token
from app.services.spotify_client import get_current_profile, get_spotify_oauth

router = APIRouter()


def _smallest_image_url(images: list[dict] | None) -> str | None:
    # Spotify orders images largest-first; the smallest is plenty for an avatar.
    if not images:
        return None
    return images[-1].get("url")


@router.get("/auth/login")
def login() -> RedirectResponse:
    auth_url = get_spotify_oauth().get_authorize_url()
    return RedirectResponse(auth_url)


@router.get("/auth/callback")
def callback(code: str | None = None, error: str | None = None, db: Session = Depends(get_db)):
    if error:
        raise HTTPException(status_code=400, detail=f"Spotify authorization failed: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    token_info = get_spotify_oauth().get_access_token(code, as_dict=True, check_cache=False)
    profile = get_current_profile(token_info["access_token"])

    expires_at = datetime.now(UTC) + timedelta(seconds=token_info["expires_in"])

    user = db.query(User).filter(User.spotify_id == profile["id"]).one_or_none()
    if user is None:
        user = User(spotify_id=profile["id"])
        db.add(user)

    user.display_name = profile.get("display_name")
    user.profile_image_url = _smallest_image_url(profile.get("images"))
    user.access_token = encrypt_token(token_info["access_token"])
    user.refresh_token = encrypt_token(token_info["refresh_token"])
    user.token_expires_at = expires_at
    db.commit()
    db.refresh(user)

    frontend_url = get_settings().frontend_url
    return RedirectResponse(f"{frontend_url}/auth/success?user_id={user.id}")
