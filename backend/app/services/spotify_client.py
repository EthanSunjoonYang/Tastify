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


def create_playlist(sp: spotipy.Spotify, name: str, description: str, public: bool = False) -> str:
    # spotipy's user_playlist_create() still posts to the old users/{id}/playlists
    # path, which Spotify's Feb 2026 Web API migration turned into a hard 403 for
    # every caller (not just new apps -- verified live). POST /me/playlists is
    # the documented replacement and doesn't need the user id at all.
    #
    # Known Spotify-side bug (verified live, both on create and via a follow-up
    # PUT /playlists/{id}): the public flag is accepted and echoed back
    # correctly in the response, but not actually honored -- every playlist
    # ends up public regardless. Left as public=False here since that's the
    # correct request; nothing we can do differently until Spotify fixes it.
    payload = {
        "name": name,
        "public": public,
        "collaborative": False,
        "description": description,
    }
    playlist = sp._post("me/playlists", payload=payload)
    return playlist["id"]


def add_tracks_to_playlist(sp: spotipy.Spotify, playlist_id: str, track_ids: list[str]) -> None:
    # Same migration: playlist_add_items() posts to the old .../tracks path.
    # POST /playlists/{id}/items is the replacement (verified live).
    uris = [f"spotify:track:{track_id}" for track_id in track_ids]
    sp._post(f"playlists/{playlist_id}/items", payload={"uris": uris})
