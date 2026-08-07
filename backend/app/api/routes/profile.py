from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.profile import TasteProfileResponse
from app.services.profile_service import get_or_build_profile

router = APIRouter()


@router.get("/profile/me", response_model=TasteProfileResponse)
def get_my_profile(user_id: UUID, db: Session = Depends(get_db)) -> TasteProfileResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    profile = get_or_build_profile(db, user)
    return TasteProfileResponse(
        user_id=profile.user_id,
        era_vector=profile.era_vector,
        top_artist_ids=profile.top_artist_ids,
        artist_names=profile.artist_names,
        artist_images=profile.artist_images,
        top_track_ids=profile.top_track_ids,
        computed_at=profile.computed_at,
    )
