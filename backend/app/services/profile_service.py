from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.taste_profile import TasteProfile
from app.models.user import User
from app.services import profile_builder
from app.services.spotify_client import (
    fetch_audio_features,
    fetch_top_artists_by_range,
    fetch_top_tracks_by_range,
    get_client,
)
from app.services.spotify_data import ensure_valid_access_token

STALE_AFTER = timedelta(hours=24)


def get_or_build_profile(db: Session, user: User) -> TasteProfile:
    existing = db.query(TasteProfile).filter(TasteProfile.user_id == user.id).one_or_none()
    if existing and existing.computed_at > datetime.now(UTC) - STALE_AFTER:
        return existing

    access_token = ensure_valid_access_token(db, user)
    sp = get_client(access_token)

    top_artists_by_range = fetch_top_artists_by_range(sp)
    top_tracks_by_range = fetch_top_tracks_by_range(sp)

    artist_weights = profile_builder.compute_artist_weights(top_artists_by_range)
    genre_vector = profile_builder.compute_genre_vector(top_artists_by_range, artist_weights)
    top_track_ids = profile_builder.compute_top_track_pool(top_tracks_by_range)

    audio_features = fetch_audio_features(sp, top_track_ids)
    audio_profile = profile_builder.compute_audio_profile(audio_features)

    if existing is None:
        existing = TasteProfile(user_id=user.id)
        db.add(existing)

    existing.genre_vector = genre_vector
    existing.audio_profile = audio_profile
    existing.top_artist_ids = artist_weights
    existing.top_track_ids = top_track_ids
    existing.computed_at = datetime.now(UTC)
    db.commit()
    db.refresh(existing)
    return existing
