from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.services.playlist_service as playlist_service
from app.db import get_db
from app.main import app
from app.models.comparison import Comparison
from app.models.user import User


def _override_get_db(session: Session):
    def _get_db():
        yield session

    return _get_db


def _make_user(db_session: Session, suffix: str) -> User:
    user = User(
        spotify_id=f"spotify-{uuid4()}",
        display_name=f"Test User {suffix}",
        access_token="unused",
        refresh_token="unused",
        token_expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_generate_playlist_selects_tracks_and_stores_result(db_session: Session, monkeypatch):
    user_a = _make_user(db_session, "A")
    user_b = _make_user(db_session, "B")

    comparison = Comparison(
        user_a_id=user_a.id,
        user_b_id=user_b.id,
        overall_score=80.0,
        era_score=0.8,
        artist_score=0.8,
        shared_artists=[],
        taste_gaps={},
        era_breakdown=[],
    )
    db_session.add(comparison)
    db_session.commit()
    db_session.refresh(comparison)

    profiles = {
        user_a.id: SimpleNamespace(
            top_track_ids=["t1"],
            track_meta={
                "t1": {"name": "Shared Song", "artist_ids": ["shared"], "decade": "2010s"}
            },
            top_artist_ids={"shared": 1.0},
            era_vector={"2010s": 1.0},
        ),
        user_b.id: SimpleNamespace(
            # "filler" has no track_meta entry -- pushes t2 to rank 1, avoiding a
            # tier-1 confidence tie against user_a's rank-0 t1.
            top_track_ids=["filler", "t2"],
            track_meta={
                "t2": {"name": "Also Shared", "artist_ids": ["shared"], "decade": "2010s"}
            },
            top_artist_ids={"shared": 0.8},
            era_vector={"2010s": 1.0},
        ),
    }

    added_tracks = {}
    monkeypatch.setattr(playlist_service, "get_or_build_comparison", lambda db, a, b: comparison)
    monkeypatch.setattr(
        playlist_service, "get_or_build_profile", lambda db, user: profiles[user.id]
    )
    monkeypatch.setattr(
        playlist_service, "ensure_valid_access_token", lambda db, user: "fake-token"
    )
    monkeypatch.setattr(playlist_service, "get_client", lambda token: object())
    monkeypatch.setattr(
        playlist_service,
        "create_playlist",
        lambda sp, name, description: "playlist123",
    )

    def _fake_add_tracks(sp, playlist_id, track_ids):
        added_tracks["playlist_id"] = playlist_id
        added_tracks["track_ids"] = track_ids

    monkeypatch.setattr(playlist_service, "add_tracks_to_playlist", _fake_add_tracks)

    user_a_id, user_b_id, comparison_id = user_a.id, user_b.id, comparison.id
    app.dependency_overrides[get_db] = _override_get_db(db_session)
    try:
        response = TestClient(app).post(
            f"/api/playlist/generate/{user_b_id}", params={"user_id": str(user_a_id)}
        )
    finally:
        app.dependency_overrides.pop(get_db, None)
        db_session.query(Comparison).filter(Comparison.id == comparison_id).delete()
        db_session.query(User).filter(User.id.in_([user_a_id, user_b_id])).delete(
            synchronize_session=False
        )
        db_session.commit()

    assert response.status_code == 200
    body = response.json()
    assert body["spotify_playlist_id"] == "playlist123"
    assert body["spotify_playlist_url"] == "https://open.spotify.com/playlist/playlist123"
    assert body["playlist_track_ids"] == ["t1", "t2"]
    assert added_tracks == {"playlist_id": "playlist123", "track_ids": ["t1", "t2"]}


def test_generate_playlist_returns_404_for_unknown_user(client: TestClient, db_session: Session):
    user = _make_user(db_session, "Solo")
    try:
        response = client.post(
            f"/api/playlist/generate/{uuid4()}", params={"user_id": str(user.id)}
        )
    finally:
        db_session.query(User).filter(User.id == user.id).delete()
        db_session.commit()

    assert response.status_code == 404
