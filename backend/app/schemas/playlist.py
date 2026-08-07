from pydantic import BaseModel


class PlaylistResponse(BaseModel):
    spotify_playlist_id: str
    spotify_playlist_url: str
    playlist_track_ids: list[str]
