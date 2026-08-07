from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.services.profile_service as profile_service
from app.db import get_db
from app.main import app
from app.models.taste_profile import TasteProfile
from app.models.user import User


def _override_get_db(session: Session):
    def _get_db():
        yield session

    return _get_db


def test_get_my_profile_builds_and_returns_profile(db_session: Session, monkeypatch):
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

    monkeypatch.setattr(
        profile_service, "ensure_valid_access_token", lambda db, user: "fake-token"
    )
    monkeypatch.setattr(profile_service, "get_client", lambda token: object())
    monkeypatch.setattr(
        profile_service,
        "fetch_top_artists_by_range",
        lambda sp: {
            "short_term": [{"id": "a1", "genres": ["indie rock"]}],
            "medium_term": [{"id": "a1", "genres": ["indie rock"]}],
            "long_term": [],
        },
    )
    monkeypatch.setattr(
        profile_service,
        "fetch_top_tracks_by_range",
        lambda sp: {
            "short_term": [{"id": "t1"}],
            "medium_term": [{"id": "t1"}],
            "long_term": [],
        },
    )
    monkeypatch.setattr(
        profile_service,
        "fetch_audio_features",
        lambda sp, track_ids: [
            {
                "id": "t1",
                "danceability": 0.8,
                "energy": 0.7,
                "valence": 0.6,
                "tempo": 120,
                "acousticness": 0.2,
            }
        ],
    )

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    try:
        response = TestClient(app).get("/api/profile/me", params={"user_id": str(user.id)})
    finally:
        app.dependency_overrides.pop(get_db, None)
        db_session.query(TasteProfile).filter(TasteProfile.user_id == user.id).delete()
        db_session.query(User).filter(User.id == user.id).delete()
        db_session.commit()

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == str(user.id)
    assert body["genre_vector"] == {"indie rock": 1.0}
    assert body["top_artist_ids"] == {"a1": 1.0}
    assert body["top_track_ids"] == ["t1"]
    assert body["audio_profile"]["danceability"] == pytest.approx(0.8)


def test_get_my_profile_returns_404_for_unknown_user(client: TestClient):
    response = client.get("/api/profile/me", params={"user_id": str(uuid4())})

    assert response.status_code == 404
