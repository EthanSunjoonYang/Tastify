from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SharedArtist(BaseModel):
    artist_id: str
    name: str
    image_url: str
    weight_a: float
    weight_b: float
    combined_weight: float


class UniqueArtist(BaseModel):
    artist_id: str
    name: str
    image_url: str
    weight: float


class TasteGaps(BaseModel):
    eras_only_in_a: list[str]
    eras_only_in_b: list[str]
    artists_only_in_a: list[UniqueArtist]
    artists_only_in_b: list[UniqueArtist]


class EraBreakdownRow(BaseModel):
    decade: str
    user_a: float
    user_b: float


class ComparisonResponse(BaseModel):
    user_a_id: UUID
    user_b_id: UUID
    overall_score: float
    era_score: float
    artist_score: float
    shared_artists: list[SharedArtist]
    taste_gaps: TasteGaps
    era_breakdown: list[EraBreakdownRow]
    computed_at: datetime
