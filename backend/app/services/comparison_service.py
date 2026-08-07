from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.comparison import Comparison
from app.models.user import User
from app.services import comparison_engine
from app.services.profile_service import get_or_build_profile


def get_or_build_comparison(db: Session, user_a: User, user_b: User) -> Comparison:
    profile_a = get_or_build_profile(db, user_a)
    profile_b = get_or_build_profile(db, user_b)

    era_score = comparison_engine.compute_cosine_similarity(
        profile_a.era_vector, profile_b.era_vector
    )
    artist_score = comparison_engine.compute_jaccard_index(
        set(profile_a.top_artist_ids), set(profile_b.top_artist_ids)
    )
    overall_score = comparison_engine.compute_overall_score(era_score, artist_score)

    shared_artists = comparison_engine.compute_shared_artists(
        profile_a.top_artist_ids,
        profile_a.artist_names,
        profile_b.top_artist_ids,
        profile_b.artist_names,
    )
    era_gaps = comparison_engine.compute_era_gaps(profile_a.era_vector, profile_b.era_vector)
    taste_gaps = {
        "eras_only_in_a": era_gaps["only_in_a"],
        "eras_only_in_b": era_gaps["only_in_b"],
        "artists_only_in_a": comparison_engine.compute_unique_artists(
            profile_a.top_artist_ids, profile_a.artist_names, profile_b.top_artist_ids
        ),
        "artists_only_in_b": comparison_engine.compute_unique_artists(
            profile_b.top_artist_ids, profile_b.artist_names, profile_a.top_artist_ids
        ),
    }
    era_breakdown = comparison_engine.compute_era_breakdown(
        profile_a.era_vector, profile_b.era_vector
    )

    existing = (
        db.query(Comparison)
        .filter(Comparison.user_a_id == user_a.id, Comparison.user_b_id == user_b.id)
        .one_or_none()
    )
    if existing is None:
        existing = Comparison(user_a_id=user_a.id, user_b_id=user_b.id)
        db.add(existing)

    existing.overall_score = float(round(overall_score * 100))
    existing.era_score = era_score
    existing.artist_score = artist_score
    existing.shared_artists = shared_artists
    existing.taste_gaps = taste_gaps
    existing.era_breakdown = era_breakdown
    existing.computed_at = datetime.now(UTC)
    db.commit()
    db.refresh(existing)
    return existing
