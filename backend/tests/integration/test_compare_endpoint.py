from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.services.comparison_service as comparison_service
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


def test_compare_users_builds_and_returns_comparison(db_session: Session, monkeypatch):
    user_a = _make_user(db_session, "A")
    user_b = _make_user(db_session, "B")

    profiles = {
        user_a.id: SimpleNamespace(
            era_vector={"2010s": 1.0},
            top_artist_ids={"a1": 1.0, "a2": 0.5},
            artist_names={"a1": "Shared Artist", "a2": "Only A"},
        ),
        user_b.id: SimpleNamespace(
            era_vector={"2010s": 0.5, "2020s": 0.5},
            top_artist_ids={"a1": 0.8, "a3": 0.4},
            artist_names={"a1": "Shared Artist", "a3": "Only B"},
        ),
    }
    monkeypatch.setattr(
        comparison_service, "get_or_build_profile", lambda db, user: profiles[user.id]
    )
    user_a_id, user_b_id = user_a.id, user_b.id

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    try:
        response = TestClient(app).get(
            f"/api/compare/{user_b_id}", params={"user_id": str(user_a_id)}
        )
    finally:
        app.dependency_overrides.pop(get_db, None)
        db_session.query(Comparison).filter(
            Comparison.user_a_id == user_a_id, Comparison.user_b_id == user_b_id
        ).delete()
        db_session.query(User).filter(User.id.in_([user_a_id, user_b_id])).delete(
            synchronize_session=False
        )
        db_session.commit()

    assert response.status_code == 200
    body = response.json()
    assert body["user_a_id"] == str(user_a_id)
    assert body["user_b_id"] == str(user_b_id)
    # shared {a1}, union {a1, a2, a3} -> 1/3
    assert body["artist_score"] == pytest.approx(1 / 3)
    assert body["shared_artists"] == [
        {
            "artist_id": "a1",
            "name": "Shared Artist",
            "weight_a": 1.0,
            "weight_b": 0.8,
            "combined_weight": pytest.approx(1.8),
        }
    ]
    assert body["taste_gaps"]["artists_only_in_a"] == [
        {"artist_id": "a2", "name": "Only A", "weight": 0.5}
    ]
    assert body["taste_gaps"]["artists_only_in_b"] == [
        {"artist_id": "a3", "name": "Only B", "weight": 0.4}
    ]
    assert body["taste_gaps"]["eras_only_in_b"] == ["2020s"]


def test_compare_users_returns_404_for_unknown_user(client: TestClient, db_session: Session):
    user = _make_user(db_session, "Solo")
    try:
        response = client.get(f"/api/compare/{uuid4()}", params={"user_id": str(user.id)})
    finally:
        db_session.query(User).filter(User.id == user.id).delete()
        db_session.commit()

    assert response.status_code == 404
