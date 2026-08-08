import pytest

from app.services import crypto
from app.services.crypto import decrypt_token, encrypt_token


def test_encrypt_decrypt_round_trip():
    token = "some-spotify-access-token"

    encrypted = encrypt_token(token)

    assert encrypted != token
    assert decrypt_token(encrypted) == token


def test_missing_encryption_key_raises_runtime_error(monkeypatch):
    crypto._fernet.cache_clear()
    monkeypatch.setattr(
        crypto, "get_settings", lambda: type("Settings", (), {"token_encryption_key": ""})()
    )

    with pytest.raises(RuntimeError, match="TOKEN_ENCRYPTION_KEY"):
        encrypt_token("x")

    crypto._fernet.cache_clear()
