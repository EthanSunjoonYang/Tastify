import spotipy
from spotipy.oauth2 import SpotifyOAuth

from app.config import get_settings

SCOPES = "user-top-read playlist-modify-public playlist-modify-private"


def get_spotify_oauth() -> SpotifyOAuth:
    settings = get_settings()
    return SpotifyOAuth(
        client_id=settings.spotify_client_id,
        client_secret=settings.spotify_client_secret,
        redirect_uri=settings.spotify_redirect_uri,
        scope=SCOPES,
        cache_handler=spotipy.cache_handler.MemoryCacheHandler(),
        show_dialog=True,
    )


def get_current_profile(access_token: str) -> dict:
    return spotipy.Spotify(auth=access_token).me()
