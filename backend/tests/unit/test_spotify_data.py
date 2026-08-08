from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import app.services.spotify_data as spotify_data
from app.services.crypto import decrypt_token, encrypt_token
from app.services.spotify_data import ensure_valid_access_token


class FakeUser:
    def __init__(self, access_token: str, refresh_token: str, token_expires_at: datetime):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = token_expires_at


def test_ensure_valid_access_token_returns_cached_token_when_not_expiring_soon(monkeypatch):
    user = FakeUser(
        access_token=encrypt_token("still-valid-token"),
        refresh_token=encrypt_token("unused-refresh-token"),
        token_expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    mock_get_oauth = Mock()
    monkeypatch.setattr(spotify_data, "get_spotify_oauth", mock_get_oauth)

    token = ensure_valid_access_token(db=Mock(), user=user)

    assert token == "still-valid-token"
    mock_get_oauth.assert_not_called()


def test_ensure_valid_access_token_refreshes_when_expired(monkeypatch):
    user = FakeUser(
        access_token=encrypt_token("stale-token"),
        refresh_token=encrypt_token("my-refresh-token"),
        token_expires_at=datetime.now(UTC) - timedelta(minutes=5),
    )
    mock_oauth = Mock()
    mock_oauth.refresh_access_token.return_value = {
        "access_token": "fresh-token",
        "expires_in": 3600,
    }
    monkeypatch.setattr(spotify_data, "get_spotify_oauth", lambda: mock_oauth)
    db = Mock()

    token = ensure_valid_access_token(db, user)

    assert token == "fresh-token"
    mock_oauth.refresh_access_token.assert_called_once_with("my-refresh-token")
    assert decrypt_token(user.access_token) == "fresh-token"
    # Spotify didn't return a new refresh token, so the old one is kept.
    assert decrypt_token(user.refresh_token) == "my-refresh-token"
    assert user.token_expires_at > datetime.now(UTC) + timedelta(minutes=59)
    db.commit.assert_called_once()


def test_ensure_valid_access_token_rotates_refresh_token_if_spotify_returns_one(monkeypatch):
    user = FakeUser(
        access_token=encrypt_token("stale-token"),
        refresh_token=encrypt_token("old-refresh-token"),
        token_expires_at=datetime.now(UTC) - timedelta(minutes=5),
    )
    mock_oauth = Mock()
    mock_oauth.refresh_access_token.return_value = {
        "access_token": "fresh-token",
        "refresh_token": "rotated-refresh-token",
        "expires_in": 3600,
    }
    monkeypatch.setattr(spotify_data, "get_spotify_oauth", lambda: mock_oauth)

    ensure_valid_access_token(Mock(), user)

    assert decrypt_token(user.refresh_token) == "rotated-refresh-token"
