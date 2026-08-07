from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TasteProfileResponse(BaseModel):
    user_id: UUID
    era_vector: dict[str, float]
    top_artist_ids: dict[str, float]
    top_track_ids: list[str]
    computed_at: datetime
