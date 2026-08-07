import spotipy
from spotipy.oauth2 import SpotifyOAuth

from app.config import get_settings

SCOPES = "user-top-read playlist-modify-public playlist-modify-private"
TIME_RANGES = ("short_term", "medium_term", "long_term")
TOP_ITEMS_LIMIT = 50
AUDIO_FEATURES_BATCH_SIZE = 100


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


def get_client(access_token: str) -> spotipy.Spotify:
    return spotipy.Spotify(auth=access_token)


def fetch_top_artists_by_range(sp: spotipy.Spotify) -> dict[str, list[dict]]:
    return {
        time_range: sp.current_user_top_artists(limit=TOP_ITEMS_LIMIT, time_range=time_range)[
            "items"
        ]
        for time_range in TIME_RANGES
    }


def fetch_top_tracks_by_range(sp: spotipy.Spotify) -> dict[str, list[dict]]:
    return {
        time_range: sp.current_user_top_tracks(limit=TOP_ITEMS_LIMIT, time_range=time_range)[
            "items"
        ]
        for time_range in TIME_RANGES
    }


def fetch_audio_features(sp: spotipy.Spotify, track_ids: list[str]) -> list[dict]:
    features = []
    for i in range(0, len(track_ids), AUDIO_FEATURES_BATCH_SIZE):
        batch = track_ids[i : i + AUDIO_FEATURES_BATCH_SIZE]
        results = sp.audio_features(tracks=batch)
        features.extend(f for f in results if f is not None)
    return features
