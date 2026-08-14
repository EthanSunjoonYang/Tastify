from uuid import UUID

from pydantic import BaseModel


class LobbyParticipant(BaseModel):
    id: UUID
    display_name: str | None
    profile_image_url: str | None


class LobbyResponse(BaseModel):
    host: LobbyParticipant
    guest: LobbyParticipant | None
    blend_ready: bool
