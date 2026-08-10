from datetime import UTC, datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

from fastapi.testclient import TestClient
from spotipy.exceptions import SpotifyException
from sqlalchemy.orm import Session

import app.api.routes.auth as auth_route
from app.db import get_db
from app.main import app
from app.models.user import User
from app.services.crypto import decrypt_token


def _override_get_db(session: Session):
    def _get_db():
        yield session

    return _get_db


def test_login_redirects_to_spotify_authorize_url(client: TestClient):
    response = client.get("/api/auth/login", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"].startswith("https://accounts.spotify.com/authorize")


def test_callback_with_error_param_returns_400(client: TestClient):
    response = client.get("/api/auth/callback", params={"error": "access_denied"})

    assert response.status_code == 400


def test_callback_missing_code_returns_400(client: TestClient):
    response = client.get("/api/auth/callback")

    assert response.status_code == 400


def test_callback_creates_new_user(db_session: Session, monkeypatch):
    spotify_id = f"spotify-{uuid4()}"
    mock_oauth = Mock()
    mock_oauth.get_access_token.return_value = {
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
        "expires_in": 3600,
    }
    monkeypatch.setattr(auth_route, "get_spotify_oauth", lambda: mock_oauth)
    monkeypatch.setattr(
        auth_route,
        "get_current_profile",
        lambda token: {
            "id": spotify_id,
            "display_name": "New Person",
            "images": [{"url": "https://img/large.jpg"}, {"url": "https://img/small.jpg"}],
        },
    )

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    try:
        response = TestClient(app).get(
            "/api/auth/callback", params={"code": "auth-code"}, follow_redirects=False
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 307
    user = db_session.query(User).filter(User.spotify_id == spotify_id).one()
    try:
        assert user.display_name == "New Person"
        assert user.profile_image_url == "https://img/small.jpg"
        assert decrypt_token(user.access_token) == "new-access-token"
        assert decrypt_token(user.refresh_token) == "new-refresh-token"
        assert f"/auth/success?user_id={user.id}" in response.headers["location"]
    finally:
        db_session.delete(user)
        db_session.commit()


def test_callback_updates_existing_user_without_duplicating(db_session: Session, monkeypatch):
    spotify_id = f"spotify-{uuid4()}"
    existing = User(
        spotify_id=spotify_id,
        display_name="Old Name",
        access_token="unused",
        refresh_token="unused",
        token_expires_at=datetime.now(UTC) - timedelta(days=1),
    )
    db_session.add(existing)
    db_session.commit()
    db_session.refresh(existing)
    existing_id = existing.id

    mock_oauth = Mock()
    mock_oauth.get_access_token.return_value = {
        "access_token": "refreshed-access-token",
        "refresh_token": "refreshed-refresh-token",
        "expires_in": 3600,
    }
    monkeypatch.setattr(auth_route, "get_spotify_oauth", lambda: mock_oauth)
    monkeypatch.setattr(
        auth_route,
        "get_current_profile",
        lambda token: {"id": spotify_id, "display_name": "Updated Name"},
    )

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    try:
        TestClient(app).get(
            "/api/auth/callback", params={"code": "auth-code"}, follow_redirects=False
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    try:
        matching = db_session.query(User).filter(User.spotify_id == spotify_id).all()
        assert len(matching) == 1
        assert matching[0].id == existing_id
        assert matching[0].display_name == "Updated Name"
        assert decrypt_token(matching[0].access_token) == "refreshed-access-token"
    finally:
        db_session.query(User).filter(User.spotify_id == spotify_id).delete()
        db_session.commit()


def test_callback_spotify_api_failure_returns_502(db_session: Session, monkeypatch):
    mock_oauth = Mock()
    mock_oauth.get_access_token.side_effect = SpotifyException(500, -1, "boom")
    monkeypatch.setattr(auth_route, "get_spotify_oauth", lambda: mock_oauth)

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    try:
        response = TestClient(app).get("/api/auth/callback", params={"code": "auth-code"})
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 502
