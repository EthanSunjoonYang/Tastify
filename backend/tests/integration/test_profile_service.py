from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

import app.services.profile_service as profile_service
from app.models.taste_profile import TasteProfile
from app.models.user import User
from app.services.profile_service import get_or_build_profile


def test_get_or_build_profile_returns_cached_profile_without_hitting_spotify(
    db_session: Session, monkeypatch
):
    user = User(
        spotify_id=f"spotify-{uuid4()}",
        display_name="Test User",
        access_token="unused",
        refresh_token="unused",
        token_expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    existing = TasteProfile(
        user_id=user.id,
        era_vector={"2010s": 1.0},
        top_artist_ids={"a1": 1.0},
        artist_names={"a1": "Cached Artist"},
        artist_images={"a1": "https://img/a1.jpg"},
        top_track_ids=["t1"],
        track_meta={"t1": {"name": "Cached Song", "artist_ids": ["a1"], "decade": "2010s"}},
        computed_at=datetime.now(UTC) - timedelta(hours=1),
    )
    db_session.add(existing)
    db_session.commit()
    db_session.refresh(existing)

    def _fail_if_called(*args, **kwargs):
        raise AssertionError("should not hit Spotify for a fresh cached profile")

    monkeypatch.setattr(profile_service, "ensure_valid_access_token", _fail_if_called)

    try:
        result = get_or_build_profile(db_session, user)
        assert result.id == existing.id
        assert result.artist_names == {"a1": "Cached Artist"}
    finally:
        db_session.query(TasteProfile).filter(TasteProfile.user_id == user.id).delete()
        db_session.query(User).filter(User.id == user.id).delete()
        db_session.commit()
