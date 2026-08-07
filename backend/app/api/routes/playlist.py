from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.playlist import PlaylistResponse
from app.services.playlist_service import generate_playlist

router = APIRouter()


@router.post("/playlist/generate/{other_user_id}", response_model=PlaylistResponse)
def generate_shared_playlist(
    other_user_id: UUID, user_id: UUID, db: Session = Depends(get_db)
) -> PlaylistResponse:
    user_a = db.get(User, user_id)
    user_b = db.get(User, other_user_id)
    if user_a is None or user_b is None:
        raise HTTPException(status_code=404, detail="User not found")

    comparison = generate_playlist(db, user_a, user_b)
    return PlaylistResponse(
        spotify_playlist_id=comparison.spotify_playlist_id,
        spotify_playlist_url=(
            f"https://open.spotify.com/playlist/{comparison.spotify_playlist_id}"
        ),
        playlist_track_ids=comparison.playlist_track_ids,
    )
