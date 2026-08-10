from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.lobby import LobbyParticipant, LobbyResponse
from app.services.lobby_service import get_or_create_lobby, join_lobby

router = APIRouter()


def _to_participant(user: User) -> LobbyParticipant:
    return LobbyParticipant(
        id=user.id,
        display_name=user.display_name,
        profile_image_url=user.profile_image_url,
    )


def _to_response(host: User, guest: User | None) -> LobbyResponse:
    return LobbyResponse(
        host=_to_participant(host),
        guest=_to_participant(guest) if guest is not None else None,
    )


@router.get("/lobby/{host_user_id}", response_model=LobbyResponse)
def get_lobby(host_user_id: UUID, db: Session = Depends(get_db)) -> LobbyResponse:
    host = db.get(User, host_user_id)
    if host is None:
        raise HTTPException(status_code=404, detail="User not found")

    lobby = get_or_create_lobby(db, host)
    guest = db.get(User, lobby.guest_user_id) if lobby.guest_user_id else None
    return _to_response(host, guest)


@router.post("/lobby/join/{host_user_id}", response_model=LobbyResponse)
def join(host_user_id: UUID, user_id: UUID, db: Session = Depends(get_db)) -> LobbyResponse:
    host = db.get(User, host_user_id)
    guest = db.get(User, user_id)
    if host is None or guest is None:
        raise HTTPException(status_code=404, detail="User not found")
    if host.id == guest.id:
        raise HTTPException(status_code=400, detail="Cannot join your own lobby")

    lobby = join_lobby(db, host, guest)
    joined_guest = db.get(User, lobby.guest_user_id)
    return _to_response(host, joined_guest)
