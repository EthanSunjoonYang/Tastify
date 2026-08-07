from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.user import User
from app.services.crypto import decrypt_token, encrypt_token
from app.services.spotify_client import get_spotify_oauth

# Refresh proactively rather than waiting for a 401, so a single profile build
# never straddles an expiry mid-request.
EXPIRY_BUFFER = timedelta(seconds=60)


def ensure_valid_access_token(db: Session, user: User) -> str:
    if user.token_expires_at > datetime.now(UTC) + EXPIRY_BUFFER:
        return decrypt_token(user.access_token)

    token_info = get_spotify_oauth().refresh_access_token(decrypt_token(user.refresh_token))

    user.access_token = encrypt_token(token_info["access_token"])
    if token_info.get("refresh_token"):
        user.refresh_token = encrypt_token(token_info["refresh_token"])
    user.token_expires_at = datetime.now(UTC) + timedelta(seconds=token_info["expires_in"])
    db.commit()

    return token_info["access_token"]
