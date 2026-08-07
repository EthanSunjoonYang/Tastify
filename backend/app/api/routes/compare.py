from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.comparison import ComparisonResponse
from app.services.comparison_service import get_or_build_comparison

router = APIRouter()


@router.get("/compare/{other_user_id}", response_model=ComparisonResponse)
def compare_users(
    other_user_id: UUID, user_id: UUID, db: Session = Depends(get_db)
) -> ComparisonResponse:
    user_a = db.get(User, user_id)
    user_b = db.get(User, other_user_id)
    if user_a is None or user_b is None:
        raise HTTPException(status_code=404, detail="User not found")

    comparison = get_or_build_comparison(db, user_a, user_b)
    return ComparisonResponse(
        user_a_id=comparison.user_a_id,
        user_a_display_name=user_a.display_name,
        user_b_id=comparison.user_b_id,
        user_b_display_name=user_b.display_name,
        overall_score=comparison.overall_score,
        era_score=comparison.era_score,
        artist_score=comparison.artist_score,
        shared_artists=comparison.shared_artists,
        taste_gaps=comparison.taste_gaps,
        era_breakdown=comparison.era_breakdown,
        computed_at=comparison.computed_at,
    )
