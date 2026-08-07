import spotipy
from spotipy.oauth2 import SpotifyOAuth

from app.config import get_settings

SCOPES = "user-top-read playlist-modify-public playlist-modify-private"
TIME_RANGES = ("short_term", "medium_term", "long_term")
TOP_ITEMS_LIMIT = 50


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


def create_playlist(
    sp: spotipy.Spotify, spotify_user_id: str, name: str, description: str
) -> str:
    playlist = sp.user_playlist_create(
        spotify_user_id, name, public=True, description=description
    )
    return playlist["id"]


def add_tracks_to_playlist(sp: spotipy.Spotify, playlist_id: str, track_ids: list[str]) -> None:
    uris = [f"spotify:track:{track_id}" for track_id in track_ids]
    sp.playlist_add_items(playlist_id, uris)
