from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TasteProfileResponse(BaseModel):
    user_id: UUID
    genre_vector: dict[str, float]
    audio_profile: dict[str, float]
    top_artist_ids: dict[str, float]
    top_track_ids: list[str]
    computed_at: datetime
