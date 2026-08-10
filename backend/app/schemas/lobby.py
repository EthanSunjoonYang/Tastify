from uuid import UUID

from pydantic import BaseModel


class LobbyParticipant(BaseModel):
    id: UUID
    display_name: str | None


class LobbyResponse(BaseModel):
    host: LobbyParticipant
    guest: LobbyParticipant | None
