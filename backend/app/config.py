from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/spotify_comparator"

    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    # Spotify's dashboard rejects "localhost" as insecure; only HTTPS or the
    # literal loopback IP 127.0.0.1 are accepted for redirect URIs.
    spotify_redirect_uri: str = "http://127.0.0.1:8000/api/auth/callback"

    token_encryption_key: str = ""

    frontend_url: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
